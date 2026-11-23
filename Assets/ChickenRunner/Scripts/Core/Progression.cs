using System;

namespace ChickenRunner.Core
{
    /// <summary>
    /// The story's nine levels, three to a zone, and the stars that open each zone (design doc, Progression):
    /// 5 of zone 1's 9 stars open the fields, 12 of the first 18 open the terraces. Levels are numbered from 0 here
    /// and shown to players from 1.
    /// </summary>
    public static class StoryMap
    {
        public const int LevelCount = 9;
        public const int ZoneCount = 3;
        public const int LevelsPerZone = 3;
        public const int StarsPerLevel = 3;

        public static int ZoneOf(int level)
        {
            CheckLevel(level);
            return level / LevelsPerZone + 1;
        }

        public static int FirstLevelOf(int zone)
        {
            CheckZone(zone);
            return (zone - 1) * LevelsPerZone;
        }

        /// <summary>Stars needed from the earlier zones' levels before this zone opens.</summary>
        public static int StarsToOpen(int zone)
        {
            CheckZone(zone);
            switch (zone)
            {
                case 2: return 5;
                case 3: return 12;
                default: return 0;
            }
        }

        internal static void CheckLevel(int level)
        {
            if (level < 0 || level >= LevelCount)
                throw new ArgumentOutOfRangeException(nameof(level), level, "Story levels are 0 to " + (LevelCount - 1));
        }

        internal static void CheckZone(int zone)
        {
            if (zone < 1 || zone > ZoneCount)
                throw new ArgumentOutOfRangeException(nameof(zone), zone, "Zones are 1 to " + ZoneCount);
        }
    }

    /// <summary>
    /// Everything the game remembers between sessions, as plain fields so Unity's JsonUtility can write it.
    /// Stars are kept star by star: each level's best ever grab, mango and no-stumble stars, earned in any runs.
    /// </summary>
    [Serializable]
    public sealed class SaveData
    {
        public const int CurrentVersion = 1;

        public int version = CurrentVersion;
        /// <summary>Per level: bit 0 the grab star, bit 1 the mango star, bit 2 the no-stumble star.</summary>
        public int[] stars = new int[StoryMap.LevelCount];
        /// <summary>Per level: the most mangoes taken in one run.</summary>
        public int[] bestMangoes = new int[StoryMap.LevelCount];
        /// <summary>Per level: a bit for each hidden tail feather found.</summary>
        public int[] feathers = new int[StoryMap.LevelCount];
        /// <summary>Mangoes banked from every run, to spend on outfits.</summary>
        public int mangoes;
        public bool storySeen;
        public bool finaleSeen;
        public int lastLevel;
        public bool soundOn = true;

        /// <summary>Puts an older, newer or damaged save back into shape: right-sized arrays, nothing negative.</summary>
        public void Repair()
        {
            stars = Resize(stars, 0b111);
            bestMangoes = Resize(bestMangoes, int.MaxValue);
            feathers = Resize(feathers, int.MaxValue);
            mangoes = Math.Max(0, mangoes);
            if (lastLevel < 0 || lastLevel >= StoryMap.LevelCount) lastLevel = 0;
            version = CurrentVersion;
        }

        static int[] Resize(int[] values, int mask)
        {
            var result = new int[StoryMap.LevelCount];
            if (values == null) return result;
            for (int i = 0; i < result.Length && i < values.Length; i++)
                result[i] = Math.Max(0, values[i]) & mask;
            return result;
        }
    }

    /// <summary>What one finished run changed, for the result screen.</summary>
    public struct LevelReport
    {
        public int level;
        public StarResult stars;
        /// <summary>Stars this run earned that the level did not have before.</summary>
        public int newStars;
        public int mangoes;
        public int newFeathers;
        /// <summary>The first time this level was won.</summary>
        public bool firstWin;
        /// <summary>The zone this run opened (2 or 3), or 0.</summary>
        public int zoneOpened;
        /// <summary>The level to offer next, or -1 when there is none open.</summary>
        public int nextLevel;
    }

    /// <summary>The rules over <see cref="SaveData"/>: which levels are open, totals, and recording a run.</summary>
    public sealed class Progress
    {
        const int GrabBit = 1;
        const int MangoBit = 2;
        const int CleanBit = 4;

        public Progress(SaveData data = null)
        {
            Data = data ?? new SaveData();
            Data.Repair();
        }

        public SaveData Data { get; }
        public int Mangoes => Data.mangoes;

        public StarResult StarsOf(int level)
        {
            StoryMap.CheckLevel(level);
            int bits = Data.stars[level];
            return new StarResult { grab = (bits & GrabBit) != 0, mangoes = (bits & MangoBit) != 0, clean = (bits & CleanBit) != 0 };
        }

        public int StarCount(int level) => StarsOf(level).Count;

        public bool IsWon(int level) => StarsOf(level).grab;

        public int TotalStars
        {
            get
            {
                int total = 0;
                for (int i = 0; i < StoryMap.LevelCount; i++) total += StarCount(i);
                return total;
            }
        }

        /// <summary>Stars from the levels of the zones before <paramref name="zone"/>.</summary>
        public int StarsBefore(int zone)
        {
            int total = 0;
            for (int i = 0; i < StoryMap.FirstLevelOf(zone); i++) total += StarCount(i);
            return total;
        }

        public bool IsZoneOpen(int zone) => StarsBefore(zone) >= StoryMap.StarsToOpen(zone);

        /// <summary>The first level is always open; each later one once the level before is won and its zone is open.</summary>
        public bool IsLevelOpen(int level)
        {
            StoryMap.CheckLevel(level);
            return level == 0 || (IsWon(level - 1) && IsZoneOpen(StoryMap.ZoneOf(level)));
        }

        public int FeathersFound(int level)
        {
            StoryMap.CheckLevel(level);
            return CountBits(Data.feathers[level]);
        }

        public int TotalFeathers
        {
            get
            {
                int total = 0;
                for (int i = 0; i < StoryMap.LevelCount; i++) total += FeathersFound(i);
                return total;
            }
        }

        /// <summary>The level after this one if it is open, else -1.</summary>
        public int NextOpenLevel(int level)
        {
            StoryMap.CheckLevel(level);
            int next = level + 1;
            return next < StoryMap.LevelCount && IsLevelOpen(next) ? next : -1;
        }

        /// <summary>The level the map should point at: the first open level not yet won, else the last one played.</summary>
        public int SuggestedLevel()
        {
            for (int i = 0; i < StoryMap.LevelCount; i++)
            {
                if (IsLevelOpen(i) && !IsWon(i)) return i;
            }
            return Data.lastLevel;
        }

        /// <summary>
        /// Records a finished run, won or lost. Stars only come with a win (ChaseRules gives none for a loss); the
        /// mangoes taken are banked either way, and so are the feathers found, each feather once.
        /// </summary>
        public LevelReport Record(int level, StarResult stars, int mangoesCollected, int featherMask = 0)
        {
            StoryMap.CheckLevel(level);
            if (mangoesCollected < 0) throw new ArgumentOutOfRangeException(nameof(mangoesCollected));

            bool wasWon = IsWon(level);
            bool[] zoneWasOpen = new bool[StoryMap.ZoneCount + 1];
            for (int zone = 1; zone <= StoryMap.ZoneCount; zone++) zoneWasOpen[zone] = IsZoneOpen(zone);

            int before = Data.stars[level];
            int earned = (stars.grab ? GrabBit : 0) | (stars.mangoes ? MangoBit : 0) | (stars.clean ? CleanBit : 0);
            Data.stars[level] = before | earned;

            int feathersBefore = Data.feathers[level];
            Data.feathers[level] = feathersBefore | Math.Max(0, featherMask);

            Data.bestMangoes[level] = Math.Max(Data.bestMangoes[level], mangoesCollected);
            Data.mangoes += mangoesCollected;
            Data.lastLevel = level;

            var report = new LevelReport
            {
                level = level,
                stars = stars,
                newStars = CountBits(Data.stars[level]) - CountBits(before),
                mangoes = mangoesCollected,
                newFeathers = CountBits(Data.feathers[level]) - CountBits(feathersBefore),
                firstWin = stars.grab && !wasWon,
            };
            for (int zone = 2; zone <= StoryMap.ZoneCount; zone++)
            {
                if (!zoneWasOpen[zone] && IsZoneOpen(zone)) report.zoneOpened = zone;
            }
            report.nextLevel = NextOpenLevel(level);
            return report;
        }

        /// <summary>Spends banked mangoes (outfits); false and nothing spent if there are not enough.</summary>
        public bool Spend(int mangoes)
        {
            if (mangoes < 0) throw new ArgumentOutOfRangeException(nameof(mangoes));
            if (Data.mangoes < mangoes) return false;
            Data.mangoes -= mangoes;
            return true;
        }

        static int CountBits(int value)
        {
            int count = 0;
            for (uint v = (uint)value; v != 0; v &= v - 1) count++;
            return count;
        }
    }
}
