using System.Globalization;
using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// The screens around the chase, drawn with IMGUI over the painted art so they need no UI assets yet:
    /// title (F1), the wordless story strip (F2-F6), the village map with its nine stops, the result with Next, Retry
    /// and Map, the rooster-escaped picture (F7) and the finale (F8). Holds no rules: it reads the GameSession and
    /// Progress and calls the session's methods. The signboard UI of milestone 3 can replace it screen by screen.
    /// </summary>
    public sealed class GameMenus : MonoBehaviour
    {
        static readonly Color s_panel = new Color(0.12f, 0.08f, 0.05f, 0.82f);
        static readonly Color s_shade = new Color(0f, 0f, 0f, 0.45f);
        static readonly Color s_mango = new Color(1f, 0.7f, 0.1f);
        static readonly Color s_kumkum = new Color(0.85f, 0.12f, 0.3f);
        static readonly Color s_locked = new Color(0.25f, 0.22f, 0.2f, 0.85f);
        static readonly Color s_open = new Color(0.98f, 0.93f, 0.82f, 0.95f);
        static readonly Color s_ink = new Color(0.22f, 0.12f, 0.06f);
        static readonly string[] s_zoneNames = { "The lane", "Fields and canal", "Terraces and market" };

        [SerializeField] internal GameSession session;

        [Header("Painted screens")]
        [SerializeField] internal Texture2D title;
        [Tooltip("F2 to F6, in order.")]
        [SerializeField] internal Texture2D[] story = new Texture2D[0];
        [SerializeField] internal Texture2D won;
        [SerializeField] internal Texture2D escaped;
        [SerializeField] internal Texture2D finale;
        [Tooltip("A mood painting per zone for the map: lane, fields, market.")]
        [SerializeField] internal Texture2D[] zones = new Texture2D[3];

        GUIStyle _label;
        GUIStyle _big;
        GUIStyle _small;
        GUIStyle _dark;
        GUIStyle _pale;
        GUIStyle _button;
        int _styleHeight;
        bool _confirmReset;

        void OnEnable()
        {
            if (session != null) session.ScreenChanged += OnScreenChanged;
        }

        void OnDisable()
        {
            if (session != null) session.ScreenChanged -= OnScreenChanged;
        }

        void OnScreenChanged(GameScreen screen) => _confirmReset = false;

        void OnGUI()
        {
            if (session == null || session.Progress == null) return;
            EnsureStyles();
            float scale = HudLayout.Scale;
            GUI.matrix = Matrix4x4.Scale(new Vector3(scale, scale, 1f));
            float w = HudLayout.Width;
            const float h = HudLayout.ReferenceHeight;

            switch (session.Screen)
            {
                case GameScreen.Title:
                    DrawTitle(w, h);
                    break;
                case GameScreen.Story:
                    DrawStory(w, h);
                    break;
                case GameScreen.Map:
                    DrawMap(w, h);
                    break;
                case GameScreen.Chase:
                    DrawPauseExtras(w, h);
                    break;
                case GameScreen.Result:
                    DrawResult(w, h);
                    break;
                case GameScreen.Finale:
                    DrawFinale(w, h);
                    break;
            }
        }

        // ------------------------------------------------------------------ title

        void DrawTitle(float w, float h)
        {
            Picture(new Rect(0f, 0f, w, h), title, ScaleMode.ScaleAndCrop, new Color(0.95f, 0.7f, 0.4f));
            if (title == null) Shadowed(new Rect(0f, h * 0.2f, w, 120f), "Chicken Runner", _big);

            if (GUI.Button(new Rect(w * 0.5f - 150f, h - 170f, 300f, 92f), "Play", _button)) session.Play();

            var progress = session.Progress;
            if (GUI.Button(new Rect(24f, h - 84f, 170f, 60f), "Story", _button)) session.ShowStory();
            if (GUI.Button(new Rect(206f, h - 84f, 200f, 60f), progress.Data.soundOn ? "Sound: on" : "Sound: off", _button))
                session.SetSound(!progress.Data.soundOn);
            string reset = _confirmReset ? "Tap again to erase" : "Reset";
            if (GUI.Button(new Rect(w - 264f, h - 84f, 240f, 60f), reset, _button))
            {
                if (_confirmReset) session.ResetProgress();
                else _confirmReset = true;
            }
        }

        // ------------------------------------------------------------------ story strip

        void DrawStory(float w, float h)
        {
            Fill(new Rect(0f, 0f, w, h), new Color(0.08f, 0.05f, 0.03f));
            int page = session.StoryPage;
            var art = story != null && page < story.Length ? story[page] : null;
            Picture(new Rect(0f, 0f, w, h - 40f), art, ScaleMode.ScaleToFit, new Color(0.3f, 0.2f, 0.12f));

            int pages = Mathf.Max(1, story != null ? story.Length : 0);
            for (int i = 0; i < pages; i++)
                Fill(new Rect(w * 0.5f + (i - pages * 0.5f) * 28f, h - 26f, 16f, 10f), i == page ? s_mango : new Color(1f, 1f, 1f, 0.3f));

            if (GUI.Button(new Rect(w - 160f, 16f, 140f, 56f), "Skip", _button))
            {
                session.SkipStory();
                return;
            }
            // Anywhere else on the picture turns the page.
            if (GUI.Button(new Rect(0f, 80f, w, h - 80f), GUIContent.none, GUIStyle.none)) session.NextStoryPage();
        }

        // ------------------------------------------------------------------ village map

        void DrawMap(float w, float h)
        {
            var progress = session.Progress;
            Fill(new Rect(0f, 0f, w, h), new Color(0.55f, 0.36f, 0.2f));

            // Top bar: totals and the way back to the title.
            Fill(new Rect(0f, 0f, w, 72f), s_panel);
            Shadowed(new Rect(24f, 0f, 400f, 72f), "Village map", _big, TextAnchor.MiddleLeft);
            string totals = "Stars " + progress.TotalStars + " / " + StoryMap.LevelCount * StoryMap.StarsPerLevel
                + "     Mangoes " + progress.Mangoes.ToString(CultureInfo.InvariantCulture)
                + "     Feathers " + progress.TotalFeathers + " / " + StoryMap.LevelCount * 3;
            Shadowed(new Rect(w * 0.5f - 330f, 0f, 660f, 72f), totals, _label);
            if (GUI.Button(new Rect(w - 160f, 8f, 140f, 56f), "Title", _button)) session.ShowTitle();

            const float gap = 18f;
            float top = 90f;
            float panelW = (w - gap * 4f) / 3f;
            float panelH = h - top - gap;
            int suggested = progress.SuggestedLevel();
            for (int zone = 1; zone <= StoryMap.ZoneCount; zone++)
            {
                var panel = new Rect(gap + (zone - 1) * (panelW + gap), top, panelW, panelH);
                DrawZone(panel, zone, suggested);
            }
        }

        void DrawZone(Rect panel, int zone, int suggested)
        {
            var progress = session.Progress;
            bool open = session.UnlockAll || progress.IsZoneOpen(zone);
            bool someOpen = open || session.ZoneHasOpenLevel(zone);
            var art = zones != null && zone - 1 < zones.Length ? zones[zone - 1] : null;
            Picture(panel, art, ScaleMode.ScaleAndCrop, new Color(0.4f, 0.55f, 0.3f));
            Fill(new Rect(panel.x, panel.y, panel.width, 64f), s_shade);
            Shadowed(new Rect(panel.x, panel.y, panel.width, 64f), zone + ". " + s_zoneNames[zone - 1], _label);

            int first = StoryMap.FirstLevelOf(zone);
            var stops = new Vector2[StoryMap.LevelsPerZone];
            for (int i = 0; i < stops.Length; i++)
            {
                // A winding footpath: the stops zig-zag down the panel.
                float x = panel.x + panel.width * (i % 2 == 0 ? 0.36f : 0.64f);
                float y = panel.y + 120f + i * (panel.height - 190f) / (stops.Length - 1);
                stops[i] = new Vector2(x, y);
            }
            for (int i = 0; i + 1 < stops.Length; i++) DottedPath(stops[i], stops[i + 1]);

            for (int i = 0; i < stops.Length; i++)
            {
                int level = first + i;
                var def = session.LevelAt(level);
                bool levelOpen = session.IsLevelOpen(level);
                var rect = new Rect(stops[i].x - 120f, stops[i].y - 46f, 240f, 92f);
                if (level == suggested && levelOpen)
                {
                    float pulse = 4f + 3f * Mathf.Sin(Time.unscaledTime * 5f);
                    Fill(new Rect(rect.x - pulse, rect.y - pulse, rect.width + pulse * 2f, rect.height + pulse * 2f), s_mango);
                }
                Fill(rect, levelOpen ? s_open : s_locked);
                string name = def != null ? def.DisplayName : "Level " + (level + 1);
                GUI.Label(new Rect(rect.x + 10f, rect.y + 4f, rect.width - 20f, 34f), (level + 1) + ". " + name, levelOpen ? _dark : _pale);
                if (levelOpen) DrawStarPips(new Rect(rect.x + 10f, rect.y + 50f, rect.width - 20f, 28f), progress.StarsOf(level), progress.FeathersFound(level));
                else GUI.Label(new Rect(rect.x + 10f, rect.y + 44f, rect.width - 20f, 40f), "locked", _small);
                if (levelOpen && GUI.Button(rect, GUIContent.none, GUIStyle.none)) session.StartLevel(level);
            }

            if (!open)
            {
                Fill(new Rect(panel.x, panel.yMax - 92f, panel.width, 92f), s_panel);
                int need = StoryMap.StarsToOpen(zone) - progress.StarsBefore(zone);
                // A zone whose first level is open from the start says its other levels open with the stars.
                Shadowed(new Rect(panel.x + 10f, panel.yMax - 92f, panel.width - 20f, 92f),
                    (someOpen ? "Its other levels open with " : "Opens with ") + StoryMap.StarsToOpen(zone)
                    + " stars from the earlier zones (" + need + " more)", _small);
            }
        }

        void DrawStarPips(Rect rect, StarResult stars, int feathers)
        {
            bool[] earned = { stars.grab, stars.mangoes, stars.clean };
            for (int i = 0; i < 3; i++)
                Fill(new Rect(rect.x + i * 34f, rect.y, 26f, 26f), earned[i] ? s_mango : new Color(0f, 0f, 0f, 0.15f));
            for (int i = 0; i < 3; i++)
                Fill(new Rect(rect.xMax - 66f + i * 22f, rect.y + 2f, 12f, 22f), i < feathers ? s_kumkum : new Color(0f, 0f, 0f, 0.12f));
        }

        static void DottedPath(Vector2 from, Vector2 to)
        {
            float length = Vector2.Distance(from, to);
            int dots = Mathf.Max(2, Mathf.FloorToInt(length / 22f));
            for (int i = 1; i < dots; i++)
            {
                var p = Vector2.Lerp(from, to, i / (float)dots);
                Fill(new Rect(p.x - 5f, p.y - 5f, 10f, 10f), new Color(0.98f, 0.9f, 0.7f, 0.9f));
            }
        }

        // ------------------------------------------------------------------ chase extras

        void DrawPauseExtras(float w, float h)
        {
            var flow = session.Flow;
            if (flow == null || !flow.Paused) return;
            var panel = new Rect(w * 0.5f - 300f, h * 0.5f - 150f, 600f, 300f);
            Fill(panel, s_panel);
            var level = session.CurrentLevel;
            Shadowed(new Rect(panel.x, panel.y + 20f, panel.width, 64f), "Paused", _big);
            if (level != null) Shadowed(new Rect(panel.x, panel.y + 84f, panel.width, 40f), (session.LevelIndex + 1) + ". " + level.DisplayName, _label);
            if (GUI.Button(new Rect(panel.x + 40f, panel.yMax - 112f, 250f, 80f), "Carry on", _button)) flow.SetPaused(false);
            if (GUI.Button(new Rect(panel.xMax - 290f, panel.yMax - 112f, 250f, 80f), "Village map", _button)) session.ShowMap();
        }

        // ------------------------------------------------------------------ result

        void DrawResult(float w, float h)
        {
            var flow = session.Flow;
            var director = flow.Director;
            var report = session.LastReport;
            bool caught = director.Outcome == ChaseOutcome.Caught;

            Fill(new Rect(0f, 0f, w, h), new Color(0f, 0f, 0f, 0.35f));
            var panel = new Rect(w * 0.5f - 470f, h * 0.5f - 230f, 940f, 460f);
            Fill(panel, s_panel);
            var art = new Rect(panel.x + 20f, panel.y + 20f, 360f, panel.height - 40f);
            Picture(art, caught ? won : escaped, ScaleMode.ScaleAndCrop, new Color(0.35f, 0.25f, 0.15f));

            float x = art.xMax + 24f;
            float right = panel.xMax - 24f;
            Shadowed(new Rect(x, panel.y + 20f, right - x, 64f), caught ? "Caught him!" : "He got away!", _big, TextAnchor.MiddleLeft);
            string detail;
            if (caught)
            {
                detail = "...and he wriggled free. " + director.Elapsed.ToString("0.0", CultureInfo.InvariantCulture) + " s, "
                    + director.Stumbles + (director.Stumbles == 1 ? " stumble" : " stumbles");
            }
            else
            {
                detail = director.Outcome == ChaseOutcome.EscapedTooFar
                    ? "He got more than " + director.Tuning.escapeDistance.ToString("0", CultureInfo.InvariantCulture) + " m ahead."
                    : "He reached the end of the course first.";
            }
            GUI.Label(new Rect(x, panel.y + 88f, right - x, 50f), detail, _small);

            var stars = director.Stars;
            float starW = (right - x - 24f) / 3f;
            DrawStar(new Rect(x, panel.y + 146f, starW, 64f), "Grab", stars.grab);
            DrawStar(new Rect(x + starW + 12f, panel.y + 146f, starW, 64f), "Mangoes", stars.mangoes);
            DrawStar(new Rect(x + (starW + 12f) * 2f, panel.y + 146f, starW, 64f), "No stumble", stars.clean);

            string line = "+" + director.Mangoes + " mangoes (" + director.Mangoes + " of " + director.MangoesPassed + ")";
            if (report.newStars > 0) line += "     " + report.newStars + (report.newStars == 1 ? " new star" : " new stars");
            if (report.newFeathers > 0) line += "     " + report.newFeathers + (report.newFeathers == 1 ? " feather found" : " feathers found");
            GUI.Label(new Rect(x, panel.y + 222f, right - x, 40f), line, _small);
            if (report.zoneOpened > 0)
                Shadowed(new Rect(x, panel.y + 262f, right - x, 40f), s_zoneNames[report.zoneOpened - 1] + " is open!", _label, TextAnchor.MiddleLeft, s_mango);

            if (!flow.CanDismissResult) return;
            float by = panel.yMax - 96f;
            if (caught)
            {
                bool last = session.LevelIndex == StoryMap.LevelCount - 1;
                if (GUI.Button(new Rect(x, by, 200f, 72f), last ? "Home!" : "Next", _button)) session.Next();
                if (GUI.Button(new Rect(x + 214f, by, 180f, 72f), "Again", _button)) session.Retry();
            }
            else if (GUI.Button(new Rect(x, by, 220f, 72f), "Retry", _button))
            {
                session.Retry();
            }
            if (GUI.Button(new Rect(right - 160f, by, 160f, 72f), "Map", _button)) session.ShowMap();
        }

        void DrawStar(Rect rect, string label, bool earned)
        {
            Fill(rect, earned ? s_mango : new Color(1f, 1f, 1f, 0.12f));
            Shadowed(rect, label, _label, TextAnchor.MiddleCenter, earned ? Color.white : new Color(1f, 1f, 1f, 0.5f));
        }

        // ------------------------------------------------------------------ finale

        void DrawFinale(float w, float h)
        {
            Picture(new Rect(0f, 0f, w, h), finale, ScaleMode.ScaleAndCrop, new Color(0.5f, 0.3f, 0.15f));
            Fill(new Rect(0f, h - 120f, w, 120f), s_shade);
            Shadowed(new Rect(0f, h - 120f, w, 70f), "Home at last, rooster and all.", _big);
            Shadowed(new Rect(0f, h - 56f, w, 40f), "Tap to go back to the village", _small);
            if (GUI.Button(new Rect(0f, 0f, w, h), GUIContent.none, GUIStyle.none)) session.FinishFinale();
        }

        // ------------------------------------------------------------------ helpers

        /// <summary>Draws the art, or a flat colour while that picture has not been made yet.</summary>
        static void Picture(Rect rect, Texture2D art, ScaleMode mode, Color missing)
        {
            if (art == null)
            {
                Fill(rect, missing);
                return;
            }
            GUI.DrawTexture(rect, art, mode, true);
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
            if (_label != null && _styleHeight == Screen.height) return;
            _styleHeight = Screen.height;
            _label = new GUIStyle(GUI.skin.label) { fontSize = 24, fontStyle = FontStyle.Bold, wordWrap = false };
            _label.normal.textColor = Color.white;
            _big = new GUIStyle(_label) { fontSize = 44, alignment = TextAnchor.MiddleCenter };
            _small = new GUIStyle(_label) { fontSize = 19, fontStyle = FontStyle.Normal, wordWrap = true };
            _dark = new GUIStyle(_label) { fontSize = 21, wordWrap = false, clipping = TextClipping.Clip };
            _dark.normal.textColor = s_ink;
            _pale = new GUIStyle(_dark);
            _pale.normal.textColor = new Color(1f, 1f, 1f, 0.75f);
            _button = new GUIStyle(GUI.skin.button) { fontSize = 30, fontStyle = FontStyle.Bold };
        }
    }
}
