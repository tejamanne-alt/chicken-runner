using UnityEngine;

namespace ChickenRunner
{
    public enum PickupKind
    {
        /// <summary>The currency; lines of them mark the best route.</summary>
        Mango,
        /// <summary>A 2-second sprint.</summary>
        Chilli,
        /// <summary>Three hidden per level on the harder routes; they unlock outfits.</summary>
        Feather,
    }

    /// <summary>A collectible with a trigger collider. Spins, pops when taken, comes back when its chunk is reused.</summary>
    public sealed class Pickup : MonoBehaviour, IChunkPart
    {
        const float PopDuration = 0.15f;

        [SerializeField] internal PickupKind kind = PickupKind.Mango;
        [SerializeField] internal Transform visual;
        [SerializeField] internal float spinSpeed = 180f;

        Collider _collider;
        Vector3 _restScale = Vector3.one;
        float _popTimer = -1f;
        bool _cached;

        public PickupKind Kind => kind;
        public bool Collected { get; private set; }

        void Awake()
        {
            Cache();
            ResetPart();
        }

        void Cache()
        {
            if (_cached) return;
            _cached = true;
            _collider = GetComponent<Collider>();
            if (visual == null && transform.childCount > 0) visual = transform.GetChild(0);
            if (visual != null) _restScale = visual.localScale;
        }

        public void Collect()
        {
            if (Collected) return;
            Collected = true;
            if (_collider != null) _collider.enabled = false;
            _popTimer = 0f;
        }

        public void ResetPart()
        {
            Cache();
            Collected = false;
            _popTimer = -1f;
            if (_collider != null) _collider.enabled = true;
            if (visual != null)
            {
                visual.gameObject.SetActive(true);
                visual.localScale = _restScale;
            }
        }

        void Update()
        {
            if (visual == null) return;
            visual.Rotate(0f, spinSpeed * Time.deltaTime, 0f, Space.World);
            if (_popTimer < 0f) return;

            _popTimer += Time.deltaTime;
            float t = _popTimer / PopDuration;
            if (t >= 1f)
            {
                visual.gameObject.SetActive(false);
                _popTimer = -1f;
            }
            else
            {
                visual.localScale = _restScale * (1f + t);
            }
        }
    }
}
