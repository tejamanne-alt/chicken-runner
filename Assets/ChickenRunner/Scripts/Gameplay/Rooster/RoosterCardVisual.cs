using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// The rooster drawn from his painted poses (ArtSource/cutouts/rooster): pecking and strutting before the chase,
    /// two running frames swapped by distance, flutter over hops, crowing while he taunts, startled when he panics,
    /// tumbling out of the kid's hands. Only reads the RoosterBrain.
    /// </summary>
    public sealed class RoosterCardVisual : MonoBehaviour
    {
        [SerializeField] internal RoosterBrain rooster;
        [SerializeField] internal Transform body;
        [SerializeField] internal CardFlipbook card;

        [Header("Poses")]
        [SerializeField] internal Texture2D run1;
        [SerializeField] internal Texture2D run2;
        [SerializeField] internal Texture2D flutter;
        [SerializeField] internal Texture2D crow;
        [SerializeField] internal Texture2D startled;
        [SerializeField] internal Texture2D tumble;
        [SerializeField] internal Texture2D peck;
        [SerializeField] internal Texture2D strut;

        [Header("Timing")]
        [SerializeField, Min(0.05f)] internal float frameDistance = 0.32f;
        [SerializeField, Min(0.1f)] internal float idleCycle = 1.8f;

        float _distance;
        float _lastX;
        float _spin;

        void OnEnable()
        {
            if (rooster == null) rooster = GetComponentInParent<RoosterBrain>();
            if (rooster != null) _lastX = rooster.transform.position.x;
        }

        void LateUpdate()
        {
            if (rooster == null || card == null) return;
            float dt = Time.deltaTime;
            float x = rooster.transform.position.x;
            float dx = x - _lastX;
            _lastX = x;
            if (dx > 0f && dx < 2f) _distance += dx;
            bool second = (int)(_distance / frameDistance) % 2 == 1;

            Texture2D frame;
            float spinSpeed = 0f;
            switch (rooster.Act)
            {
                case RoosterAct.Idle:
                    frame = Mathf.Repeat(Time.time, idleCycle) < idleCycle * 0.6f ? peck : strut;
                    break;
                case RoosterAct.Wriggle:
                    frame = tumble;
                    spinSpeed = 540f;
                    break;
                default:
                    if (rooster.IsAirborne) frame = flutter;
                    else if (rooster.Mood == RoosterMood.Taunting && rooster.Speed < 1f) frame = crow;
                    else if (rooster.Mood == RoosterMood.Panicking) frame = second ? startled : run1;
                    else frame = second ? run2 : run1;
                    break;
            }
            card.Show(frame != null ? frame : run1);

            if (body == null) return;
            _spin = spinSpeed > 0f ? _spin + spinSpeed * dt : Mathf.MoveTowardsAngle(_spin, 0f, 720f * dt);
            body.localRotation = Quaternion.Euler(0f, 0f, -_spin);
        }
    }
}
