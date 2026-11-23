using System.Globalization;
using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>Screen layout shared by the HUD and the input, in a virtual 720-pixel-high space.</summary>
    public static class HudLayout
    {
        public const float ReferenceHeight = 720f;

        public static float Scale => Mathf.Max(1, Screen.height) / ReferenceHeight;
        public static float Width => Screen.width / Scale;
        public static Rect PauseButton => new Rect(Width - 92f, 14f, 76f, 56f);

        /// <summary>Touches that start here belong to the HUD, not the kid. Takes screen pixels, origin bottom left.</summary>
        public static bool IsReserved(Vector2 screenPixels)
        {
            var gui = new Vector2(screenPixels.x / Scale, (Screen.height - screenPixels.y) / Scale);
            var pause = PauseButton;
            pause.xMin -= 12f;
            pause.yMax += 12f;
            return pause.Contains(gui);
        }
    }

    /// <summary>
    /// Grey-box HUD drawn with IMGUI so it needs no assets: gap bar with metres, rooster course progress,
    /// mango count, pause, the off-screen arrow, floating barks and the ready, pause and result screens.
    /// Holds no game logic; it only reads GameFlow and ChaseDirector. The uGUI signboard HUD replaces it in milestone 3.
    /// </summary>
    public sealed class GreyboxHud : MonoBehaviour
    {
        static readonly Color s_panel = new Color(0.12f, 0.08f, 0.05f, 0.75f);
        static readonly Color s_kid = new Color(0.15f, 0.45f, 0.85f);
        static readonly Color s_rooster = new Color(0.9f, 0.3f, 0.1f);
        static readonly Color s_close = new Color(0.3f, 0.8f, 0.3f);
        static readonly Color s_mid = new Color(0.95f, 0.75f, 0.2f);
        static readonly Color s_far = new Color(0.9f, 0.25f, 0.15f);
        static readonly Color s_mango = new Color(1f, 0.7f, 0.1f);

        [SerializeField] internal GameFlow flow;

        GUIStyle _label;
        GUIStyle _big;
        GUIStyle _small;
        GUIStyle _button;
        int _styleScreenHeight;
        float _fps;

        void Update()
        {
            if (Time.unscaledDeltaTime > 0f) _fps = Mathf.Lerp(_fps, 1f / Time.unscaledDeltaTime, 0.05f);
        }

        void OnGUI()
        {
            if (flow == null || !flow.isActiveAndEnabled || flow.Director == null || flow.Director.Tuning == null) return;
            EnsureStyles();
            float scale = HudLayout.Scale;
            GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1f));
            float width = HudLayout.Width;
            const float height = HudLayout.ReferenceHeight;

            var director = flow.Director;
            DrawBarks(scale);
            if (flow.State != FlowState.Ready)
            {
                DrawGapBar(director, width);
                DrawCounters(director);
                DrawEdgeArrow(director, width);
            }
            if (flow.State == FlowState.Chase) DrawPauseButton();

            switch (flow.State)
            {
                case FlowState.Ready:
                    DrawReady(width, height);
                    break;
                case FlowState.Result:
                    // In the full game the GameMenus draw the result with its buttons.
                    if (flow.TapToRetry) DrawResult(director, width, height);
                    break;
            }
            if (flow.Paused && flow.TapToRetry) DrawCentred(width, height * 0.34f, "Paused", "Tap to carry on");
            if (flow.State != FlowState.Ready && director.Feathers > 0) DrawFeathers(director);
            if (flow.ShowDebug) DrawDebug(director);
        }

        void DrawGapBar(ChaseDirector director, float width)
        {
            var t = director.Tuning;
            float gap = Mathf.Max(0f, director.Gap);
            var bar = new Rect(width * 0.5f - 250f, 18f, 500f, 30f);
            Fill(new Rect(bar.x - 6f, bar.y - 6f, bar.width + 12f, bar.height + 32f), s_panel);
            Fill(bar, new Color(0f, 0f, 0f, 0.35f));

            // The rooster sits at the right end; the kid's marker slides toward him as the gap closes.
            float closeness = 1f - Mathf.Clamp01(gap / t.escapeDistance);
            var fillColor = gap <= 5f ? s_close : gap <= t.tauntDistance ? s_mid : s_far;
            Fill(new Rect(bar.x, bar.y, bar.width * closeness, bar.height), fillColor);

            float tauntMark = bar.x + bar.width * (1f - t.tauntDistance / t.escapeDistance);
            Fill(new Rect(tauntMark - 1f, bar.y, 2f, bar.height), new Color(1f, 1f, 1f, 0.5f));

            Fill(new Rect(bar.x + bar.width * closeness - 7f, bar.y - 3f, 14f, bar.height + 6f), s_kid);
            Fill(new Rect(bar.xMax - 7f, bar.y - 3f, 14f, bar.height + 6f), s_rooster);
            Shadowed(bar, gap.ToString("0.0", CultureInfo.InvariantCulture) + " m", _label);

            // Thin line underneath: how far the rooster is from escaping off the end of the course.
            var course = new Rect(bar.x, bar.yMax + 8f, bar.width, 6f);
            Fill(course, new Color(0f, 0f, 0f, 0.35f));
            Fill(new Rect(course.x, course.y, course.width * director.RoosterProgress, course.height), s_rooster);
            Shadowed(new Rect(course.x, course.yMax, course.width, 18f), "course", _small);
        }

        void DrawCounters(ChaseDirector director)
        {
            var panel = new Rect(16f, 14f, 150f, 56f);
            Fill(panel, s_panel);
            Fill(new Rect(panel.x + 12f, panel.y + 16f, 24f, 24f), s_mango);
            Shadowed(new Rect(panel.x + 44f, panel.y, panel.width - 44f, panel.height),
                director.Mangoes.ToString(CultureInfo.InvariantCulture), _label, TextAnchor.MiddleLeft);
        }

        void DrawFeathers(ChaseDirector director)
        {
            // Feather pips under the mango count: one per hidden feather found this run.
            for (int i = 0; i < 3; i++)
            {
                bool found = (director.FeatherMask & (1 << i)) != 0;
                Fill(new Rect(28f + i * 26f, 80f, 18f, 30f), found ? s_rooster : new Color(1f, 1f, 1f, 0.2f));
            }
        }

        void DrawEdgeArrow(ChaseDirector director, float width)
        {
            if (flow.ChaseCamera == null || flow.ChaseCamera.IsRoosterVisible(out var viewport)) return;
            float y = Mathf.Clamp((1f - viewport.y) * HudLayout.ReferenceHeight, 120f, HudLayout.ReferenceHeight - 80f);
            var box = new Rect(width - 150f, y - 26f, 136f, 52f);
            Fill(box, s_panel);
            Shadowed(box, Mathf.Max(0f, director.Gap).ToString("0", CultureInfo.InvariantCulture) + " m  >>", _label);
        }

        void DrawBarks(float scale)
        {
            var cam = flow.ChaseCamera != null ? flow.ChaseCamera.Camera : null;
            if (cam == null) return;
            var barks = WorldBarks.Active;
            for (int i = 0; i < barks.Count; i++)
            {
                var bark = barks[i];
                var screen = cam.WorldToScreenPoint(bark.position);
                if (screen.z <= 0f) continue;
                var gui = new Vector2(screen.x / scale, (Screen.height - screen.y) / scale);
                float alpha = 1f - Mathf.Clamp01((bark.age - bark.lifetime * 0.6f) / (bark.lifetime * 0.4f));
                var color = bark.color;
                color.a = alpha;
                Shadowed(new Rect(gui.x - 160f, gui.y - 20f, 320f, 40f), bark.text, _label, TextAnchor.MiddleCenter, color);
            }
        }

        void DrawPauseButton()
        {
            if (GUI.Button(HudLayout.PauseButton, flow.Paused ? ">" : "II", _button)) flow.TogglePause();
        }

        void DrawReady(float width, float height)
        {
            // Above the kid and rooster, so the player sees who is chasing whom before the first tap.
            var level = flow.Level;
            if (level != null && !string.IsNullOrEmpty(level.Subtitle))
            {
                DrawCentred(width, height * 0.34f, level.DisplayName, level.Subtitle + "\nTap to chase!");
                return;
            }
            DrawCentred(width, height * 0.34f, "Tap to chase!",
                "Tap: jump (hold for higher)   Tap in the air: double jump   Swipe down: slide, or drop in the air\n"
                + "Keyboard: Space or Up to jump, Down or S to slide, R to retry, Esc to pause, F1 for debug");
        }

        void DrawResult(ChaseDirector director, float width, float height)
        {
            bool caught = director.Outcome == ChaseOutcome.Caught;
            string title = caught ? "Caught him!" : "He got away!";
            string detail;
            if (caught)
            {
                detail = "...and he wriggled free. " + director.Elapsed.ToString("0.0", CultureInfo.InvariantCulture) + " s, "
                    + director.Mangoes + " of " + director.MangoesPassed + " mangoes, "
                    + director.Stumbles + (director.Stumbles == 1 ? " stumble" : " stumbles");
            }
            else
            {
                detail = director.Outcome == ChaseOutcome.EscapedTooFar
                    ? "He got more than " + director.Tuning.escapeDistance.ToString("0", CultureInfo.InvariantCulture) + " m ahead."
                    : "He reached the end of the course before you grabbed him.";
            }

            var panel = new Rect(width * 0.5f - 330f, height * 0.5f - 150f, 660f, 300f);
            Fill(panel, s_panel);
            Shadowed(new Rect(panel.x, panel.y + 20f, panel.width, 70f), title, _big);
            Shadowed(new Rect(panel.x + 20f, panel.y + 90f, panel.width - 40f, 40f), detail, _small);

            var stars = director.Stars;
            DrawStar(new Rect(panel.x + 90f, panel.y + 145f, 150f, 70f), "Grab", stars.grab);
            DrawStar(new Rect(panel.x + 255f, panel.y + 145f, 150f, 70f), "Mangoes", stars.mangoes);
            DrawStar(new Rect(panel.x + 420f, panel.y + 145f, 150f, 70f), "No stumble", stars.clean);

            if (flow.CanDismissResult)
                Shadowed(new Rect(panel.x, panel.yMax - 60f, panel.width, 40f), caught ? "Tap to play again" : "Tap to retry", _label);
        }

        void DrawStar(Rect rect, string label, bool earned)
        {
            Fill(rect, earned ? s_mango : new Color(1f, 1f, 1f, 0.12f));
            Shadowed(rect, label, _label, TextAnchor.MiddleCenter, earned ? Color.white : new Color(1f, 1f, 1f, 0.5f));
        }

        void DrawCentred(float width, float centreY, string title, string detail)
        {
            var panel = new Rect(width * 0.5f - 420f, centreY - 90f, 840f, 180f);
            Fill(panel, s_panel);
            Shadowed(new Rect(panel.x, panel.y + 16f, panel.width, 80f), title, _big);
            Shadowed(new Rect(panel.x + 20f, panel.y + 96f, panel.width - 40f, 70f), detail, _small);
        }

        void DrawDebug(ChaseDirector director)
        {
            var kid = flow.Kid;
            var rooster = flow.Rooster;
            string text =
                "fps " + _fps.ToString("0") + "   state " + flow.State + "\n"
                + "kid " + kid.Pose + "  " + kid.CurrentSpeed.ToString("0.00") + " m/s  x " + kid.X.ToString("0.0")
                + (kid.IsStumbling ? "  STUMBLE" : "") + (kid.IsBoosted ? "  BOOST" : "") + "\n"
                + "rooster " + rooster.Act + "/" + rooster.Mood + "  " + rooster.Speed.ToString("0.00") + " m/s  x " + rooster.X.ToString("0.0")
                + "  taunts " + rooster.Taunts + "  panics " + rooster.PanicBursts + "\n"
                + "gap " + director.Gap.ToString("0.00") + " m  time " + director.Elapsed.ToString("0.0") + " s  stumbles "
                + director.Stumbles + " (" + director.MetresLost.ToString("0.0") + " m)  intensity " + director.Intensity.ToString("0.00");
            var rect = new Rect(16f, HudLayout.ReferenceHeight - 116f, 760f, 100f);
            Fill(rect, s_panel);
            GUI.Label(new Rect(rect.x + 10f, rect.y + 6f, rect.width - 20f, rect.height - 12f), text, _small);
        }

        static void Fill(Rect rect, Color color)
        {
            var previous = GUI.color;
            GUI.color = color;
            GUI.DrawTexture(rect, Texture2D.whiteTexture);
            GUI.color = previous;
        }

        static void Shadowed(Rect rect, string text, GUIStyle style, TextAnchor anchor = TextAnchor.MiddleCenter, Color? color = null)
        {
            var previous = GUI.color;
            var c = color ?? Color.white;
            style.alignment = anchor;
            GUI.color = new Color(0f, 0f, 0f, 0.6f * c.a);
            GUI.Label(new Rect(rect.x + 2f, rect.y + 2f, rect.width, rect.height), text, style);
            GUI.color = c;
            GUI.Label(rect, text, style);
            GUI.color = previous;
        }

        void EnsureStyles()
        {
            if (_label != null && _styleScreenHeight == Screen.height) return;
            _styleScreenHeight = Screen.height;
            _label = new GUIStyle(GUI.skin.label) { fontSize = 22, fontStyle = FontStyle.Bold, wordWrap = false };
            _label.normal.textColor = Color.white;
            _big = new GUIStyle(_label) { fontSize = 44, alignment = TextAnchor.MiddleCenter };
            _small = new GUIStyle(_label) { fontSize = 16, fontStyle = FontStyle.Normal, wordWrap = true };
            _button = new GUIStyle(GUI.skin.button) { fontSize = 26, fontStyle = FontStyle.Bold };
        }
    }
}
