using System;
using System.Reflection;

namespace ChickenRunner.Core
{
    /// <summary>
    /// Every number from the design doc's tuning tables, in metres and seconds.
    /// One instance lives in each zone's TuningConfig asset; gameplay reads it every tick,
    /// so edits in the Inspector apply while the game is running.
    /// </summary>
    [Serializable]
    public sealed class ChaseTuning
    {
        // Speeds and course
        public float kidRunSpeed = 6.0f;
        public float roosterRunSpeed = 5.5f;
        public float courseLength = 500f;

        // Starting gap
        public float startGapSmoothLift = 10f;
        public float startGapClumsyLift = 14f;
        public float startGapNoBasket = 12f;

        // Win and loss
        public float grabDistance = 0.8f;
        /// <summary>The dive only counts when kid and rooster are this close in height (no grabs mid-bounce).</summary>
        public float grabHeightTolerance = 1.0f;
        public float escapeDistance = 25f;

        // Rooster behaviours
        public float tauntDistance = 18f;
        public float tauntDuration = 1.4f;
        public float tauntCooldown = 5f;
        public float panicDistance = 2f;
        public float panicSpeedMultiplier = 1.3f;
        public float panicDuration = 0.8f;
        public float panicCooldown = 3f;
        /// <summary>Panic bursts allowed per chase; a negative value means unlimited.</summary>
        public int maxPanicBursts = 2;
        /// <summary>Mischief only fires when the new obstacle lands at least this far ahead of the kid.</summary>
        public float mischiefMinKidDistance = 7f;

        // Jump. Gravity is derived so a held jump is jumpHeight tall and jumpLength long at jumpReferenceSpeed.
        public float jumpHeight = 1.4f;
        public float tapJumpHeight = 0.9f;
        public float jumpLength = 3.7f;
        public float jumpReferenceSpeed = 6f;
        public float doubleJumpTotalHeight = 2.6f;
        public float fallGravityMultiplier = 1f;
        public float maxFallSpeed = 20f;
        public float fastDropSpeed = 16f;
        public float jumpBuffer = 0.1f;
        public float coyoteTime = 0.08f;
        public float cotBounceHeight = 2.4f;

        // Slide
        public float slideDuration = 0.6f;

        // Wall vault: the kid nearly stops while climbing, which is what makes it cost distance.
        public float vaultDuration = 0.45f;
        public float vaultSpeedFactor = 0.1f;
        public float maxVaultHeight = 2.8f;

        // Ladders: a scramble up the rungs and off the top. At 0.45 s it loses about 1.7 m to the rooster at 6 m/s,
        // against 2.3 m for vaulting the same roof. On the mango branch, which has no rungs, a pull-up that keeps
        // ladderSpeedFactor of the run speed.
        public float ladderClimbDuration = 0.45f;
        public float ladderSpeedFactor = 0.6f;

        // Wading across a canal (zone 2): slow going, but not a stumble.
        public float wadeSpeedFactor = 0.45f;

        // Mistakes
        public float stumbleDuration = 0.7f;
        public float stumbleSpeedFactor = 0.45f;
        public float hitGracePeriod = 0.35f;

        // Chilli boost
        public float boostSpeedBonus = 0.35f;
        public float boostDuration = 2.2f;

        // Camera keeps the rooster in frame up to this gap; beyond it the HUD shows an edge arrow.
        public float framingMaxGap = 14f;

        // Stars
        public float mangoStarFraction = 0.7f;

        // Level geometry this zone's tuning has to support; used only by TuningReport's checks.
        // Zero or empty means the zone has none (houses are in zones 1 and 3, canals in zone 2).
        public float roofHeightMin = 2.2f;
        public float roofHeightMax = 2.6f;
        public float[] canalWidths = new float[0];

        /// <summary>Design-doc starting values for zone 1, 2 or 3.</summary>
        public static ChaseTuning ForZone(int zone)
        {
            var t = new ChaseTuning();
            switch (zone)
            {
                case 2:
                    t.kidRunSpeed = 7.0f;
                    t.roosterRunSpeed = 6.4f;
                    t.courseLength = 600f;
                    t.roofHeightMin = 0f;
                    t.roofHeightMax = 0f;
                    t.canalWidths = new[] { 2.5f, 3.5f, 4.5f };
                    break;
                case 3:
                    t.kidRunSpeed = 8.0f;
                    t.roosterRunSpeed = 7.4f;
                    t.courseLength = 700f;
                    break;
            }
            return t;
        }

        /// <summary>
        /// Overwrites every value with <paramref name="source"/>'s, keeping this instance, so systems that hold
        /// a reference to it keep reading live values.
        /// </summary>
        public void CopyFrom(ChaseTuning source)
        {
            if (source == null) throw new ArgumentNullException(nameof(source));
            foreach (var field in typeof(ChaseTuning).GetFields(BindingFlags.Public | BindingFlags.Instance))
                field.SetValue(this, field.GetValue(source));
            canalWidths = source.canalWidths == null ? null : (float[])source.canalWidths.Clone();
        }

        public ChaseTuning Clone()
        {
            var copy = (ChaseTuning)MemberwiseClone();
            copy.canalWidths = canalWidths == null ? null : (float[])canalWidths.Clone();
            return copy;
        }
    }
}
