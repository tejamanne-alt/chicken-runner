using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Plays the 3D kid's clips (built in ArtSource/tools/characters) from the KidController's state: run, idle, jump,
    /// fall, land, double-jump somersault, slide, vault, ladder climb, stumble, wade and the dive. Running and wading play
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
        [Tooltip("The run speed the Run clip was made for, in m/s.")]
        [SerializeField] internal float runReferenceSpeed = 6f;
        [SerializeField] internal float crossFade = 0.07f;

        string _state;
        float _landTimer;
        float _stumbleTimer;
        float _doubleTimer;
        bool _caught;
        Texture2D _face;
        MaterialPropertyBlock _block;

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
            switch (kid.Pose)
            {
                case KidPose.Dive: state = "Dive"; break;
                case KidPose.Vault: state = "Vault"; break;
                case KidPose.Climb: state = "Climb"; break;
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
            animator.speed = Mathf.Clamp(speed, 0.3f, 2.5f);
            if (state != _state)
            {
                animator.CrossFadeInFixedTime(state, crossFade, 0, 0f);
                _state = state;
            }
            SetFace(FaceFor(state));
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
