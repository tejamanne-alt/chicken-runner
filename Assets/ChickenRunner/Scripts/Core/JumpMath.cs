using System;

namespace ChickenRunner.Core
{
    /// <summary>
    /// Turns the doc's jump numbers (height, length at a reference speed) into gravity and launch velocities,
    /// so designers tune in metres rather than in m/s².
    /// </summary>
    public static class JumpMath
    {
        /// <summary>Gravity that makes a full jump jumpHeight tall and jumpLength long at jumpReferenceSpeed.</summary>
        public static float Gravity(ChaseTuning t)
        {
            // Air time T = L / v and h = g T² / 8, so g = 8 h v² / L².
            float v = t.jumpReferenceSpeed;
            return 8f * t.jumpHeight * v * v / (t.jumpLength * t.jumpLength);
        }

        public static float JumpVelocity(ChaseTuning t) => VelocityForHeight(Gravity(t), t.jumpHeight);

        /// <summary>The double jump resets vertical speed to this value, so pressing it at the apex reaches doubleJumpTotalHeight.</summary>
        public static float DoubleJumpVelocity(ChaseTuning t) =>
            VelocityForHeight(Gravity(t), Math.Max(0f, t.doubleJumpTotalHeight - t.jumpHeight));

        public static float BounceVelocity(ChaseTuning t) => VelocityForHeight(Gravity(t), t.cotBounceHeight);

        /// <summary>Launch speed for a bounce of <paramref name="height"/> metres (awnings, a buffalo's back); 0 or less uses the cot's.</summary>
        public static float BounceVelocity(ChaseTuning t, float height) =>
            height > 0f ? VelocityForHeight(Gravity(t), height) : BounceVelocity(t);

        /// <summary>Extra gravity while rising with the button released; an instant release peaks at tapJumpHeight.</summary>
        public static float LowJumpGravityMultiplier(ChaseTuning t) =>
            t.tapJumpHeight <= 0f ? 1f : Math.Max(1f, t.jumpHeight / t.tapJumpHeight);

        public static float VelocityForHeight(float gravity, float height) =>
            height <= 0f ? 0f : (float)Math.Sqrt(2.0 * gravity * height);

        /// <summary>Ground-to-ground length of a full single jump at the given run speed.</summary>
        public static float JumpLengthAt(ChaseTuning t, float runSpeed) =>
            runSpeed * 2f * JumpVelocity(t) / Gravity(t);

        /// <summary>Highest the feet can get with a double jump pressed at the given height on the way up or down.</summary>
        public static float DoubleJumpApexFrom(ChaseTuning t, float heightAtPress) =>
            heightAtPress + Math.Max(0f, t.doubleJumpTotalHeight - t.jumpHeight);

        /// <summary>
        /// How long the double jump can be pressed and still put the feet above a ledge of the given height,
        /// assuming a full first jump. Zero means only a frame-perfect press (or nothing) gets there.
        /// </summary>
        public static float DoubleJumpWindowFor(ChaseTuning t, float ledgeHeight)
        {
            // Second jump adds a fixed rise, so the first jump must be at least this high when pressed.
            float needed = ledgeHeight - Math.Max(0f, t.doubleJumpTotalHeight - t.jumpHeight);
            if (needed <= 0f) return 2f * JumpVelocity(t) / Gravity(t);
            if (needed >= t.jumpHeight) return 0f;
            // Time spent above `needed` on a jump of height h is 2 * sqrt(2 (h - needed) / g).
            return 2f * (float)Math.Sqrt(2.0 * (t.jumpHeight - needed) / Gravity(t));
        }
    }
}
