using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Grey-box animation for the capsule kid: squash and stretch, run bob, slide, vault lean, stumble wobble,
    /// dive and a chilli tint. Purely cosmetic; the supplied model and its Animator replace it in milestone 2.
    /// The body transform's pivot should be at the feet.
    /// </summary>
    public sealed class KidVisual : MonoBehaviour
    {
        [SerializeField] internal KidController kid;
        [SerializeField] internal Transform body;
        [SerializeField] internal GreyboxColor kit;
        [SerializeField] internal Color kitColor = new Color(0.15f, 0.45f, 0.85f);
        [SerializeField] internal Color boostColor = new Color(0.95f, 0.25f, 0.1f);

        float _squash;
        float _squashVelocity;
        float _wobbleTimer;
        float _runPhase;
        float _lean;
        bool _tinted;

        void OnEnable()
        {
            if (kid == null) kid = GetComponentInParent<KidController>();
            if (kid == null) return;
            kid.Jumped += OnJumped;
            kid.DoubleJumped += OnJumped;
            kid.Bounced += OnBounced;
            kid.Landed += OnLanded;
            kid.HitObstacle += OnHit;
            kid.SlideStarted += OnSlide;
        }

        void OnDisable()
        {
            if (kid == null) return;
            kid.Jumped -= OnJumped;
            kid.DoubleJumped -= OnJumped;
            kid.Bounced -= OnBounced;
            kid.Landed -= OnLanded;
            kid.HitObstacle -= OnHit;
            kid.SlideStarted -= OnSlide;
        }

        void OnJumped()
        {
            _squash = -0.25f;
            Debris.Burst(kid.transform.position, new Color(0.75f, 0.55f, 0.35f), 3, 1.2f, 0.06f);
        }

        void OnBounced() => _squash = -0.4f;

        void OnLanded()
        {
            _squash = 0.3f;
            Debris.Burst(kid.transform.position, new Color(0.75f, 0.55f, 0.35f), 4, 1.5f, 0.06f);
        }

        void OnHit(Obstacle obstacle, float metresLost) => _wobbleTimer = 0.7f;

        void OnSlide() => Debris.Burst(kid.transform.position, new Color(0.75f, 0.55f, 0.35f), 5, 2f, 0.07f);

        void LateUpdate()
        {
            if (kid == null || body == null) return;
            float dt = Time.deltaTime;

            // A critically damped spring back to rest for squash and stretch.
            _squash = Mathf.SmoothDamp(_squash, 0f, ref _squashVelocity, 0.08f);
            _wobbleTimer = Mathf.Max(0f, _wobbleTimer - dt);
            _runPhase += kid.CurrentSpeed * dt * 2.2f;

            float scaleY = 1f - _squash;
            float scaleXZ = 1f + _squash * 0.5f;
            float bob = 0f;
            float targetLean = 0f;

            switch (kid.Pose)
            {
                case KidPose.Run:
                    bob = kid.CurrentSpeed > 0.1f ? Mathf.Abs(Mathf.Sin(_runPhase)) * 0.06f : Mathf.Sin(Time.time * 3f) * 0.01f;
                    targetLean = kid.CurrentSpeed > 0.1f ? -8f : 0f;
                    break;
                case KidPose.Air:
                    targetLean = Mathf.Clamp(-kid.VerticalSpeed * 1.5f, -15f, 15f);
                    break;
                case KidPose.Slide:
                    scaleY *= 0.5f;
                    scaleXZ *= 1.2f;
                    targetLean = 20f;
                    break;
                case KidPose.Vault:
                case KidPose.Climb:
                    targetLean = -35f;
                    break;
                case KidPose.Dive:
                    targetLean = -80f;
                    break;
            }

            if (_wobbleTimer > 0f) targetLean += Mathf.Sin(_wobbleTimer * 40f) * 25f * _wobbleTimer;
            _lean = Mathf.Lerp(_lean, targetLean, 1f - Mathf.Exp(-18f * dt));

            body.localPosition = new Vector3(0f, bob, 0f);
            body.localScale = new Vector3(scaleXZ, scaleY, scaleXZ);
            // Facing +X, so a negative Z rotation leans the kid forward.
            body.localRotation = Quaternion.Euler(0f, 0f, _lean);

            bool boosted = kid.IsBoosted;
            if (kit != null && boosted != _tinted)
            {
                _tinted = boosted;
                kit.SetColor(boosted ? boostColor : kitColor);
            }
        }
    }
}
