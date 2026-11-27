using System;
using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    public enum KidPose
    {
        Run,
        Air,
        Slide,
        Vault,
        Dive,
        /// <summary>Going up a bamboo ladder onto a roof.</summary>
        Climb,
    }

    /// <summary>
    /// The kid's kinematic motor: auto-run along +X, gravity and jumps from the zone tuning, raycasts against
    /// the chunk colliders. No rigidbody physics, and it is stepped at a fixed rate by GameFlow,
    /// so a jump is the same height and length on every device.
    ///
    /// Solid (non-trigger) colliders are ground, platforms and walls; a wall with a <see cref="Ladder"/> is climbed
    /// quickly instead of vaulted. Trigger colliders are obstacles, pickups, bouncers (cots, awnings, a buffalo's back)
    /// and canal water, recognised by their components.
    /// </summary>
    /// <summary>What the level 1 opening shows the kid doing before the chase (her visual plays the matching clip).</summary>
    public enum KidIntroPose
    {
        None,
        /// <summary>Sneaking past the sleeping neighbour to the basket.</summary>
        Tiptoe,
        /// <summary>Lifting the basket's rim: <see cref="KidController.IntroLift"/> scrubs the BasketLift clip.</summary>
        Lift,
    }

    public sealed class KidController : MonoBehaviour
    {
        const int MaxOverlaps = 16;
        const float Skin = 0.02f;
        const float FallbackGroundY = 0f;
        const float GroundRayInset = 0.7f;

        [Header("Body, metres")]
        [SerializeField] internal float radius = 0.175f;
        [SerializeField] internal float standHeight = 1.05f;
        [SerializeField] internal float slideHeight = 0.525f;
        [Tooltip("Ledges up to this height are stepped onto without a vault.")]
        [SerializeField] internal float stepHeight = 0.3f;

        [Header("Dive grab")]
        [SerializeField] internal float diveDuration = 0.5f;
        [SerializeField] internal float diveLength = 1.3f;
        [SerializeField] internal float diveHeight = 0.35f;

        readonly Collider[] _overlaps = new Collider[MaxOverlaps];
        ChaseTuning _t;
        KidSpeedModel _speed;

        Vector2 _position;
        Vector2 _previousPosition;
        float _verticalSpeed;
        float _verticalStep;
        bool _grounded;
        float _timeSinceGrounded;
        bool _jumpedSinceGrounded;
        bool _doubleJumpUsed;
        bool _groundJumpRising;
        bool _jumpCut;
        bool _jumpHeld;
        float _jumpBufferTimer;
        bool _slideRequested;
        bool _slideQueued;
        float _slideTimer;
        float _graceTimer;
        bool _stopping;

        float _vaultTimer;
        float _vaultDuration;
        Vector2 _vaultFrom;
        Vector2 _vaultTo;
        Collider _wallCollider;
        // Share of a ladder climb spent going up the rungs; the rest is stepping off onto the top.
        const float ClimbRiseShare = 0.8f;

        bool _inWater;
        bool _wasInWater;

        float _diveTimer;
        Vector2 _diveFrom;
        float _diveGroundY;

        public KidPose Pose { get; private set; }
        /// <summary>Set by <see cref="GameFlow"/> during the basket intro; None in the chase.</summary>
        public KidIntroPose IntroPose { get; set; }
        /// <summary>The basket lift, 0 to 1, while <see cref="IntroPose"/> is Lift.</summary>
        public float IntroLift { get; set; }
        public float X => _position.x;
        public Vector2 Position => _position;
        public float VerticalSpeed => _verticalSpeed;
        public bool IsGrounded => _grounded;
        public float CurrentSpeed { get; private set; }
        public float BaseSpeed => _t != null ? _t.kidRunSpeed : 0f;
        public bool IsStumbling => _speed != null && _speed.IsPenalised;
        public bool IsBoosted => _speed != null && _speed.IsBoosted;
        public float Height => Pose == KidPose.Slide ? slideHeight : standHeight;
        /// <summary>On the bed of a canal, slowed to wading pace.</summary>
        public bool IsWading => _inWater && _grounded;
        /// <summary>The ladder being climbed rung by rung, or null.</summary>
        public Ladder ClimbLadder { get; private set; }
        /// <summary>How fast the kid is going up the ladder's rungs, in m/s (0 while stepping off at the top).</summary>
        public float ClimbRate { get; private set; }

        /// <summary>The kid ran into an armed obstacle; the float is the metres the mistake costs.</summary>
        public event Action<Obstacle, float> HitObstacle;
        public event Action<Pickup> Collected;
        public event Action Jumped;
        public event Action DoubleJumped;
        public event Action Landed;
        public event Action Bounced;
        public event Action Vaulted;
        public event Action Climbed;
        public event Action SlideStarted;
        /// <summary>Splashed down into a canal.</summary>
        public event Action EnteredWater;

        public void Init(ChaseTuning tuning)
        {
            _t = tuning ?? throw new ArgumentNullException(nameof(tuning));
            _speed = new KidSpeedModel(tuning);
        }

        /// <summary>Stands the kid still at course position <paramref name="x"/>. Chunks there must already be spawned.</summary>
        public void ResetTo(float x)
        {
            float groundY = CastGround(x, 3f, 6f, out float y) ? y : FallbackGroundY;
            _position = _previousPosition = new Vector2(x, groundY);
            _verticalSpeed = 0f;
            _verticalStep = 0f;
            _grounded = true;
            _timeSinceGrounded = 0f;
            _jumpedSinceGrounded = false;
            _doubleJumpUsed = false;
            _groundJumpRising = false;
            _jumpCut = false;
            _jumpHeld = false;
            _jumpBufferTimer = 0f;
            _slideRequested = false;
            _slideQueued = false;
            _slideTimer = 0f;
            _graceTimer = 0f;
            _stopping = false;
            _inWater = false;
            _wasInWater = false;
            _wallCollider = null;
            ClimbLadder = null;
            ClimbRate = 0f;
            _speed?.Reset();
            CurrentSpeed = 0f;
            Pose = KidPose.Run;
            ApplyVisual(1f);
        }

        public void PressJump() => _jumpBufferTimer = _t.jumpBuffer;
        public void SetJumpHeld(bool held) => _jumpHeld = held;
        public void PressSlide() => _slideRequested = true;

        /// <summary>The rooster escaped: run out of steam and stop.</summary>
        public void BeginStop() => _stopping = true;

        /// <summary>The automatic dive inside grab distance.</summary>
        public void BeginDive()
        {
            Pose = KidPose.Dive;
            _diveTimer = 0f;
            _diveFrom = _position;
            float probeTop = _position.y + _t.maxVaultHeight + 0.5f;
            _diveGroundY = CastGround(_position.x + diveLength, probeTop, probeTop + 10f, out float y) ? y : _position.y;
        }

        public void Tick(float dt)
        {
            _previousPosition = _position;
            _graceTimer = Mathf.Max(0f, _graceTimer - dt);
            _speed.Tick(dt);

            if (Pose == KidPose.Dive)
            {
                TickDive(dt);
                return;
            }
            if (Pose == KidPose.Vault || Pose == KidPose.Climb)
            {
                // Input keeps its normal 0.1 s buffer during the climb; slides are not possible mid-vault.
                _jumpBufferTimer = Mathf.Max(0f, _jumpBufferTimer - dt);
                _slideRequested = false;
                TickVault(dt);
                TouchTriggers(pickupsOnly: true);
                return;
            }

            CurrentSpeed = _stopping ? Mathf.MoveTowards(CurrentSpeed, 0f, 12f * dt)
                : _speed.Speed * (IsWading ? _t.wadeSpeedFactor : 1f);

            HandleJumpInput(dt);
            HandleSlideInput(dt);
            ApplyGravity(dt);

            float dx = CurrentSpeed * dt;
            if (ProbeWall(dx, out float wallX, out float topY))
            {
                float rise = topY - _position.y;
                if (rise <= stepHeight)
                {
                    // Pop up onto a low ledge (or one met just below its top while falling) and far enough onto it
                    // that the front ground ray lands on it.
                    _position.y = topY;
                    _verticalSpeed = Mathf.Max(0f, _verticalSpeed);
                    _verticalStep = 0f;
                    _position.x = Mathf.Max(_position.x + dx, wallX - radius * GroundRayInset + Skin);
                    dx = 0f;
                }
                else if (rise <= _t.maxVaultHeight)
                {
                    StartVault(wallX, topY);
                    return;
                }
                else
                {
                    dx = Mathf.Max(0f, wallX - (_position.x + radius) - Skin);
                }
            }

            _position.x += dx;
            _position.y += _verticalStep;
            UpdateGround();
            TouchTriggers(pickupsOnly: false);

            _timeSinceGrounded = _grounded ? 0f : _timeSinceGrounded + dt;
            if (Pose != KidPose.Slide || !_grounded) Pose = _grounded ? KidPose.Run : KidPose.Air;

            if (_position.y < -10f) ResetTo(_position.x); // fell out of the course: put the kid back rather than lose them
        }

        /// <summary>Moves the transform between the last two simulation steps, so motion is smooth at any frame rate.</summary>
        public void ApplyVisual(float alpha)
        {
            var p = Vector2.Lerp(_previousPosition, _position, Mathf.Clamp01(alpha));
            transform.position = new Vector3(p.x, p.y, 0f);
        }

        void HandleJumpInput(float dt)
        {
            if (_jumpBufferTimer <= 0f) return;

            bool canGroundJump = _grounded || (_timeSinceGrounded <= _t.coyoteTime && !_jumpedSinceGrounded);
            if (canGroundJump) GroundJump();
            else if (!_doubleJumpUsed) DoubleJump();
            else _jumpBufferTimer -= dt; // keep it buffered so a tap just before landing still jumps
        }

        void GroundJump()
        {
            _verticalSpeed = JumpMath.JumpVelocity(_t);
            _grounded = false;
            _jumpedSinceGrounded = true;
            _groundJumpRising = true;
            _jumpCut = false;
            _jumpBufferTimer = 0f;
            _slideQueued = false;
            if (Pose == KidPose.Slide) Pose = KidPose.Air;
            Jumped?.Invoke();
        }

        void DoubleJump()
        {
            _verticalSpeed = JumpMath.DoubleJumpVelocity(_t);
            _doubleJumpUsed = true;
            _groundJumpRising = false;
            _jumpBufferTimer = 0f;
            _slideQueued = false;
            DoubleJumped?.Invoke();
        }

        void HandleSlideInput(float dt)
        {
            if (_slideRequested)
            {
                _slideRequested = false;
                if (_grounded)
                {
                    StartSlide();
                }
                else
                {
                    // In the air a swipe down is a fast drop, and the slide starts on landing.
                    _verticalSpeed = Mathf.Min(_verticalSpeed, -_t.fastDropSpeed);
                    _groundJumpRising = false;
                    _slideQueued = true;
                }
            }

            if (Pose == KidPose.Slide)
            {
                _slideTimer -= dt;
                if (_slideTimer <= 0f) Pose = KidPose.Run;
            }
        }

        void StartSlide()
        {
            Pose = KidPose.Slide;
            _slideTimer = _t.slideDuration;
            _slideQueued = false;
            SlideStarted?.Invoke();
        }

        /// <summary>Updates vertical speed and works out this tick's vertical move, exactly for constant gravity.</summary>
        void ApplyGravity(float dt)
        {
            float startSpeed = _verticalSpeed;
            if (_grounded)
            {
                _verticalStep = startSpeed * dt;
                return;
            }
            float gravity = JumpMath.Gravity(_t);
            if (_verticalSpeed > 0f && _groundJumpRising)
            {
                // Letting go early cuts the jump short: tap for a low hop, hold for the full height.
                if (!_jumpHeld) _jumpCut = true;
                if (_jumpCut) gravity *= JumpMath.LowJumpGravityMultiplier(_t);
            }
            else if (_verticalSpeed < 0f)
            {
                gravity *= _t.fallGravityMultiplier;
            }
            _verticalSpeed = Mathf.Max(_verticalSpeed - gravity * dt, -_t.maxFallSpeed);
            // Averaging the start and end speeds makes jump heights match the tuning at any tick rate.
            _verticalStep = (startSpeed + _verticalSpeed) * 0.5f * dt;
            if (_verticalSpeed <= 0f) _groundJumpRising = false;
        }

        void UpdateGround()
        {
            if (_verticalSpeed > 0f)
            {
                _grounded = false;
                return;
            }

            // While running, stick to the ground over small steps down; while falling, only catch what we fell through.
            float snap = _grounded ? stepHeight : 0f;
            bool hit = CastGround(_position.x, _position.y + stepHeight, stepHeight + snap + Skin, out float groundY);
            if (hit)
            {
                bool wasAirborne = !_grounded;
                _position.y = groundY;
                _verticalSpeed = 0f;
                _grounded = true;
                _jumpedSinceGrounded = false;
                _doubleJumpUsed = false;
                _groundJumpRising = false;
                _jumpCut = false;
                if (wasAirborne)
                {
                    Landed?.Invoke();
                    if (_slideQueued) StartSlide();
                }
            }
            else
            {
                _grounded = false;
            }
        }

        /// <summary>Highest solid surface under the kid's feet, from two rays at the front and back of the capsule.</summary>
        bool CastGround(float x, float originY, float distance, out float groundY)
        {
            groundY = float.NegativeInfinity;
            bool found = false;
            float inset = radius * GroundRayInset;
            for (int i = 0; i < 2; i++)
            {
                var origin = new Vector3(x + (i == 0 ? inset : -inset), originY, 0f);
                if (Physics.Raycast(origin, Vector3.down, out var hit, distance, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore)
                    && hit.point.y > groundY)
                {
                    groundY = hit.point.y;
                    found = true;
                }
            }
            return found;
        }

        /// <summary>Looks for a wall face within this step's movement; returns its X and the height of its top.</summary>
        bool ProbeWall(float dx, out float wallX, out float topY)
        {
            wallX = float.PositiveInfinity;
            topY = float.PositiveInfinity;
            _wallCollider = null;
            // The lowest ray sits just above the feet, so a ledge met while falling is still seen as a wall
            // (and stepped onto if it is low enough) rather than fallen into.
            float bottom = _position.y + Skin;
            float top = _position.y + Height - 0.05f;
            float originX = _position.x + radius - Skin;
            float distance = dx + Skin * 2f;
            float lowestHitHeight = float.PositiveInfinity;

            for (int i = 0; i < 3; i++)
            {
                float y = Mathf.Lerp(bottom, top, i / 2f);
                if (Physics.Raycast(new Vector3(originX, y, 0f), Vector3.right, out var hit, distance, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore)
                    && hit.normal.x < -0.5f && hit.point.x < wallX)
                {
                    wallX = hit.point.x;
                    _wallCollider = hit.collider;
                    lowestHitHeight = Mathf.Min(lowestHitHeight, y);
                }
            }
            if (float.IsPositiveInfinity(wallX)) return false;

            float probeTop = _position.y + _t.maxVaultHeight + 0.5f;
            if (Physics.Raycast(new Vector3(wallX + 0.05f, probeTop, 0f), Vector3.down, out var down, probeTop - _position.y, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore)
                && down.point.y >= lowestHitHeight)
            {
                topY = down.point.y;
            }
            // Otherwise the wall is taller than a vault (the ray started inside it), so topY stays infinite: blocked.
            return true;
        }

        /// <summary>Over a wall too high to step onto: a slow vault, or a quick climb if the wall has a ladder.</summary>
        void StartVault(float wallX, float topY)
        {
            var rungs = _wallCollider != null ? _wallCollider.GetComponentInParent<Ladder>() : null;
            bool ladder = rungs != null;
            Pose = ladder ? KidPose.Climb : KidPose.Vault;
            _vaultTimer = 0f;
            _vaultDuration = Mathf.Max(0.01f, ladder ? _t.ladderClimbDuration : _t.vaultDuration);
            _vaultFrom = _position;
            float speedFactor = ladder ? _t.ladderSpeedFactor : _t.vaultSpeedFactor;
            float creep = _t.kidRunSpeed * speedFactor * _vaultDuration;
            _vaultTo = new Vector2(Mathf.Max(_position.x + creep, wallX + radius + 0.05f), topY);
            ClimbLadder = rungs != null && rungs.Upright ? rungs : null;
            ClimbRate = 0f;
            // Up the rungs and off the top onto the roof, a short step past the ladder's head.
            if (ClimbLadder != null) _vaultTo = new Vector2(Mathf.Max(wallX + radius + 0.05f, ClimbLadder.Head.x + 0.3f), topY);
            _verticalSpeed = 0f;
            _grounded = false;
            _slideQueued = false;
            CurrentSpeed = (_vaultTo.x - _vaultFrom.x) / _vaultDuration;
            if (ladder) Climbed?.Invoke();
            else Vaulted?.Invoke();
        }

        void TickVault(float dt)
        {
            _vaultTimer += dt;
            float k = Mathf.Clamp01(_vaultTimer / Mathf.Max(0.01f, _vaultDuration));
            if (ClimbLadder != null) TickClimb(k);
            else
            {
                float up = 1f - (1f - k) * (1f - k);
                _position = new Vector2(Mathf.Lerp(_vaultFrom.x, _vaultTo.x, k * k), Mathf.Lerp(_vaultFrom.y, _vaultTo.y, up));
            }
            if (k < 1f) return;

            ClimbLadder = null;
            ClimbRate = 0f;
            Pose = KidPose.Run;
            _grounded = true;
            _jumpedSinceGrounded = false;
            _doubleJumpUsed = false;
            _timeSinceGrounded = 0f;
        }

        /// <summary>
        /// Up a ladder: across to it in the first moments, straight up its rungs at a steady rate (following its lean),
        /// then a step off onto the top. k runs 0 to 1 over the climb.
        /// </summary>
        void TickClimb(float k)
        {
            var ladder = ClimbLadder;
            if (k < ClimbRiseShare)
            {
                float rise = k / ClimbRiseShare;
                float y = Mathf.Lerp(_vaultFrom.y, _vaultTo.y, rise);
                float across = Mathf.SmoothStep(0f, 1f, Mathf.Clamp01(rise / 0.15f));
                _position = new Vector2(Mathf.Lerp(_vaultFrom.x, ladder.At(y).x, across), y);
                ClimbRate = (_vaultTo.y - _vaultFrom.y) / Mathf.Max(0.01f, _vaultDuration * ClimbRiseShare);
            }
            else
            {
                float off = Mathf.SmoothStep(0f, 1f, (k - ClimbRiseShare) / (1f - ClimbRiseShare));
                _position = new Vector2(Mathf.Lerp(ladder.At(_vaultTo.y).x, _vaultTo.x, off), _vaultTo.y);
                ClimbRate = 0f;
            }
        }

        void TickDive(float dt)
        {
            _diveTimer += dt;
            float k = Mathf.Clamp01(_diveTimer / Mathf.Max(0.01f, diveDuration));
            float x = _diveFrom.x + diveLength * (1f - (1f - k) * (1f - k));
            float y = Mathf.Lerp(_diveFrom.y, _diveGroundY, k) + diveHeight * Mathf.Sin(Mathf.PI * k);
            _position = new Vector2(x, y);
            CurrentSpeed = k < 1f ? diveLength / diveDuration : 0f;
        }

        void TouchTriggers(bool pickupsOnly)
        {
            float height = Height;
            var bottom = new Vector3(_position.x, _position.y + radius, 0f);
            var top = new Vector3(_position.x, _position.y + Mathf.Max(radius, height - radius), 0f);
            int count = Physics.OverlapCapsuleNonAlloc(bottom, top, radius, _overlaps, Physics.AllLayers, QueryTriggerInteraction.Collide);
            if (!pickupsOnly) _inWater = false;

            for (int i = 0; i < count; i++)
            {
                var other = _overlaps[i];
                if (other == null || !other.isTrigger) continue;

                var pickup = other.GetComponentInParent<Pickup>();
                if (pickup != null)
                {
                    if (!pickup.Collected) Collect(pickup);
                    continue;
                }
                if (pickupsOnly) continue;

                var bouncer = other.GetComponentInParent<Bouncer>();
                if (bouncer != null)
                {
                    TryBounce(bouncer);
                    continue;
                }

                if (other.GetComponentInParent<WaterZone>() != null)
                {
                    _inWater = true;
                    continue;
                }

                var obstacle = other.GetComponentInParent<Obstacle>();
                if (obstacle != null && obstacle.IsArmed && _graceTimer <= 0f) HitObstacleNow(obstacle);
            }

            if (pickupsOnly) return;
            // A jump over a canal can brush the water's trigger; only standing in it is a splash.
            if (IsWading && !_wasInWater) EnteredWater?.Invoke();
            _wasInWater = IsWading;
        }

        void Collect(Pickup pickup)
        {
            pickup.Collect();
            if (pickup.Kind == PickupKind.Chilli) _speed.StartBoost();
            Collected?.Invoke(pickup);
        }

        void TryBounce(Bouncer bouncer)
        {
            // Bounce when landing on the cot or running into it, not while already flying up past it,
            // and not once the chase is over (a kid stopped on a cot would bounce for ever).
            if (_stopping || _verticalSpeed > 0.5f || _position.y > bouncer.TopY + 0.2f) return;
            _verticalSpeed = JumpMath.BounceVelocity(_t, bouncer.BounceHeight);
            _grounded = false;
            _jumpedSinceGrounded = true;
            _doubleJumpUsed = false;
            _groundJumpRising = false;
            _jumpCut = false;
            _slideQueued = false;
            Pose = KidPose.Air;
            bouncer.Bounce();
            Bounced?.Invoke();
        }

        void HitObstacleNow(Obstacle obstacle)
        {
            float scale = obstacle.Definition != null ? obstacle.Definition.DurationScale : 1f;
            float duration = _t.stumbleDuration * scale;
            _speed.ApplyPenalty(_t.stumbleSpeedFactor, duration);
            _graceTimer = _t.hitGracePeriod;
            obstacle.Hit();
            HitObstacle?.Invoke(obstacle, KidSpeedModel.DistanceLost(_t.kidRunSpeed, _t.stumbleSpeedFactor, duration));
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.cyan;
            var p = Application.isPlaying ? new Vector3(_position.x, _position.y, 0f) : transform.position;
            float h = Application.isPlaying ? Height : standHeight;
            Gizmos.DrawWireSphere(p + Vector3.up * radius, radius);
            Gizmos.DrawWireSphere(p + Vector3.up * Mathf.Max(radius, h - radius), radius);
        }
    }
}
