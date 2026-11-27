using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// The chase camera, framed as Kick Off frames its kid (Kick Off's CameraFollow2D): a perspective camera looking
    /// along +z at the lane, tilted down a touch so the ground reads as ground, close enough that the kid is about a
    /// fifth of the screen tall (5.4 m of height at the lane, or more on a narrow screen to keep 11 m of lane across),
    /// with the village close behind her and the sky above it. The kid stands on the left third with the lane ahead
    /// of her; a faster zone pulls back just enough to keep a second of lane ahead in view.
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

        [Header("Framing, as Kick Off's")]
        [Tooltip("Half the visible height at the lane (m): 2.7 shows 5.4 m, so the kid is about a fifth of the screen tall.")]
        [SerializeField] internal float viewHalfHeight = 2.7f;
        [Tooltip("At least this much lane either side of the view's centre (m); a narrower screen pulls back to keep it.")]
        [SerializeField] internal float minHalfWidth = 5.5f;
        [Tooltip("At least this many seconds of lane ahead of the kid at her running speed: a faster zone pulls back a little.")]
        [SerializeField] internal float lookAheadSeconds = 1f;
        [Tooltip("Where the kid stands across the screen (0 = left edge): the left third, the lane ahead of her.")]
        [SerializeField, Range(0.2f, 0.5f)] internal float kidScreenX = 1f / 3f;
        [Tooltip("How far the view's centre is above the ground she runs on (m), so her feet sit low in the frame "
            + "(Kick Off: 1.15 m above the kid's middle).")]
        [SerializeField] internal float focusHeight = 1.75f;
        [Tooltip("Downward tilt in degrees, so the lane's ground shows.")]
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

            // The close framing: Kick Off's size, or wider on a narrow screen or in a fast zone.
            float run = director != null && director.Tuning != null ? director.Tuning.kidRunSpeed : 6f;
            float minHalf = Mathf.Max(minHalfWidth, lookAheadSeconds * run / (2f * (1f - kidScreenX)));
            float baseHalfHeight = Mathf.Max(viewHalfHeight, minHalf / aspect);
            float targetZoom = RoosterZoom(baseHalfHeight * aspect);

            float targetHeight = _ground + focusHeight;
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
