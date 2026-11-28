using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Plays the 3D kid's clips (built in ArtSource/tools/characters) from the KidController's state: run, idle, jump,
    /// fall, land, double jump (a second push in the air), slide, vault, ladder climb, stumble, wade and the dive. Running and wading play
    /// faster or slower with her speed, so her feet keep pace with the ground. Swaps her face (neutral, grin, shocked,
    /// straining) with the action. Purely cosmetic: it only reads the controller.
    /// </summary>
    public sealed class KidModelVisual : MonoBehaviour
    {
        static readonly int MainTexId = Shader.PropertyToID("_MainTex");

        [SerializeField] internal KidController kid;
        [SerializeField] internal Animator animator;
        [Tooltip("The renderer and material slot that carries the face texture.")]
        [SerializeField] internal Renderer faceRenderer;
        [SerializeField] internal int faceMaterialIndex;
        [SerializeField] internal Texture2D faceNeutral;
        [SerializeField] internal Texture2D faceGrin;
        [SerializeField] internal Texture2D faceShocked;
        [SerializeField] internal Texture2D faceStraining;
        [Tooltip("The run speed the Run clip was made for, in m/s (Kick Off's on-screen pace: 2 strides a second).")]
        [SerializeField] internal float runReferenceSpeed = 3.5f;
        [SerializeField] internal float crossFade = 0.07f;
        [Tooltip("Seconds the rise eases into the fall over at the top of a jump (Kick Off's air pose blends with the " +
                 "vertical speed, from the lead knee up to the legs reaching down, rather than switching).")]
        [SerializeField] internal float fallCrossFade = 0.2f;
        [Tooltip("How far in front of the rungs the kid's body is while she climbs a ladder, in metres.")]
        [SerializeField] internal float ladderStandOff = 0.16f;
        [Tooltip("Seconds of one loop of the Climb clip, which moves each hand up one rung (two rungs a loop).")]
        [SerializeField] internal float climbClipLength = 0.4f;

        string _state;
        float _landTimer;
        float _stumbleTimer;
        float _doubleTimer;
        bool _caught;
        Texture2D _face;
        MaterialPropertyBlock _block;
        Transform _holder;              // the model's holder: turned to face the run, or the wall on a ladder
        Quaternion _runFacing;
        bool _haveFacing;

        void OnEnable()
        {
            if (kid == null) kid = GetComponentInParent<KidController>();
            if (animator == null) animator = GetComponentInChildren<Animator>();
            if (kid == null) return;
            kid.Landed += OnLanded;
            kid.DoubleJumped += OnDoubleJumped;
            kid.HitObstacle += OnHit;
        }

        void OnDisable()
        {
            if (kid == null) return;
            kid.Landed -= OnLanded;
            kid.DoubleJumped -= OnDoubleJumped;
            kid.HitObstacle -= OnHit;
        }

        void OnLanded() => _landTimer = 0.25f;
        void OnDoubleJumped() => _doubleTimer = 0.4f;
        void OnHit(Obstacle obstacle, float metres) => _stumbleTimer = 0.7f;

        static readonly int TiptoeState = Animator.StringToHash("Tiptoe");
        static readonly int LiftState = Animator.StringToHash("BasketLift");

        /// <summary>
        /// The basket intro: Tiptoe at its own pace, or BasketLift held at the lift's progress (the clip is scrubbed by the
        /// player's hold). False if the model has no such clip, so the usual states play instead.
        /// </summary>
        bool PlayIntro()
        {
            bool lift = kid.IntroPose == KidIntroPose.Lift;
            int hash = lift ? LiftState : TiptoeState;
            if (!animator.HasState(0, hash)) return false;
            if (lift)
            {
                animator.speed = 0f;
                animator.Play(hash, 0, Mathf.Clamp01(kid.IntroLift) * 0.999f);
                _state = "BasketLift";
                SetFace(faceStraining);
                return true;
            }
            animator.speed = 1f;
            if (_state != "Tiptoe")
            {
                animator.CrossFadeInFixedTime(hash, crossFade, 0, 0f);
                _state = "Tiptoe";
            }
            SetFace(faceNeutral);
            return true;
        }

        /// <summary>The kid has the rooster in her hands for a moment: grin.</summary>
        public void SetCaught(bool caught) => _caught = caught;

        void LateUpdate()
        {
            if (kid == null || animator == null) return;
            float dt = Time.deltaTime;
            _landTimer = Mathf.Max(0f, _landTimer - dt);
            _stumbleTimer = Mathf.Max(0f, _stumbleTimer - dt);
            _doubleTimer = Mathf.Max(0f, _doubleTimer - dt);

            string state;
            float speed = 1f;
            if (kid.IntroPose != KidIntroPose.None && PlayIntro()) return;
            switch (kid.Pose)
            {
                case KidPose.Dive: state = "Dive"; break;
                case KidPose.Vault: state = "Vault"; break;
                case KidPose.Climb:
                    state = "Climb";
                    // Hands and feet keep time with the rungs: a loop of the clip climbs two of them.
                    if (kid.ClimbLadder != null && kid.ClimbRate > 0f)
                        speed = kid.ClimbRate * climbClipLength / (2f * Mathf.Max(0.05f, kid.ClimbLadder.rungSpacing));
                    break;
                case KidPose.Slide: state = "Slide"; break;
                case KidPose.Air:
                    state = _doubleTimer > 0f ? "DoubleJump" : kid.VerticalSpeed > 0.5f ? "JumpUp" : "Fall";
                    break;
                default:
                    if (kid.CurrentSpeed < 0.1f) state = "Idle";
                    else if (_stumbleTimer > 0f && kid.IsStumbling) { state = "Stumble"; }
                    else if (_landTimer > 0f) { state = "Land"; }
                    else if (kid.IsWading) { state = "Wade"; speed = kid.CurrentSpeed / Mathf.Max(0.1f, runReferenceSpeed * 0.45f); }
                    else { state = "Run"; speed = kid.CurrentSpeed / Mathf.Max(0.1f, runReferenceSpeed); }
                    break;
            }
            animator.speed = Mathf.Clamp(speed, 0.3f, state == "Climb" ? 5f : 2.5f);
            FaceLadder(dt);
            if (state != _state)
            {
                animator.CrossFadeInFixedTime(state, state == "Fall" ? fallCrossFade : crossFade, 0, 0f);
                _state = state;
            }
            SetFace(FaceFor(state));
        }

        /// <summary>
        /// On a ladder the kid turns her back to the camera to face the wall and keeps just in front of the rungs as the
        /// ladder leans back; off it she turns back to face the run.
        /// </summary>
        void FaceLadder(float dt)
        {
            if (_holder == null)
            {
                _holder = animator.transform.parent != null && animator.transform.parent != kid.transform
                    ? animator.transform.parent : animator.transform;
                _runFacing = _holder.localRotation;
                _haveFacing = true;
            }
            if (!_haveFacing) return;
            var ladder = kid.Pose == KidPose.Climb ? kid.ClimbLadder : null;
            Quaternion facing = ladder != null ? Quaternion.identity : _runFacing;   // the model's own front is +Z
            float z = ladder != null ? ladder.At(kid.Position.y).z - ladderStandOff - kid.transform.position.z : 0f;
            float follow = 1f - Mathf.Exp(-dt * 22f);
            _holder.localRotation = Quaternion.Slerp(_holder.localRotation, facing, follow);
            var p = _holder.localPosition;
            _holder.localPosition = new Vector3(p.x, p.y, Mathf.Lerp(p.z, z, follow));
        }

        Texture2D FaceFor(string state)
        {
            if (_caught) return faceGrin;
            switch (state)
            {
                case "JumpUp":
                case "DoubleJump":
                case "Slide": return faceGrin;
                case "Fall":
                case "Stumble": return faceShocked;
                case "Vault":
                case "Climb":
                case "Dive":
                case "Wade": return faceStraining;
                default: return faceNeutral;
            }
        }

        void SetFace(Texture2D face)
        {
            if (face == null || face == _face || faceRenderer == null) return;
            _face = face;
            _block ??= new MaterialPropertyBlock();
            faceRenderer.GetPropertyBlock(_block, faceMaterialIndex);
            _block.SetTexture(MainTexId, face);
            faceRenderer.SetPropertyBlock(_block, faceMaterialIndex);
        }
    }
}
