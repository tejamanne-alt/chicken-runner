using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Canal water: a trigger over a canal's bed. While the kid stands in it she wades at the tuning's wadeSpeedFactor.
    /// Wading is slow but is not a stumble, so it never costs the no-stumble star; a jump or the plank bridge is faster.
    /// </summary>
    [RequireComponent(typeof(Collider))]
    public sealed class WaterZone : MonoBehaviour
    {
        void Reset()
        {
            GetComponent<Collider>().isTrigger = true;
        }
    }
}
