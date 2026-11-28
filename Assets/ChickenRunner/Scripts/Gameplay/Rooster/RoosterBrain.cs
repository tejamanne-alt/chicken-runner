using System;
using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    public enum RoosterAct
    {
        /// <summary>Before the chase: pecking about.</summary>
        Idle,
        Chase,
        /// <summary>Slipping out of the dive at the end of a level.</summary>
        Wriggle,
        /// <summary>Running off after escaping or wriggling free.</summary>
        Flee,
        /// <summary>Out from under the lifted basket, sprinting to his head start (level 1's opening).</summary>
        Burst,
    }

    /// <summary>
    /// Moves the rooster along the course. His speed comes from <see cref="RoosterMind"/> (driven by the gap);
    /// his path comes from the RoosterHop markers authored in each chunk, so his route is predictable
    /// and his timing is not. Also triggers the mischief spots he runs past.
    /// </summary>
    public sealed class RoosterBrain : MonoBehaviour
    {
        const float WriggleGravity = 16f;
        const float HopEntryWindow = 0.5f;

        [SerializeField] internal float groundFollowSpeed = 8f;
        [SerializeField] internal float wriggleUpSpeed = 7.5f;
        [SerializeField] internal float wriggleForwardSpeed = 3.5f;   // out of her grasp and away, as fast as she runs
        [SerializeField] internal float fleeSpeedMultiplier = 1.5f;

        ChaseTuning _t;
        RoosterMind _mind;
        Vector2 _position;
        Vector2 _previousPosition;
        float _verticalSpeed;
        RoosterHop _hop;
        float _hopStartY;
        float _hopEndY;

        public RoosterAct Act { get; private set; }
        public RoosterMood Mood => _mind != null ? _mind.Mood : RoosterMood.Running;
        public float X => _position.x;
        public Vector2 Position => _position;
        public float Speed { get; private set; }
        public bool IsAirborne => _hop != null || Act == RoosterAct.Wriggle;
        public int PanicBursts => _mind != null ? _mind.PanicBursts : 0;
        public int Taunts => _mind != null ? _mind.Taunts : 0;

        public event Action Taunted;
        public event Action Panicked;
        public event Action CausedMischief;
        public event Action Wriggled;

        public void Init(ChaseTuning tuning)
        {
            _t = tuning ?? throw new ArgumentNullException(nameof(tuning));
            _mind = new RoosterMind(tuning);
        }

        public void ResetTo(float x)
        {
            _mind.Reset();
            _position = _previousPosition = new Vector2(x, GroundAt(x));
            _verticalSpeed = 0f;
            _hop = null;
            Speed = 0f;
            Act = RoosterAct.Idle;
            ApplyVisual(1f);
        }

        public void StartChase()
        {
            Act = RoosterAct.Chase;
            WorldBarks.Show("BAWK!", _position + Vector2.up * 1f, new Color(0.85f, 0.2f, 0.1f));
            Debris.Feathers(new Vector3(_position.x, _position.y + 0.4f, 0f), new Color(0.9f, 0.45f, 0.15f), 6);
        }

        float _burstFrom;
        float _burstTo;
        float _burstTime;
        float _burstDuration;
        float _burstEndSpeed;

        /// <summary>Seconds since the burst began (his visual shows the startled leap first).</summary>
        public float BurstTime => _burstTime;
        /// <summary>The startled beat on the spot before the burst's sprint, seconds.</summary>
        public const float BurstBeat = 0.25f;

        /// <summary>He bursts out from under the basket and sprints to <paramref name="toX"/> over <paramref name="duration"/> s.</summary>
        public void BeginBurst(float toX, float duration, float endSpeed)
        {
            Act = RoosterAct.Burst;
            _hop = null;
            _burstFrom = _position.x;
            _burstTo = toX;
            _burstTime = 0f;
            _burstDuration = Mathf.Max(BurstBeat + 0.1f, duration);
            _burstEndSpeed = Mathf.Max(0f, endSpeed);
            WorldBarks.Show("BAWK!", _position + Vector2.up * 1f, new Color(0.85f, 0.2f, 0.1f));
            Debris.Feathers(new Vector3(_position.x, _position.y + 0.4f, 0f), new Color(0.9f, 0.45f, 0.15f), 10);
        }

        void TickBurst(float dt)
        {
            _burstTime += dt;
            // A beat on the spot (the startled leap), then a sprint from a standing start that eases down into his
            // running speed as it arrives, so the chase picks up without a jolt: a cubic with no speed at the start and
            // endSpeed at the end (its end slope s1, in units of the distance over the sprint's time, is kept under 3
            // so he never runs back).
            float sprint = _burstDuration - BurstBeat;
            float k = Mathf.Clamp01((_burstTime - BurstBeat) / sprint);
            float distance = _burstTo - _burstFrom;
            float s1 = Mathf.Abs(distance) > 1e-3f ? Mathf.Clamp(_burstEndSpeed * sprint / Mathf.Abs(distance), 0f, 2.9f) : 0f;
            float eased = (s1 - 2f) * k * k * k + (3f - s1) * k * k;
            float x = _burstFrom + distance * eased;
            Speed = (x - _position.x) / Mathf.Max(dt, 1e-4f);
            _position.x = x;
            _position.y = GroundAt(x);
        }

        /// <summary>The kid's dive reached him: he pops out of the kid's hands and runs off.</summary>
        public void BeginWriggle()
        {
            Act = RoosterAct.Wriggle;
            _hop = null;
            _verticalSpeed = wriggleUpSpeed;
            WorldBarks.Show("BAWK BAWK!", _position + Vector2.up * 1.2f, new Color(0.85f, 0.2f, 0.1f));
            Debris.Feathers(new Vector3(_position.x, _position.y + 0.4f, 0f), new Color(0.9f, 0.45f, 0.15f), 14);
            Wriggled?.Invoke();
        }

        /// <summary>He got away: a victory crow and a sprint off screen.</summary>
        public void BeginFlee()
        {
            Act = RoosterAct.Flee;
            WorldBarks.Show("COCK-A-DOODLE-DOO!", _position + Vector2.up * 1.2f, new Color(0.85f, 0.2f, 0.1f), 1.6f);
        }

        public void Tick(float dt, float gap, float kidX)
        {
            _previousPosition = _position;
            switch (Act)
            {
                case RoosterAct.Chase:
                    TickChase(dt, gap, kidX);
                    break;
                case RoosterAct.Wriggle:
                    TickWriggle(dt);
                    break;
                case RoosterAct.Burst:
                    TickBurst(dt);
                    break;
                case RoosterAct.Flee:
                    Speed = _t.roosterRunSpeed * fleeSpeedMultiplier;
                    _position.x += Speed * dt;
                    FollowRoute(dt);
                    break;
            }
        }

        public void ApplyVisual(float alpha)
        {
            var p = Vector2.Lerp(_previousPosition, _position, Mathf.Clamp01(alpha));
            transform.position = new Vector3(p.x, p.y, 0f);
        }

        void TickChase(float dt, float gap, float kidX)
        {
            Speed = _mind.Tick(dt, gap, canStartTaunt: _hop == null);
            if (_mind.MoodChangedThisTick) AnnounceMood();

            float fromX = _position.x;
            _position.x += Speed * dt;
            FollowRoute(dt);

            var spots = MischiefSpot.Active;
            for (int i = 0; i < spots.Count; i++)
            {
                var spot = spots[i];
                if (spot.X > fromX && spot.X <= _position.x && spot.TryTrigger(kidX, _t.mischiefMinKidDistance))
                {
                    WorldBarks.Show("CLATTER!", new Vector3(spot.X + 1f, 1f, 0f), new Color(0.75f, 0.35f, 0.2f));
                    CausedMischief?.Invoke();
                }
            }
        }

        void AnnounceMood()
        {
            var head = new Vector3(_position.x, _position.y + 1.1f, 0f);
            switch (_mind.Mood)
            {
                case RoosterMood.Taunting:
                    WorldBarks.Show("cock-a-doodle-doo~", head, new Color(0.85f, 0.2f, 0.1f), 1.4f);
                    Taunted?.Invoke();
                    break;
                case RoosterMood.Panicking:
                    WorldBarks.Show("SQUAWK!", head, new Color(0.85f, 0.2f, 0.1f));
                    Debris.Feathers(new Vector3(_position.x, _position.y + 0.4f, 0f), new Color(0.9f, 0.45f, 0.15f), 10);
                    Panicked?.Invoke();
                    break;
            }
        }

        void TickWriggle(float dt)
        {
            Speed = wriggleForwardSpeed;
            _position.x += wriggleForwardSpeed * dt;
            _verticalSpeed -= WriggleGravity * dt;
            _position.y += _verticalSpeed * dt;
            float ground = GroundAt(_position.x);
            if (_verticalSpeed < 0f && _position.y <= ground)
            {
                _position.y = ground;
                _verticalSpeed = 0f;
                Act = RoosterAct.Flee;
            }
        }

        /// <summary>Arcs over authored hops; otherwise runs on the highest solid surface.</summary>
        void FollowRoute(float dt)
        {
            if (_hop != null && _position.x >= _hop.EndX) _hop = null;
            if (_hop == null)
            {
                // Only start a hop at its beginning; landing inside one (after the wriggle) must not snap him up.
                _hop = RoosterHop.Find(_position.x);
                if (_hop != null && _position.x - _hop.StartX > HopEntryWindow) _hop = null;
                if (_hop != null)
                {
                    _hopStartY = _position.y;
                    _hopEndY = GroundAt(_hop.EndX + 0.05f);
                }
            }

            if (_hop != null)
            {
                _position.y = Mathf.Lerp(_hopStartY, _hopEndY, _hop.Progress(_position.x)) + _hop.HeightAt(_position.x);
                return;
            }

            float ground = GroundAt(_position.x);
            _position.y = ground > _position.y ? ground : Mathf.MoveTowards(_position.y, ground, groundFollowSpeed * dt);
        }

        static float GroundAt(float x)
        {
            return Physics.Raycast(new Vector3(x, 20f, 0f), Vector3.down, out var hit, 40f, Physics.DefaultRaycastLayers, QueryTriggerInteraction.Ignore)
                ? hit.point.y
                : 0f;
        }
    }
}
