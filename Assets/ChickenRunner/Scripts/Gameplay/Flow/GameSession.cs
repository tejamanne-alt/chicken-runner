using System;
using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    public enum GameScreen
    {
        Title,
        /// <summary>The wordless story strip, F2 to F6.</summary>
        Story,
        /// <summary>The village map: nine stops, stars and locks.</summary>
        Map,
        Chase,
        Result,
        /// <summary>After the last level: the rooster in Amma's kitchen (F8).</summary>
        Finale,
    }

    /// <summary>
    /// The whole game around the chase: title, story strip, village map, the nine levels, results and the finale.
    /// Owns the save (<see cref="Progress"/> over <see cref="SaveData"/>), loads levels into the <see cref="GameFlow"/>
    /// and the zone's scenery into the <see cref="BackdropStreamer"/>, and records every finished chase.
    /// The screens themselves are drawn by <see cref="GameMenus"/>, which only calls the methods here.
    /// </summary>
    [DefaultExecutionOrder(-200)]
    public sealed class GameSession : MonoBehaviour
    {
        [SerializeField] internal GameFlow flow;
        [SerializeField] internal BackdropStreamer backdrop;
        [Tooltip("The story levels in order, three per zone.")]
        [SerializeField] internal LevelDefinition[] levels = new LevelDefinition[StoryMap.LevelCount];
        [SerializeField] internal int storyPages = 5;
        [Tooltip("Editor testing: open every level and skip the title.")]
        [SerializeField] internal bool unlockAll;
        [Tooltip("Levels (zero-based) open from the start whatever the stars: the ones laid from audited plans, one per "
            + "zone, so each zone can be played straight away. The other levels keep the doc's star gates.")]
        [SerializeField] internal int[] openFromStart = new int[0];

        /// <summary>Set by the editor's Chicken Runner > Play Level menu: the level to start in, skipping the title.</summary>
        public const string PlayLevelKey = "ChickenRunner.PlayLevel";

        Progress _progress;

        public GameScreen Screen { get; private set; }
        public int LevelIndex { get; private set; }
        public int StoryPage { get; private set; }
        public LevelReport LastReport { get; private set; }
        public Progress Progress => _progress;
        public GameFlow Flow => flow;
        public int LevelCount => levels.Length;
        public LevelDefinition CurrentLevel => LevelAt(LevelIndex);
        public bool UnlockAll => unlockAll;

        /// <summary>The screen changed; the menus reset their per-screen state.</summary>
        public event Action<GameScreen> ScreenChanged;

        public LevelDefinition LevelAt(int index) => index >= 0 && index < levels.Length ? levels[index] : null;

        public bool IsLevelOpen(int index) =>
            LevelAt(index) != null && (unlockAll || IsOpenFromStart(index)
                || (index < StoryMap.LevelCount && _progress.IsLevelOpen(index)));

        public bool IsOpenFromStart(int index) => openFromStart != null && Array.IndexOf(openFromStart, index) >= 0;

        /// <summary>Whether any level of <paramref name="zone"/> is open whatever the stars.</summary>
        public bool ZoneHasOpenLevel(int zone)
        {
            int first = StoryMap.FirstLevelOf(zone);
            for (int i = 0; i < StoryMap.LevelsPerZone; i++)
            {
                if (IsOpenFromStart(first + i)) return true;
            }
            return false;
        }

        void Awake()
        {
            _progress = new Progress(SaveService.Load());
        }

        void Start()
        {
            if (flow == null)
            {
                Debug.LogError("GameSession needs its GameFlow. Run Chicken Runner > Build Game to regenerate the scene.", this);
                enabled = false;
                return;
            }
            flow.TapToRetry = false;
            flow.Finished += OnChaseFinished;
            // Chicken Runner > Play Level in the editor: straight into that level.
            int direct = Application.isEditor ? PlayerPrefs.GetInt(PlayLevelKey, -1) : -1;
            if (direct >= 0)
            {
                PlayerPrefs.DeleteKey(PlayLevelKey);
                if (LevelAt(direct) != null)
                {
                    StartLevel(direct, true);
                    return;
                }
            }
            if (unlockAll) ShowMap();
            else ShowTitle();
        }

        void OnDestroy()
        {
            if (flow != null) flow.Finished -= OnChaseFinished;
        }

        void OnApplicationPause(bool paused)
        {
            if (paused) Save();
        }

        public void ShowTitle() => Go(GameScreen.Title);

        /// <summary>Play from the title: the story strip the first time, the map after that.</summary>
        public void Play()
        {
            if (!_progress.Data.storySeen) ShowStory();
            else ShowMap();
        }

        public void ShowStory()
        {
            StoryPage = 0;
            Go(GameScreen.Story);
        }

        /// <summary>Next story page; after the last, a new player goes straight into level 1.</summary>
        public void NextStoryPage()
        {
            if (++StoryPage < storyPages) return;
            bool first = !_progress.Data.storySeen;
            _progress.Data.storySeen = true;
            Save();
            if (first) StartLevel(0);
            else ShowMap();
        }

        public void SkipStory()
        {
            StoryPage = storyPages - 1;
            NextStoryPage();
        }

        public void ShowMap() => Go(GameScreen.Map);

        public void StartLevel(int index) => StartLevel(index, false);

        void StartLevel(int index, bool evenIfLocked)
        {
            var level = LevelAt(index);
            if (level == null || (!evenIfLocked && !IsLevelOpen(index))) return;
            LevelIndex = index;
            if (backdrop != null && level.Art != null) backdrop.Show(level.Art);
            Go(GameScreen.Chase);
            flow.LoadLevel(level);
        }

        public void Retry()
        {
            if (Screen != GameScreen.Result && Screen != GameScreen.Chase) return;
            Go(GameScreen.Chase);
            flow.Retry();
        }

        /// <summary>From a won result: the finale after the last level, else the next open level, else the map.</summary>
        public void Next()
        {
            if (LevelIndex == StoryMap.LevelCount - 1 && LastReport.stars.grab)
            {
                Go(GameScreen.Finale);
                return;
            }
            int next = LastReport.nextLevel;
            if (next < 0 && unlockAll && LevelIndex + 1 < levels.Length) next = LevelIndex + 1;
            if (next >= 0) StartLevel(next);
            else ShowMap();
        }

        public void FinishFinale()
        {
            _progress.Data.finaleSeen = true;
            Save();
            ShowMap();
        }

        public void ResetProgress()
        {
            SaveService.Delete();
            _progress = new Progress();
            ShowTitle();
        }

        public void SetSound(bool on)
        {
            _progress.Data.soundOn = on;
            AudioListener.volume = on ? 1f : 0f;
            Save();
        }

        void OnChaseFinished()
        {
            var director = flow.Director;
            if (LevelIndex < StoryMap.LevelCount)
                LastReport = _progress.Record(LevelIndex, director.Stars, director.Mangoes, director.FeatherMask);
            Save();
            Go(GameScreen.Result);
        }

        void Go(GameScreen screen)
        {
            Screen = screen;
            // The chase only runs on its own screens; elsewhere the world stands still behind the menus.
            bool chasing = screen == GameScreen.Chase || screen == GameScreen.Result;
            if (flow.enabled != chasing) flow.enabled = chasing;
            AudioListener.volume = _progress.Data.soundOn ? 1f : 0f;
            ScreenChanged?.Invoke(screen);
        }

        void Save() => SaveService.Save(_progress.Data);
    }
}
