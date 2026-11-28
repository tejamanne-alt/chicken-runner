using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// The chase camera, framed as Kick Off's gameplay is on a phone (measured from a 2868 x 1320 screenshot of it): a
    /// perspective camera looking along +z at the lane, tilted 4 degrees down, the kid 24.1% of the screen tall with her
    /// feet 16.9% up it and 40% of the way across, the road under her and the village close behind (a house's base about
    /// 35% up the screen, its eaves about 70%), the sky above. Kick Off's kid is 1.3 m tall in a 5.4 m view; this kid is
    /// 1.08 m, so the view is 4.48 m tall, about 7.3 m back, and on the screen she is the same size. A faster zone pulls
    /// back just enough to keep three quarters of a second of lane ahead in view.
    ///
    /// Unlike Kick Off's camera it follows the ground the kid runs on rather than the kid, so jumps do not bob the
    /// view: it rises when she lands on a roof and drops when she drops. The rooster: a close one is brought into the
    /// frame with a mild pull-back (at most <see cref="maxRoosterZoom"/>, as Kick Off's aim zoom); a farther one is
    /// off to the right and the HUD's edge arrow shows him. Before a chase (<see cref="Establishing"/>) the view pulls
    /// back to show the kid and the rooster both, then eases in when the chase starts.
    /// </summary>
    [RequireComponent(typeof(Camera))]
    public sealed class ChaseCamera : MonoBehaviour
    {
        [SerializeField] internal KidController kid;
        [SerializeField] internal RoosterBrain rooster;
        [SerializeField] internal ChaseDirector director;

        [Header("Framing, measured from Kick Off's gameplay")]
        [Tooltip("The kid's standing height (m): the Kid model is 1.08 m.")]
        [SerializeField] internal float kidHeight = 1.08f;
        [Tooltip("How tall she stands on screen, as a share of its height (Kick Off: 0.241).")]
        [SerializeField, Range(0.1f, 0.4f)] internal float kidScreenHeight = 0.241f;
        [Tooltip("Where her feet are on screen, as a share of its height up from the bottom (Kick Off: 0.169).")]
        [SerializeField, Range(0.05f, 0.4f)] internal float feetScreenY = 0.169f;
        [Tooltip("Where she stands across the screen (0 = left edge; Kick Off: 0.40), the lane ahead of her.")]
        [SerializeField, Range(0.2f, 0.5f)] internal float kidScreenX = 0.4f;
        [Tooltip("At least this many seconds of lane ahead of her at her running speed: a faster zone, or a narrower "
            + "screen, pulls back just enough.")]
        [SerializeField] internal float lookAheadSeconds = 0.75f;
        [Tooltip("Downward tilt in degrees, so the lane's ground shows (Kick Off: 4).")]
        [SerializeField] internal float pitch = 4f;

        [Header("The rooster")]
        [Tooltip("At most this much the view pulls back to bring a close rooster into the frame.")]
        [SerializeField] internal float maxRoosterZoom = 1.25f;
        [Tooltip("Where a framed rooster may stand across the screen at most.")]
        [SerializeField, Range(0.6f, 0.98f)] internal float roosterScreenX = 0.9f;
        [Tooltip("Before the chase: pulled back to show the kid and the rooster both, at most this much.")]
        [SerializeField] internal float maxEstablishingZoom = 2.4f;

        [Header("Smoothing, seconds")]
        [SerializeField] internal float heightSmoothTime = 0.35f;
        [SerializeField] internal float zoomSmoothTime = 0.6f;

        Camera _camera;
        float _ground;
        float _height;
        float _heightVelocity;
        float _zoom = 1f;
        float _zoomVelocity;
        bool _started;

        public Camera Camera => _camera != null ? _camera : _camera = GetComponent<Camera>();

        /// <summary>Before the chase starts: the view pulls back to show the rooster too. GameFlow sets it.</summary>
        public bool Establishing { get; set; }

        /// <summary>Whether the rooster is on screen; the HUD draws an edge arrow when he is not.</summary>
        public bool IsRoosterVisible(out Vector3 viewportPoint)
        {
            viewportPoint = Camera.WorldToViewportPoint(rooster.transform.position + Vector3.up * 0.3f);
            return viewportPoint.z > 0f && viewportPoint.x <= 0.98f;
        }

        public void Snap() => Frame(true);

        void LateUpdate() => Frame(false);

        void Frame(bool snap)
        {
            if (kid == null) return;
            var cam = Camera;
            float aspect = Mathf.Max(0.1f, cam.aspect);
            var feet = kid.transform.position;

            // The ground she runs on: where she last stood, or lower if she falls below it (off a roof, into a canal).
            if (snap || !_started || kid.IsGrounded || feet.y < _ground) _ground = feet.y;

            // The close framing: the kid as big on screen as Kick Off's, or a touch wider where a fast zone or a narrow
            // screen needs the lane ahead.
            float run = director != null && director.Tuning != null ? director.Tuning.kidRunSpeed : 6f;
            float minHalf = lookAheadSeconds * run / (2f * (1f - kidScreenX));
            float baseHalfHeight = Mathf.Max(0.5f * kidHeight / Mathf.Max(0.05f, kidScreenHeight), minHalf / aspect);
            float targetZoom = RoosterZoom(baseHalfHeight * aspect);

            // The view's centre above the ground she runs on, so her feet sit feetScreenY up the screen at any zoom.
            float targetHeight = _ground + (1f - 2f * feetScreenY) * baseHalfHeight * targetZoom;
            if (snap || !_started)
            {
                _zoom = targetZoom;
                _height = targetHeight;
                _zoomVelocity = _heightVelocity = 0f;
                _started = true;
            }
            else
            {
                float dt = Time.unscaledDeltaTime;
                _zoom = Mathf.SmoothDamp(_zoom, targetZoom, ref _zoomVelocity, zoomSmoothTime, Mathf.Infinity, dt);
                _height = Mathf.SmoothDamp(_height, targetHeight, ref _heightVelocity, heightSmoothTime, Mathf.Infinity, dt);
            }

            float halfHeight = baseHalfHeight * _zoom;
            float halfWidth = halfHeight * aspect;
            // Keep all of her in the frame however high she goes (a bounce off the buffalo, a double jump off a roof).
            float centreY = Mathf.Max(_height, feet.y + 1.3f - halfHeight * 0.85f);
            centreY = Mathf.Min(centreY, feet.y + halfHeight * 0.8f);
            float centreX = feet.x + (0.5f - kidScreenX) * 2f * halfWidth;

            float distance = halfHeight / Mathf.Tan(cam.fieldOfView * 0.5f * Mathf.Deg2Rad);
            var rotation = Quaternion.Euler(pitch, 0f, 0f);
            transform.SetPositionAndRotation(new Vector3(centreX, centreY, 0f) - rotation * Vector3.forward * distance, rotation);
        }

        /// <summary>
        /// How far to pull back: before the chase, far enough to show the rooster (up to <see cref="maxEstablishingZoom"/>);
        /// in it, enough to bring a close rooster into the frame (up to <see cref="maxRoosterZoom"/>), else not at all.
        /// </summary>
        float RoosterZoom(float baseHalfWidth)
        {
            if (rooster == null) return 1f;
            float gap = rooster.transform.position.x - kid.transform.position.x;
            if (gap <= 0f) return 1f;
            float needed = (gap + 0.6f) / (2f * Mathf.Max(0.05f, roosterScreenX - kidScreenX)) / Mathf.Max(0.1f, baseHalfWidth);
            if (Establishing) return Mathf.Clamp(needed, 1f, maxEstablishingZoom);
            return needed <= maxRoosterZoom ? Mathf.Max(1f, needed) : 1f;
        }
    }
}
