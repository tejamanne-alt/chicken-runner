using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// One zone's tuning numbers. Gameplay holds a reference to <see cref="Values"/> and reads it every tick,
    /// so Inspector edits apply while the game is running (and, as with any asset, persist after Play mode).
    /// </summary>
    [CreateAssetMenu(menuName = "Chicken Runner/Tuning Config", fileName = "Tuning_Zone1", order = 0)]
    public sealed class TuningConfig : ScriptableObject
    {
        [SerializeField, Range(1, 3)] internal int zone = 1;
        [SerializeField] internal ChaseTuning values = ChaseTuning.ForZone(1);

        public int Zone => zone;
        public ChaseTuning Values => values ??= ChaseTuning.ForZone(zone);

        /// <summary>Puts every number back to the design doc's starting values for this zone.</summary>
        public void ResetToDesignValues() => values = ChaseTuning.ForZone(zone);

        void Reset() => ResetToDesignValues();
    }
}
