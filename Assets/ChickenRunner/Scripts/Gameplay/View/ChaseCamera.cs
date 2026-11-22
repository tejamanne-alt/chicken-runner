using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Side-on follow camera with a slight perspective. Keeps the kid on the left third and pulls back as the gap
    /// grows so the rooster stays in frame up to the zone's framingMaxGap; past that the HUD shows an edge arrow.
    /// A plain script for the grey-box; the doc's Cinemachine rig can take over the same framing rule later.
    /// </summary>
    [RequireComponent(typeof(Camera))]
    public sealed class ChaseCamera : MonoBehaviour
    {
        [SerializeField] internal KidController kid;
        [SerializeField] internal RoosterBrain rooster;
        [SerializeField] internal ChaseDirector director;

        [Header("Framing (fractions of screen width)")]
        [SerializeField, Range(0.1f, 0.5f)] internal float kidScreenX = 1f / 3f;
        [SerializeField, Range(0.5f, 0.98f)] internal float roosterScreenX = 0.88f;
        [Tooltip("Metres of course visible at the kid's depth when the rooster is close.")]
        [SerializeField] internal float minVisibleWidth = 13f;

        [Header("Height")]
        [Tooltip("Where the ground under the kid sits on screen, as a fraction of screen height from the bottom.")]
        [SerializeField, Range(0.1f, 0.5f)] internal float groundScreenY = 0.28f;
        [SerializeField] internal float cameraRaise = 0.8f;
        [Tooltip("How much of the kid's height above the ground the camera follows (roofs, bounces).")]
        [SerializeField, Range(0f, 1f)] internal float verticalFollow = 0.45f;

        [Header("Smoothing, seconds")]
        [SerializeField] internal float zoomSmoothTime = 0.45f;
        [SerializeField] internal float heightSmoothTime = 0.3f;

        Camera _camera;
        float _distance;
        float _distanceVelocity;
        float _height;
        float _heightVelocity;

        public Camera Camera => _camera != null ? _camera : _camera = GetComponent<Camera>();

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
            float gap = director != null ? director.FramedGap : 0f;
            float width = Mathf.Max(minVisibleWidth, (gap + 0.8f) / Mathf.Max(0.05f, roosterScreenX - kidScreenX));
            float targetDistance = width / (2f * Mathf.Tan(HorizontalFov(cam) * 0.5f));
            float targetHeight = kid.transform.position.y * verticalFollow;

            if (snap || _distance <= 0f)
            {
                _distance = targetDistance;
                _height = targetHeight;
                _distanceVelocity = 0f;
                _heightVelocity = 0f;
            }
            else
            {
                float dt = Time.unscaledDeltaTime;
                _distance = Mathf.SmoothDamp(_distance, targetDistance, ref _distanceVelocity, zoomSmoothTime, Mathf.Infinity, dt);
                _height = Mathf.SmoothDamp(_height, targetHeight, ref _heightVelocity, heightSmoothTime, Mathf.Infinity, dt);
            }

            float visibleWidth = 2f * _distance * Mathf.Tan(HorizontalFov(cam) * 0.5f);
            float visibleHeight = 2f * _distance * Mathf.Tan(cam.fieldOfView * 0.5f * Mathf.Deg2Rad);
            float centreX = kid.transform.position.x + (0.5f - kidScreenX) * visibleWidth;
            // Aim above the ground so it sits low on screen at every zoom, leaving the upper part for jumps and roofs.
            float lookY = _height + (0.5f - groundScreenY) * visibleHeight;
            var position = new Vector3(centreX, lookY + cameraRaise, -_distance);
            transform.SetPositionAndRotation(position, Quaternion.LookRotation(new Vector3(centreX, lookY, 0f) - position));
        }

        static float HorizontalFov(Camera cam) =>
            Camera.VerticalToHorizontalFieldOfView(cam.fieldOfView, Mathf.Max(0.1f, cam.aspect)) * Mathf.Deg2Rad;
    }
}
