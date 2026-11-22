using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Grey-box animation that makes the block rooster readable: run bob, wing flaps on hops, the turn-and-crow
    /// taunt, panic jitter with a feather trail, and a spin while wriggling free. Pivot of the body is at his feet.
    /// </summary>
    public sealed class RoosterVisual : MonoBehaviour
    {
        [SerializeField] internal RoosterBrain brain;
        [SerializeField] internal Transform body;
        [SerializeField] internal Transform head;
        [SerializeField] internal Transform wing;
        [SerializeField] internal Color featherColor = new Color(0.9f, 0.45f, 0.15f);

        float _phase;
        float _facing;
        float _featherTimer;
        Vector3 _headRest;
        Quaternion _wingRest = Quaternion.identity;

        void Awake()
        {
            if (brain == null) brain = GetComponentInParent<RoosterBrain>();
            if (head != null) _headRest = head.localPosition;
            if (wing != null) _wingRest = wing.localRotation;
        }

        void LateUpdate()
        {
            if (brain == null || body == null) return;
            float dt = Time.deltaTime;
            float t = Time.time;
            _phase += Mathf.Max(brain.Speed, 1.5f) * dt * 3f;

            bool taunting = brain.Act == RoosterAct.Chase && brain.Mood == RoosterMood.Taunting;
            bool panicking = brain.Act == RoosterAct.Chase && brain.Mood == RoosterMood.Panicking;

            // Turn round to face the kid while crowing.
            _facing = Mathf.MoveTowards(_facing, taunting ? 180f : 0f, 900f * dt);

            float bob = brain.Act == RoosterAct.Idle ? 0f : Mathf.Abs(Mathf.Sin(_phase)) * 0.05f;
            float tilt = 0f;
            float puff = 1f;
            var headOffset = Vector3.zero;

            if (brain.Act == RoosterAct.Idle)
            {
                // Pecking at the ground.
                float peck = Mathf.Max(0f, Mathf.Sin(t * 5f));
                headOffset = new Vector3(0.05f, -0.15f, 0f) * peck;
                tilt = -20f * peck;
            }
            else if (taunting)
            {
                puff = 1.15f;
                headOffset = new Vector3(0f, 0.08f + 0.04f * Mathf.Sin(t * 14f), 0f);
                tilt = 12f;
                bob = 0f;
            }
            else if (panicking)
            {
                tilt = -25f + Mathf.Sin(t * 50f) * 10f;
                bob *= 1.8f;
                _featherTimer -= dt;
                if (_featherTimer <= 0f)
                {
                    _featherTimer = 0.07f;
                    Debris.Feathers(transform.position + Vector3.up * 0.35f, featherColor, 1);
                }
            }
            else if (brain.Act == RoosterAct.Wriggle)
            {
                tilt = t * 1080f % 360f;
            }
            else
            {
                tilt = -10f;
            }

            body.localPosition = new Vector3(0f, bob, 0f);
            body.localRotation = Quaternion.Euler(0f, _facing, tilt);
            body.localScale = Vector3.one * puff;
            if (head != null) head.localPosition = _headRest + headOffset;

            if (wing != null)
            {
                bool flapping = brain.IsAirborne || panicking || taunting;
                float flap = flapping ? Mathf.Sin(t * (taunting ? 12f : 40f)) * 60f : 0f;
                wing.localRotation = _wingRest * Quaternion.Euler(flap, 0f, 0f);
            }
        }
    }
}
