using System;
using System.Collections.Generic;
using System.Globalization;

namespace ChickenRunner.Core
{
    /// <summary>
    /// Derived numbers and sanity checks for a ChaseTuning, so a designer can see what a change does
    /// (and where it breaks the doc's promises) without playing a level.
    /// </summary>
    public sealed class TuningReport
    {
        public readonly List<KeyValuePair<string, string>> Lines = new List<KeyValuePair<string, string>>();
        public readonly List<string> Warnings = new List<string>();

        /// <summary>Clearance the feet need above a ledge for a landing to feel fair, in metres.</summary>
        public const float LedgeClearance = 0.15f;

        /// <summary>Shortest fair timing window for a double jump onto the tallest roof, in seconds.</summary>
        public const float MinDoubleJumpWindow = 0.15f;

        /// <summary>Take-off room a gap meant for a single jump should leave, in metres.</summary>
        public const float MinTakeOffRoom = 0.3f;

        public static TuningReport Build(ChaseTuning t, float forecastStep = 1f / 60f)
        {
            var r = new TuningReport();
            float g = JumpMath.Gravity(t);
            float jumpLength = JumpMath.JumpLengthAt(t, t.kidRunSpeed);
            float stumbleLoss = KidSpeedModel.DistanceLost(t.kidRunSpeed, t.stumbleSpeedFactor, t.stumbleDuration);
            float vaultLoss = KidSpeedModel.DistanceLost(t.kidRunSpeed, t.vaultSpeedFactor, t.vaultDuration);
            float chilliGain = t.kidRunSpeed * t.boostSpeedBonus * t.boostDuration;
            float roosterSlower = 1f - t.roosterRunSpeed / t.kidRunSpeed;

            r.Add("Gravity", F(g, "0.0") + " m/s²");
            r.Add("Jump launch speed", F(JumpMath.JumpVelocity(t), "0.00") + " m/s");
            r.Add("Jump length at run speed", F(jumpLength) + " m");
            r.Add("Tap jump height", F(t.tapJumpHeight) + " m (hold for " + F(t.jumpHeight) + " m)");
            r.Add("Double jump apex", F(t.doubleJumpTotalHeight) + " m, only if pressed exactly at the first apex");
            if (t.roofHeightMax > 0f)
                r.Add("Double-jump window, tallest roof", F(JumpMath.DoubleJumpWindowFor(t, t.roofHeightMax + LedgeClearance) * 1000f, "0") + " ms");
            r.Add("Stumble costs", F(stumbleLoss) + " m");
            r.Add("Slow vault costs", F(vaultLoss) + " m");
            r.Add("Chilli gains", F(chilliGain) + " m");
            r.Add("Rooster pace", F(roosterSlower * 100f, "0.0") + "% slower than the kid");

            var clean = ChaseForecast.Run(t, t.startGapNoBasket, null, null, forecastStep);
            var smooth = ChaseForecast.Run(t, t.startGapSmoothLift, null, null, forecastStep);
            var clumsy = ChaseForecast.Run(t, t.startGapClumsyLift, null, null, forecastStep);
            r.Add("Clean catch, " + F(t.startGapNoBasket, "0") + " m start", Describe(clean));
            r.Add("Clean catch, smooth lift", Describe(smooth));
            r.Add("Clean catch, clumsy lift", Describe(clumsy));
            r.Add("Rooster reaches course end after", F((t.courseLength - t.startGapNoBasket) / t.roosterRunSpeed, "0") + " s");

            float tightest = ChaseForecast.TightestSurvivableMistakeInterval(t, t.startGapNoBasket, forecastStep);
            r.Add("Most mistakes that still win", float.IsPositiveInfinity(tightest)
                ? "none"
                : "one every " + F(tightest, "0.##") + " s");

            Check(r, t, clean, stumbleLoss, chilliGain, roosterSlower, jumpLength);
            return r;
        }

        static void Check(TuningReport r, ChaseTuning t, ForecastResult clean, float stumbleLoss, float chilliGain,
            float roosterSlower, float jumpLength)
        {
            if (clean.outcome != ChaseOutcome.Caught)
                r.Warnings.Add("A clean run never catches the rooster (" + clean.outcome + "). The kid must be faster than the rooster with room to spare.");
            else if (clean.time < 20f || clean.time > 40f)
                r.Warnings.Add("A clean run catches the rooster in " + F(clean.time, "0") + " s; the doc aims for about 30 s.");

            if (stumbleLoss < 2f || stumbleLoss > 3f)
                r.Warnings.Add("A stumble costs " + F(stumbleLoss) + " m; the doc says mistakes cost 2 to 3 m.");

            if (chilliGain < 4f || chilliGain > 6f)
                r.Warnings.Add("A chilli gains " + F(chilliGain) + " m; the doc says about 5 m.");

            if (roosterSlower < 0.05f || roosterSlower > 0.12f)
                r.Warnings.Add("The rooster is " + F(roosterSlower * 100f, "0") + "% slower than the kid; the doc says about 8%.");

            if (t.tauntDistance >= t.escapeDistance)
                r.Warnings.Add("Taunt distance is not below escape distance, so the rubber band never fires before the rooster escapes.");

            if (t.panicDistance <= t.grabDistance)
                r.Warnings.Add("Panic distance is inside grab distance, so the panic burst can never fire.");

            if (t.roofHeightMax > 0f)
            {
                float window = JumpMath.DoubleJumpWindowFor(t, t.roofHeightMax + LedgeClearance);
                if (window < MinDoubleJumpWindow)
                {
                    // A full jump spends `window` seconds above height h - g w² / 8, so this is the slack a fair window needs.
                    float slack = JumpMath.Gravity(t) * MinDoubleJumpWindow * MinDoubleJumpWindow / 8f;
                    r.Warnings.Add("The tallest roof (" + F(t.roofHeightMax) + " m) leaves a " + F(window * 1000f, "0")
                        + " ms window for the double jump that clears it by " + F(LedgeClearance) + " m (the double jump tops out at "
                        + F(t.doubleJumpTotalHeight) + " m). For a " + F(MinDoubleJumpWindow * 1000f, "0") + " ms window, lower roofs to "
                        + F(t.doubleJumpTotalHeight - LedgeClearance - slack) + " m or raise the double jump to "
                        + F(t.roofHeightMax + LedgeClearance + slack) + " m.");
                }
            }

            if (t.canalWidths != null && t.canalWidths.Length > 0)
            {
                float doubleJumpReach = DoubleJumpLength(t);
                float widest = 0f;
                foreach (float width in t.canalWidths) widest = Math.Max(widest, width);
                foreach (float width in t.canalWidths)
                {
                    if (width > doubleJumpReach)
                        r.Warnings.Add("A " + F(width) + " m canal is longer than a double jump (" + F(doubleJumpReach) + " m) at this speed.");
                    else if (width < widest && width > jumpLength - MinTakeOffRoom)
                        r.Warnings.Add("A " + F(width) + " m canal leaves " + F(Math.Max(0f, jumpLength - width))
                            + " m of take-off room for a single jump (" + F(jumpLength) + " m long at this speed).");
                }
            }

            if (jumpLength < 2.5f)
                r.Warnings.Add("A full jump is only " + F(jumpLength) + " m long; pot stacks and dogs will feel cramped.");
        }

        /// <summary>Ground-to-ground length of a full jump with the double jump pressed at the first apex.</summary>
        public static float DoubleJumpLength(ChaseTuning t)
        {
            float g = JumpMath.Gravity(t);
            float v1 = JumpMath.JumpVelocity(t);
            float v2 = JumpMath.DoubleJumpVelocity(t);
            float rise1 = v1 / g;
            float rise2 = v2 / g;
            float fall = (float)Math.Sqrt(2.0 * t.doubleJumpTotalHeight / g);
            return t.kidRunSpeed * (rise1 + rise2 + fall);
        }

        void Add(string label, string value) => Lines.Add(new KeyValuePair<string, string>(label, value));

        static string Describe(ForecastResult f) =>
            f.outcome == ChaseOutcome.Caught
                ? F(f.time, "0.0") + " s, " + F(f.kidDistance, "0") + " m run, " + f.panicBursts + " panic bursts"
                : f.outcome.ToString();

        static string F(float value, string format = "0.0#") => value.ToString(format, CultureInfo.InvariantCulture);
    }
}
