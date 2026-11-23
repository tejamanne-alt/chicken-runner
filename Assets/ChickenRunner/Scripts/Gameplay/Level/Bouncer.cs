using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// A rope cot, a stall's awning or a buffalo's back: touching it from above or running into it bounces the kid high.
    /// It never costs distance. Needs a trigger collider whose top is the bouncing surface. An awning's trigger hangs
    /// above head height, so the kid runs under it and only bounces off it from a jump.
    /// </summary>
    public sealed class Bouncer : MonoBehaviour, IChunkPart
    {
        const float SquashDuration = 0.3f;

        [SerializeField] internal Transform visual;
        [Tooltip("Bounce height in metres; 0 uses the zone tuning's cot bounce height.")]
        [SerializeField, Min(0f)] internal float bounceHeight;
        [SerializeField] internal string bark = "BOING!";

        Collider _collider;
        Vector3 _restScale = Vector3.one;
        float _squashTimer = -1f;

        public float TopY => _collider != null ? _collider.bounds.max.y : transform.position.y;
        public float BounceHeight => bounceHeight;

        void Awake()
        {
            _collider = GetComponent<Collider>();
            if (visual == null && transform.childCount > 0) visual = transform.GetChild(0);
            if (visual != null) _restScale = visual.localScale;
        }

        public void Bounce()
        {
            _squashTimer = 0f;
            if (!string.IsNullOrEmpty(bark))
                WorldBarks.Show(bark, new Vector3(transform.position.x, TopY + 0.7f, 0f), new Color(0.2f, 0.6f, 0.3f));
        }

        public void ResetPart()
        {
            _squashTimer = -1f;
            if (visual != null) visual.localScale = _restScale;
        }

        void Update()
        {
            if (_squashTimer < 0f || visual == null) return;
            _squashTimer += Time.deltaTime;
            float t = Mathf.Clamp01(_squashTimer / SquashDuration);
            float squash = 1f - 0.45f * Mathf.Sin(Mathf.PI * t) * (1f - t * 0.5f);
            visual.localScale = new Vector3(_restScale.x, _restScale.y * squash, _restScale.z);
            if (t >= 1f) _squashTimer = -1f;
        }
    }
}
