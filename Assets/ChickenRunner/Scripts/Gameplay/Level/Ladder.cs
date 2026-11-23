using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Something the kid climbs instead of vaulting. Put it on the wall's solid collider (or a parent of it): running into
    /// that wall climbs it in ladderClimbDuration instead of the slow vault.
    /// <para>A real ladder (<see cref="Upright"/>: the builder stands the bamboo ladder model against the wall and gives
    /// this its foot and head) is climbed rung by rung: the kid lines up with it, climbs up it facing the wall, and steps
    /// off onto the top. Anything else (the mango branch) is a quick pull-up.</para>
    /// </summary>
    public sealed class Ladder : MonoBehaviour
    {
        [Tooltip("The middle of the ladder's foot, in metres from this object's position (not scaled or turned with it).")]
        public Vector3 foot;
        [Tooltip("The middle of the ladder where it rests against the wall, in metres from this object's position.")]
        public Vector3 head;
        [Tooltip("Distance between rungs, in metres: the climb's hands and feet keep time with it.")]
        public float rungSpacing = 0.27f;

        /// <summary>A ladder to climb rung by rung, rather than a pull-up.</summary>
        public bool Upright => head.y - foot.y > 0.5f;

        public Vector3 Foot => transform.position + foot;
        public Vector3 Head => transform.position + head;

        /// <summary>The point on the ladder's middle line at world height y (clamped to its foot and head).</summary>
        public Vector3 At(float y)
        {
            Vector3 a = Foot, b = Head;
            return Vector3.Lerp(a, b, Mathf.Clamp01((y - a.y) / Mathf.Max(0.01f, b.y - a.y)));
        }
    }
}
