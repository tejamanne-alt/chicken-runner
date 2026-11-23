using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// The kid drawn from her painted poses (ArtSource/cutouts/kid): two running frames swapped by distance run, so her
    /// feet keep pace with the ground at any speed, then jump, fall, landing crouch, slide, vault, stumble and dive.
    /// Squash and stretch and a lean are added on <see cref="body"/>, the card's parent, whose pivot is at her feet.
    /// Purely cosmetic: it only reads the KidController.
    /// </summary>
    public sealed class KidCardVisual : MonoBehaviour
    {
        [SerializeField] internal KidController kid;
        [SerializeField] internal Transform body;
        [SerializeField] internal CardFlipbook card;

        [Header("Poses")]
        [SerializeField] internal Texture2D idle;
        [SerializeField] internal Texture2D runContact;
        [SerializeField] internal Texture2D runPassing;
        [SerializeField] internal Texture2D jumpUp;
        [SerializeField] internal Texture2D fall;
        [SerializeField] internal Texture2D land;
        [SerializeField] internal Texture2D slide;
        [SerializeField] internal Texture2D vault;
        [SerializeField] internal Texture2D stumble;
        [SerializeField] internal Texture2D dive;

        [Header("Timing")]
        [Tooltip("Metres run per running frame: two frames make one stride.")]
        [SerializeField, Min(0.1f)] internal float frameDistance = 0.55f;
        [SerializeField, Min(0f)] internal float landHold = 0.12f;
        [SerializeField] internal Color boostTint = new Color(1f, 0.78f, 0.62f);

        float _distance;
        float _lastX;
        float _landTimer;
        float _squash;
        float _squashVelocity;
        float _lean;
        float _wobble;

        void OnEnable()
        {
            if (kid == null) kid = GetComponentInParent<KidController>();
            if (kid == null) return;
            kid.Jumped += OnJumped;
            kid.DoubleJumped += OnJumped;
            kid.Bounced += OnBounced;
            kid.Landed += OnLanded;
            kid.HitObstacle += OnHit;
            _lastX = kid.transform.position.x;
        }

        void OnDisable()
        {
            if (kid == null) return;
            kid.Jumped -= OnJumped;
            kid.DoubleJumped -= OnJumped;
            kid.Bounced -= OnBounced;
            kid.Landed -= OnLanded;
            kid.HitObstacle -= OnHit;
        }

        void OnJumped()
        {
            _squash = -0.18f;
            Debris.Burst(kid.transform.position, new Color(0.75f, 0.55f, 0.35f), 3, 1.2f, 0.06f);
        }

        void OnBounced() => _squash = -0.3f;

        void OnLanded()
        {
            _squash = 0.2f;
            _landTimer = landHold;
            Debris.Burst(kid.transform.position, new Color(0.75f, 0.55f, 0.35f), 4, 1.5f, 0.06f);
        }

        void OnHit(Obstacle obstacle, float metres) => _wobble = 1f;

        void LateUpdate()
        {
            if (kid == null || card == null) return;
            float dt = Time.deltaTime;
            float x = kid.transform.position.x;
            float dx = x - _lastX;
            _lastX = x;
            if (dx > 0f && dx < 2f) _distance += dx; // a reset or retry jumps back: ignore it

            _landTimer = Mathf.Max(0f, _landTimer - dt);
            _wobble = Mathf.Max(0f, _wobble - dt * 1.6f);

            float targetLean = 0f;
            Texture2D frame;
            switch (kid.Pose)
            {
                case KidPose.Slide:
                    frame = slide;
                    break;
                case KidPose.Vault:
                    frame = vault;
                    break;
                case KidPose.Climb:
                    frame = jumpUp;
                    targetLean = 8f;
                    break;
                case KidPose.Dive:
                    frame = dive;
                    break;
                case KidPose.Air:
                    frame = kid.VerticalSpeed > 0.5f ? jumpUp : fall;
                    targetLean = Mathf.Clamp(-kid.VerticalSpeed * 0.8f, -8f, 8f);
                    break;
                default:
                    if (kid.CurrentSpeed < 0.1f) frame = idle != null ? idle : runContact;
                    else if (kid.IsStumbling) frame = stumble;
                    else if (_landTimer > 0f) frame = land;
                    else frame = (int)(_distance / frameDistance) % 2 == 0 ? runContact : runPassing;
                    break;
            }
            card.Show(frame != null ? frame : runContact);
            card.SetTint(kid.IsBoosted ? Color.Lerp(Color.white, boostTint, 0.5f + 0.5f * Mathf.Sin(Time.time * 18f)) : Color.white);

            if (body == null) return;
            // A damped spring back to rest: negative stretches up (take-off), positive squashes (landing).
            _squash = Mathf.SmoothDamp(_squash, 0f, ref _squashVelocity, 0.08f, Mathf.Infinity, dt);
            float sy = 1f - _squash;
            float sx = 1f / Mathf.Sqrt(Mathf.Max(0.3f, sy));
            body.localScale = new Vector3(sx, sy, 1f);
            targetLean += Mathf.Sin(_wobble * 30f) * 14f * _wobble;
            _lean = Mathf.Lerp(_lean, targetLean, 1f - Mathf.Exp(-16f * dt));
            body.localRotation = Quaternion.Euler(0f, 0f, -_lean);
        }
    }
}
