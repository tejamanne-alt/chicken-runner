using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Level 1's opening in the neighbour's yard: the bamboo basket the rooster sits under, which the kid lifts by its
    /// near rim while the player holds (it turns up on its far rim, as kid_anims' BasketLift clip lifts it), and the
    /// neighbour asleep on his cot, who wakes when the rooster bursts out. <see cref="GameFlow"/> runs the sequence;
    /// this only shows it. Built by GameBuilder.Plans from the level plan's "basket" and "neighbour" items.
    /// </summary>
    public sealed class BasketIntro : MonoBehaviour, IChunkPart
    {
        /// <summary>The basket on the course now (one level has one), or null.</summary>
        public static BasketIntro Active { get; private set; }

        [Tooltip("The basket's far rim, on the ground: it turns about this. The basket's model is its child.")]
        [SerializeField] internal Transform hinge;
        [SerializeField] internal GameObject neighbourAsleep;
        [SerializeField] internal GameObject neighbourAwake;
        [Tooltip("How far the lift turns the basket up, degrees (kid_anims.BASKET_MAX_ANGLE).")]
        [SerializeField] internal float maxAngle = 40f;
        [Tooltip("Course x the kid tiptoes in from.")]
        [SerializeField] internal float walkFrom = -4.4f;
        [Tooltip("Course x of the rooster under the basket.")]
        [SerializeField] internal float roosterX = 0.7f;

        Vector3 _hingeRest;
        Quaternion _hingeRestRotation;
        bool _haveRest;
        float _lift;
        float _toss;

        public float WalkFrom => walkFrom;
        public float RoosterX => roosterX;
        public Vector3 NeighbourPosition => neighbourAsleep != null ? neighbourAsleep.transform.position : transform.position;

        void Awake() => CacheRest();

        void CacheRest()
        {
            if (_haveRest || hinge == null) return;
            _hingeRest = hinge.localPosition;
            _hingeRestRotation = hinge.localRotation;
            _haveRest = true;
        }

        void OnEnable() => Active = this;

        void OnDisable()
        {
            if (Active == this) Active = null;
        }

        /// <summary>The lift, 0 (down over the rooster) to 1 (propped open on its far rim).</summary>
        public void SetLift(float progress)
        {
            _lift = Mathf.Clamp01(progress);
            Apply();
        }

        /// <summary>After the burst: the kid flings the basket aside, off the lane, over 0 to 1.</summary>
        public void SetToss(float progress)
        {
            _toss = Mathf.Clamp01(progress);
            Apply();
        }

        public void Wake(bool awake)
        {
            if (neighbourAsleep != null) neighbourAsleep.SetActive(!awake);
            if (neighbourAwake != null) neighbourAwake.SetActive(awake);
        }

        void Apply()
        {
            CacheRest();
            if (hinge == null) return;
            float k = _lift * _lift * (3f - 2f * _lift);
            float angle = maxAngle * k;
            // Tossed: it keeps turning over its rim and flies back off the lane, landing on its side behind it.
            float t = _toss;
            angle = Mathf.Lerp(angle, 105f, t);
            var offset = new Vector3(0.35f * t, 0.6f * Mathf.Sin(Mathf.PI * t), 1.5f * t);
            hinge.localPosition = _hingeRest + offset;
            // The near rim is toward the kid (-x): turning it up is a negative turn about the lane's depth axis.
            hinge.localRotation = _hingeRestRotation * Quaternion.Euler(0f, 0f, -angle);
        }

        public void ResetPart()
        {
            _lift = 0f;
            _toss = 0f;
            Wake(false);
            Apply();
        }
    }
}
