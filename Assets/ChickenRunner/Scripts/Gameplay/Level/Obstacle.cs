using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// A hazard in the lane. Its trigger colliders are what the kid touches; the definition says what a hit costs
    /// and how the obstacle reacts. Each obstacle can only hurt the kid once.
    /// </summary>
    public sealed class Obstacle : MonoBehaviour, IChunkPart
    {
        const float RevealDuration = 0.35f;
        const float ReactionDuration = 0.7f;

        [SerializeField] internal ObstacleDefinition definition;
        [Tooltip("Root of the meshes, animated by reactions. Defaults to the first child.")]
        [SerializeField] internal Transform visual;
        [Tooltip("Starts out of the lane; a MischiefSpot knocks it in when the rooster runs past.")]
        [SerializeField] internal bool hiddenUntilMischief;

        Collider[] _colliders;
        Vector3 _restPosition;
        Quaternion _restRotation;
        Vector3 _restScale;
        bool _cached;
        bool _armed;
        float _revealTimer = -1f;
        float _reactionTimer = -1f;

        public ObstacleDefinition Definition => definition;
        public bool IsArmed => _armed;
        public float X => transform.position.x;

        void Awake()
        {
            Cache();
            ResetPart();
        }

        void Cache()
        {
            if (_cached) return;
            _cached = true;
            if (visual == null && transform.childCount > 0) visual = transform.GetChild(0);
            _colliders = GetComponentsInChildren<Collider>(true);
            if (visual != null)
            {
                _restPosition = visual.localPosition;
                _restRotation = visual.localRotation;
                _restScale = visual.localScale;
            }
        }

        public void ResetPart()
        {
            Cache();
            _armed = !hiddenUntilMischief;
            _revealTimer = -1f;
            _reactionTimer = -1f;
            SetCollidersEnabled(_armed);
            if (visual != null)
            {
                visual.gameObject.SetActive(!hiddenUntilMischief);
                visual.localPosition = _restPosition;
                visual.localRotation = _restRotation;
                visual.localScale = _restScale;
            }
        }

        /// <summary>The kid ran into it. Disarms the obstacle and plays its reaction.</summary>
        public void Hit()
        {
            if (!_armed) return;
            _armed = false;
            SetCollidersEnabled(false);
            _reactionTimer = 0f;

            var reaction = definition != null ? definition.Reaction : HitReaction.None;
            var color = definition != null ? definition.ReactionColor : Color.gray;
            var top = transform.position + Vector3.up * 0.8f;
            if (definition != null && !string.IsNullOrEmpty(definition.Bark)) WorldBarks.Show(definition.Bark, top, color);

            switch (reaction)
            {
                case HitReaction.Smash:
                    if (visual != null) visual.gameObject.SetActive(false);
                    Debris.Burst(transform.position + Vector3.up * 0.3f, color, 12, 4f, 0.12f);
                    break;
                case HitReaction.Splat:
                    Debris.Burst(transform.position + Vector3.up * 0.05f, color, 8, 2.5f, 0.08f);
                    break;
            }
        }

        /// <summary>The rooster knocked it into the lane: it tumbles in and arms itself when it lands.</summary>
        public void Reveal()
        {
            if (!hiddenUntilMischief || _revealTimer >= 0f || _armed) return;
            if (visual != null) visual.gameObject.SetActive(true);
            _revealTimer = 0f;
        }

        void Update()
        {
            if (visual == null) return;
            float dt = Time.deltaTime;

            if (_revealTimer >= 0f)
            {
                _revealTimer += dt;
                float t = Mathf.Clamp01(_revealTimer / RevealDuration);
                // Knocked off a veranda behind the lane: it arcs in from the back and lands upright.
                float fall = 1f - t * t;
                visual.localPosition = _restPosition + new Vector3(0f, 1.2f * fall + 0.6f * Mathf.Sin(Mathf.PI * t), 1.6f * fall);
                visual.localRotation = _restRotation * Quaternion.Euler(140f * fall, 0f, 0f);
                if (t >= 1f)
                {
                    _revealTimer = -1f;
                    _armed = true;
                    SetCollidersEnabled(true);
                    Debris.Burst(transform.position, new Color(0.6f, 0.45f, 0.3f), 6, 1.5f, 0.06f);
                }
                return;
            }

            if (_reactionTimer < 0f || definition == null) return;
            _reactionTimer += dt;
            float k = Mathf.Clamp01(_reactionTimer / ReactionDuration);
            switch (definition.Reaction)
            {
                case HitReaction.Wake:
                    visual.localPosition = _restPosition + Vector3.up * (0.7f * Mathf.Sin(Mathf.PI * Mathf.Min(1f, k * 1.6f)));
                    visual.localRotation = _restRotation * Quaternion.Euler(0f, 0f, 25f * Mathf.Sin(k * 18f) * (1f - k));
                    break;
                case HitReaction.Wobble:
                    visual.localRotation = _restRotation * Quaternion.Euler(35f * Mathf.Sin(k * 20f) * (1f - k), 0f, 0f);
                    break;
                case HitReaction.Splat:
                    float squash = Mathf.Lerp(1.6f, 1.2f, k);
                    visual.localScale = new Vector3(_restScale.x * squash, _restScale.y * 0.5f, _restScale.z * squash);
                    break;
            }
            if (k >= 1f) _reactionTimer = -1f;
        }

        void SetCollidersEnabled(bool enabled)
        {
            foreach (var c in _colliders) c.enabled = enabled;
        }
    }
}
