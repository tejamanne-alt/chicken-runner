using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Plays the 3D rooster's clips from the RoosterBrain: pecking about before the chase, running (faster legs the faster
    /// he goes), fluttering over hops and up onto roofs, the crowing taunt, a startled leap when the kid gets close and
    /// then the panic sprint with flapping wings, and the tumble out of the kid's hands. Only reads the brain.
    /// </summary>
    public sealed class RoosterModelVisual : MonoBehaviour
    {
        [SerializeField] internal RoosterBrain rooster;
        [SerializeField] internal Animator animator;
        [Tooltip("The run speed the Run clip was made for, in m/s.")]
        [SerializeField] internal float runReferenceSpeed = 5.5f;
        [SerializeField] internal float crossFade = 0.06f;

        string _state;
        float _startledTimer;

        void OnEnable()
        {
            if (rooster == null) rooster = GetComponentInParent<RoosterBrain>();
            if (animator == null) animator = GetComponentInChildren<Animator>();
            if (rooster != null) rooster.Panicked += OnPanicked;
        }

        void OnDisable()
        {
            if (rooster != null) rooster.Panicked -= OnPanicked;
        }

        void OnPanicked() => _startledTimer = 0.3f;

        void LateUpdate()
        {
            if (rooster == null || animator == null) return;
            _startledTimer = Mathf.Max(0f, _startledTimer - Time.deltaTime);
            string state;
            float speed = 1f;
            switch (rooster.Act)
            {
                case RoosterAct.Idle: state = "Idle"; break;
                case RoosterAct.Wriggle: state = "Tumble"; break;
                case RoosterAct.Burst:
                    state = rooster.BurstTime < 0.3f ? "Startled" : "Panic";
                    speed = state == "Panic" ? Mathf.Clamp(rooster.Speed / Mathf.Max(0.1f, runReferenceSpeed * 1.3f), 1f, 2.5f) : 1f;
                    break;
                default:
                    if (rooster.IsAirborne) state = "Flutter";
                    else if (rooster.Mood == RoosterMood.Taunting && rooster.Speed < 1f) { state = "Crow"; }
                    else if (_startledTimer > 0f) { state = "Startled"; }
                    else if (rooster.Mood == RoosterMood.Panicking) { state = "Panic"; speed = rooster.Speed / Mathf.Max(0.1f, runReferenceSpeed * 1.3f); }
                    else { state = "Run"; speed = rooster.Speed / Mathf.Max(0.1f, runReferenceSpeed); }
                    break;
            }
            animator.speed = Mathf.Clamp(speed, 0.4f, 2.5f);
            if (state == _state) return;
            animator.CrossFadeInFixedTime(state, crossFade, 0, 0f);
            _state = state;
        }
    }
}
