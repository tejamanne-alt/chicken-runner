using System;
using System.Collections.Generic;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    internal static partial class GameBuilder
    {
        /// <summary>A chunk design: its prefab name and how to build it.</summary>
        sealed class ChunkDesign
        {
            public string name;
            public Func<ZoneKit, GameObject> build;

            public ChunkDesign(string name, Func<ZoneKit, GameObject> build)
            {
                this.name = name;
                this.build = build;
            }
        }

        /// <summary>One story level: what it is called, its zone, its chunks in first-pass order.</summary>
        sealed class LevelDesign
        {
            public string title;
            public string subtitle;
            public int zone;
            public int seed;
            public float courseLength;
            public string[] chunks;
        }

        // Every level holds at least one chunk with each of its three hidden feathers (index 0, 1 and 2), on the
        // harder routes: high above a jump, on a roof, a branch or a bounce. A chunk that appears twice gives the same
        // feather again, which counts once.
        static readonly LevelDesign[] s_levels =
        {
            new LevelDesign { title = "Pots and the sleeping dog", subtitle = "Tap to jump. Hold for higher.", zone = 1, seed = 11,
                chunks = new[] { "Pots", "DungAndDog", "Puddle", "Cart" } },
            new LevelDesign { title = "Washing day", subtitle = "Swipe down to slide. Bounce on the cot.", zone = 1, seed = 12,
                chunks = new[] { "Clotheslines", "CotBounce", "DungAndDog", "ClothesAndPots", "Cart", "Mischief" } },
            new LevelDesign { title = "Up on the roofs", subtitle = "Ladders, roofs and the jump between them.", zone = 1, seed = 13,
                chunks = new[] { "Houses", "Clotheslines", "CotBounce", "RoofHop", "Cart", "Mischief", "DungAndDog" } },
            new LevelDesign { title = "The canal", subtitle = "Jump it, wade it, or take the plank.", zone = 2, seed = 21,
                chunks = new[] { "Canal", "BridgeCanal", "FieldDung", "WideCanal", "FieldCart", "SmallHaystacks" } },
            new LevelDesign { title = "Mango trees", subtitle = "Jump at a branch to climb up for mangoes.", zone = 2, seed = 22,
                chunks = new[] { "MangoBranch", "SmallHaystacks", "Canal", "BridgeCanal", "FieldDung", "FieldCart" } },
            new LevelDesign { title = "Buffalo and haystacks", subtitle = "Bounce off a buffalo's back.", zone = 2, seed = 23,
                chunks = new[] { "Buffalo", "HaystackChain", "FieldMischief", "WideCanal", "MangoBranch" } },
            new LevelDesign { title = "Rooftop run", subtitle = "Mind the gaps and the water tanks.", zone = 3, seed = 31,
                chunks = new[] { "RoofRun", "MarketPots", "RoofTanks", "MarketClotheslines" } },
            new LevelDesign { title = "Market day", subtitle = "Bounce across the awnings.", zone = 3, seed = 32,
                chunks = new[] { "Awnings", "Hens", "AwningsLong", "HensBaskets", "MarketMischief" } },
            new LevelDesign { title = "The temple steps", subtitle = "Everything at once. Catch him for good!", zone = 3, seed = 33, courseLength = 800f,
                chunks = new[] { "TempleSteps", "Awnings", "RoofRun", "Hens", "MarketClotheslines", "MarketPots", "MarketMischief" } },
        };

        static readonly string[] s_fronts = { "house_indigo_veranda", "house_pink", "house_limewash" };

        /// <summary>The chunks of a zone, by name; plus its runway under "Runway".</summary>
        static List<ChunkDesign> ChunkDesigns(int zone)
        {
            var list = new List<ChunkDesign> { new ChunkDesign("Runway", Runway) };
            switch (zone)
            {
                case 1:
                    list.Add(new ChunkDesign("Pots", Pots));
                    list.Add(new ChunkDesign("DungAndDog", DungAndDog));
                    list.Add(new ChunkDesign("Puddle", Puddle));
                    list.Add(new ChunkDesign("Clotheslines", Clotheslines));
                    list.Add(new ChunkDesign("CotBounce", CotBounce));
                    list.Add(new ChunkDesign("Cart", Cart));
                    list.Add(new ChunkDesign("Mischief", Mischief));
                    list.Add(new ChunkDesign("ClothesAndPots", ClothesAndPots));
                    list.Add(new ChunkDesign("Houses", Houses));
                    list.Add(new ChunkDesign("RoofHop", RoofHop));
                    break;
                case 2:
                    list.Add(new ChunkDesign("Canal", Canal));
                    list.Add(new ChunkDesign("BridgeCanal", BridgeCanal));
                    list.Add(new ChunkDesign("WideCanal", WideCanal));
                    list.Add(new ChunkDesign("FieldDung", FieldDung));
                    list.Add(new ChunkDesign("FieldCart", FieldCart));
                    list.Add(new ChunkDesign("SmallHaystacks", SmallHaystacks));
                    list.Add(new ChunkDesign("HaystackChain", HaystackChain));
                    list.Add(new ChunkDesign("MangoBranch", MangoBranch));
                    list.Add(new ChunkDesign("Buffalo", Buffalo));
                    list.Add(new ChunkDesign("FieldMischief", FieldMischief));
                    break;
                case 3:
                    list.Add(new ChunkDesign("RoofRun", RoofRun));
                    list.Add(new ChunkDesign("RoofTanks", RoofTanks));
                    list.Add(new ChunkDesign("MarketClotheslines", MarketClotheslines));
                    list.Add(new ChunkDesign("MarketPots", MarketPots));
                    list.Add(new ChunkDesign("Awnings", Awnings));
                    list.Add(new ChunkDesign("AwningsLong", AwningsLong));
                    list.Add(new ChunkDesign("Hens", Hens));
                    list.Add(new ChunkDesign("HensBaskets", HensBaskets));
                    list.Add(new ChunkDesign("MarketMischief", MarketMischief));
                    list.Add(new ChunkDesign("TempleSteps", TempleSteps));
                    break;
            }
            return list;
        }

        /// <summary>A pot stack with the mango arc that teaches the jump and the rooster's hop over it.</summary>
        static void JumpPots(Kit kit, float x)
        {
            kit.PotStack(x);
            kit.JumpArc(x);
            kit.Hop(x - 0.9f, 1.8f, 0.9f);
        }

        // ------------------------------------------------------------------ every zone

        /// <summary>Flat start: the kid starts at local 10, the rooster ahead of her pecking about.</summary>
        static GameObject Runway(ZoneKit z)
        {
            var kit = new Kit("Runway", 24f, z, 100 + z.zone);
            kit.MangoLine(14f, 5, 2f, 0.6f);
            kit.Litter(6);
            return kit.Finish();
        }

        // ------------------------------------------------------------------ zone 1: the lane

        static GameObject Pots(ZoneKit z)
        {
            var kit = new Kit("Pots", 16f, z, 1);
            JumpPots(kit, 5f);
            JumpPots(kit, 11f);
            kit.Litter(3);
            return kit.Finish();
        }

        static GameObject DungAndDog(ZoneKit z)
        {
            var kit = new Kit("DungAndDog", 18f, z, 2);
            kit.Dung(4.5f);
            kit.JumpArc(4.5f);
            kit.Hop(4f, 1f, 0.45f);
            kit.MangoLine(6.8f, 3, 0.8f, 0.55f);
            kit.Dog(10.5f);
            kit.JumpArc(10.5f);
            kit.Hop(9.7f, 1.6f, 0.8f);
            kit.Feather(10.6f, 2.8f, 0); // a double jump over the dog
            kit.Chilli(15f, 0.6f);
            kit.Litter(3);
            return kit.Finish();
        }

        static GameObject Puddle(ZoneKit z)
        {
            var kit = new Kit("Puddle", 18f, z, 3);
            kit.Puddle(5f, 1.6f);
            kit.JumpArc(5f);
            kit.Hop(4f, 2f, 0.5f);
            JumpPots(kit, 12f);
            kit.Feather(12.1f, 2.8f, 2);
            kit.Litter(3);
            return kit.Finish();
        }

        static GameObject Clotheslines(ZoneKit z)
        {
            var kit = new Kit("Clotheslines", 18f, z, 4);
            kit.Clothesline(5f);
            kit.MangoLine(4.2f, 3, 0.6f, 0.3f);
            kit.Clothesline(12f);
            kit.MangoLine(11.2f, 3, 0.6f, 0.3f);
            kit.Litter(3);
            return kit.Finish();
        }

        static GameObject CotBounce(ZoneKit z)
        {
            var kit = new Kit("CotBounce", 20f, z, 5);
            kit.Cot(3f);
            kit.Arc(2.9f, 4.8f, 2.4f, 6);
            kit.Hop(3f, 4.8f, 2.2f);
            kit.Feather(5.8f, 4.3f, 2); // a double jump at the top of the bounce
            JumpPots(kit, 14f);
            return kit.Finish();
        }

        static GameObject Cart(ZoneKit z)
        {
            var kit = new Kit("Cart", 18f, z, 6);
            kit.Cart(4f);
            kit.MangoLine(4.4f, 4, 0.5f, 1.5f);
            kit.MangoLine(4.8f, 3, 0.7f, 2.9f);
            kit.Hop(3.2f, 4f, 1.6f);
            kit.Feather(7.2f, 3.4f, 1); // a double jump off the cart's bed
            JumpPots(kit, 13.5f);
            return kit.Finish();
        }

        /// <summary>A puddle, then the rooster knocks a pot stack into the lane behind him, then a clothesline.</summary>
        static GameObject Mischief(ZoneKit z)
        {
            var kit = new Kit("Mischief", 20f, z, 7);
            kit.Puddle(4f, 1.6f);
            kit.JumpArc(4f);
            kit.Hop(3f, 2f, 0.5f);
            if (kit.Art("water_pot_stand", 12.3f, 1.6f, height: 1.1f) == null) kit.Art("brass_pots", 12.3f, 1.6f, height: 0.5f);
            var knocked = kit.PotStack(12f, hiddenUntilMischief: true);
            kit.Mischief(13f, knocked);
            kit.Clothesline(17f);
            kit.MangoLine(16.2f, 3, 0.6f, 0.3f);
            return kit.Finish();
        }

        static GameObject ClothesAndPots(ZoneKit z)
        {
            var kit = new Kit("ClothesAndPots", 20f, z, 8);
            kit.Clothesline(4f);
            kit.MangoLine(3.2f, 3, 0.6f, 0.3f);
            JumpPots(kit, 10f);
            kit.Clothesline(16f);
            kit.MangoLine(15.2f, 3, 0.6f, 0.3f);
            return kit.Finish();
        }

        /// <summary>A row of houses with a ladder up the first one; mangoes and a feather along the roofs.</summary>
        static GameObject Houses(ZoneKit z)
        {
            var kit = new Kit("Houses", 24f, z, 9);
            float end = kit.RoofRow(5f, new[] { "", "house_pink", "house_limewash" }, ladder: true);
            kit.MangoLine(5.6f, Mathf.FloorToInt((end - 6f) / 0.65f), 0.65f, 3.05f);
            kit.Feather(end - 1f, 3.95f, 2);
            JumpPots(kit, end + 7f);
            return kit.Finish();
        }

        /// <summary>Two rows of houses with a gap between: double jump up, jump the gap, drop off the end.</summary>
        static GameObject RoofHop(ZoneKit z)
        {
            var kit = new Kit("RoofHop", 26f, z, 10);
            kit.Arc(1.2f, 3.4f, 2.6f, 4);
            float end = kit.RoofRow(5f, new[] { "house_indigo_veranda", "house_pink" }, ladder: false);
            kit.Arc(end - 0.6f, 3f, 1.2f, 3, 2.5f);
            float end2 = kit.RoofRow(end + 1.8f, new[] { "house_limewash", "house_indigo_veranda" }, ladder: false);
            kit.MangoLine(end + 2.4f, 4, 0.7f, 3.05f);
            kit.Chilli(end2 + 3f, 0.6f);
            return kit.Finish();
        }

        // ------------------------------------------------------------------ zone 2: fields and canal

        static GameObject Canal(ZoneKit z)
        {
            var kit = new Kit("Canal", 18f, z, 21);
            kit.Canal(6f, 2.5f, bridge: false);
            kit.JumpArc(7.25f);
            kit.Feather(7.25f, 3.1f, 0);
            kit.Dung(14f);
            kit.JumpArc(14f);
            kit.Hop(13.5f, 1f, 0.45f);
            return kit.Finish();
        }

        static GameObject BridgeCanal(ZoneKit z)
        {
            var kit = new Kit("BridgeCanal", 18f, z, 22);
            kit.Canal(6f, 3.5f, bridge: true);
            kit.MangoLine(6.1f, 5, 0.75f, 0.55f);
            kit.Litter(3);
            return kit.Finish();
        }

        /// <summary>The widest canal, 4.5 m: a double jump, or a wade.</summary>
        static GameObject WideCanal(ZoneKit z)
        {
            var kit = new Kit("WideCanal", 20f, z, 23);
            kit.Canal(7f, 4.5f, bridge: false);
            kit.Arc(5.4f, 7.6f, 2.3f, 7);
            kit.Feather(9.25f, 3.5f, 0);
            return kit.Finish();
        }

        static GameObject FieldDung(ZoneKit z)
        {
            var kit = new Kit("FieldDung", 18f, z, 24);
            kit.Dung(5f);
            kit.JumpArc(5f);
            kit.Hop(4.5f, 1f, 0.45f);
            kit.Dung(10.5f);
            kit.JumpArc(10.5f);
            kit.Hop(10f, 1f, 0.45f);
            kit.Chilli(15f, 0.6f);
            kit.Litter(3);
            return kit.Finish();
        }

        static GameObject FieldCart(ZoneKit z)
        {
            var kit = new Kit("FieldCart", 20f, z, 25);
            kit.Cart(5f);
            kit.MangoLine(5.4f, 4, 0.5f, 1.5f);
            kit.Hop(4.2f, 4f, 1.6f);
            kit.Feather(8.4f, 3.4f, 1);
            kit.Dung(15f);
            kit.JumpArc(15f);
            kit.Hop(14.5f, 1f, 0.45f);
            return kit.Finish();
        }

        static GameObject SmallHaystacks(ZoneKit z)
        {
            var kit = new Kit("SmallHaystacks", 20f, z, 26);
            kit.Haystack(4f, big: false);
            kit.MangoLine(4.1f, 3, 0.45f, 1.75f);
            kit.Haystack(10f, big: false);
            kit.Haystack(15f, big: false);
            kit.Feather(15.6f, 3.2f, 2);
            return kit.Finish();
        }

        /// <summary>Small, big, small, big: hop, double jump, hop, double jump (or vault the big ones, slowly).</summary>
        static GameObject HaystackChain(ZoneKit z)
        {
            var kit = new Kit("HaystackChain", 24f, z, 27);
            kit.Haystack(3f, big: false);
            float end = kit.Haystack(8f, big: true);
            kit.Arc(6.5f, 4.5f, 2.4f, 5);
            kit.Feather(end - 0.8f, 3.7f, 2);
            kit.Haystack(14f, big: false);
            kit.Haystack(18.5f, big: true);
            return kit.Finish();
        }

        /// <summary>A small haystack as a step, then a mango tree whose branch is a quick climb and a row of mangoes.</summary>
        static GameObject MangoBranch(ZoneKit z)
        {
            var kit = new Kit("MangoBranch", 20f, z, 28);
            kit.Haystack(2.2f, big: false);
            kit.MangoTree(5f);
            kit.Feather(9.3f, 3.2f, 1);
            kit.Dung(15f);
            kit.JumpArc(15f);
            kit.Hop(14.5f, 1f, 0.45f);
            return kit.Finish();
        }

        static GameObject Buffalo(ZoneKit z)
        {
            var kit = new Kit("Buffalo", 22f, z, 29);
            float end = kit.Buffalo(6f);
            kit.Arc(6.5f, 7f, 2.8f, 6, 1.1f);
            kit.Feather(end + 1.6f, 4.4f, 2);
            kit.Dung(17f);
            kit.JumpArc(17f);
            kit.Hop(16.5f, 1f, 0.45f);
            return kit.Finish();
        }

        /// <summary>The rooster knocks the pots by the well into the lane, then a canal.</summary>
        static GameObject FieldMischief(ZoneKit z)
        {
            var kit = new Kit("FieldMischief", 22f, z, 30);
            kit.Dung(4f);
            kit.JumpArc(4f);
            kit.Hop(3.5f, 1f, 0.45f);
            kit.Art("well", 12.4f, 2.2f, height: 2.0f);
            var knocked = kit.PotStack(12f, hiddenUntilMischief: true);
            kit.Mischief(13f, knocked);
            kit.Canal(16.5f, 2.5f, bridge: false);
            kit.JumpArc(17.75f);
            return kit.Finish();
        }

        // ------------------------------------------------------------------ zone 3: terraces, market, temple

        static GameObject RoofRun(ZoneKit z)
        {
            var kit = new Kit("RoofRun", 30f, z, 31);
            float end = kit.RoofRow(4f, new[] { "", "house_indigo_veranda", "house_pink", "house_limewash" }, ladder: true);
            kit.Tank(9.2f, 2.5f);
            kit.Arc(9.2f - 2.4f, 4.8f, 1.4f, 5, 2.5f);
            kit.Art(null, "chilli_mat", end - 1.4f, 2.5f, 0.3f, out _, height: 0.25f);
            float end2 = kit.RoofRow(end + 2f, new[] { "house_indigo_veranda", "house_pink" }, ladder: false);
            kit.Arc(end - 0.8f, 3.6f, 1.2f, 4, 2.5f);
            kit.Feather((end + 2f + end2) * 0.5f, 4.1f, 0);
            kit.Chilli(end2 + 3f, 0.6f);
            return kit.Finish();
        }

        static GameObject RoofTanks(ZoneKit z)
        {
            var kit = new Kit("RoofTanks", 28f, z, 32);
            float end = kit.RoofRow(3f, new[] { "", "house_indigo_veranda", "house_pink", "house_indigo_veranda" }, ladder: true);
            kit.Tank(6.6f, 2.5f);
            kit.Tank(end - 2f, 2.5f);
            kit.Art(null, "papad_mat", 8.6f, 2.5f, 0.3f, out _, height: 0.25f);
            float end2 = kit.RoofRow(end + 2.2f, new[] { "house_limewash", "house_pink", "house_indigo_veranda" }, ladder: false);
            kit.Feather(end2 - 1.5f, 4.1f, 1);
            kit.MangoLine(end + 2.8f, 5, 0.7f, 3.05f);
            return kit.Finish();
        }

        static GameObject MarketClotheslines(ZoneKit z)
        {
            var kit = new Kit("MarketClotheslines", 20f, z, 33);
            kit.Clothesline(5f);
            kit.MangoLine(4.2f, 3, 0.6f, 0.3f);
            kit.Clothesline(12f);
            kit.Feather(12f, 2.7f, 2); // over the line, not under it
            kit.Litter(3);
            return kit.Finish();
        }

        static GameObject MarketPots(ZoneKit z)
        {
            var kit = new Kit("MarketPots", 18f, z, 34);
            kit.PotStack(4f);
            kit.PotStack(4.7f);
            kit.JumpArc(4.35f);
            kit.Hop(3.3f, 2.1f, 0.9f);
            kit.HensBasket(12f);
            kit.JumpArc(12f);
            kit.Hop(11.2f, 1.6f, 0.8f);
            kit.Litter(3);
            return kit.Finish();
        }

        /// <summary>Three stalls side by side: jump under an awning and bounce from roof to roof.</summary>
        static GameObject Awnings(ZoneKit z)
        {
            var kit = new Kit("Awnings", 24f, z, 35);
            float x = 3f;
            foreach (var stall in new[] { "stall_c_1", "stall_d_2", "stall_e_3" }) x = kit.Stall(x, stall) + 0.25f;
            kit.MangoLine(3.6f, Mathf.FloorToInt((x - 4f) / 1.1f), 1.1f, 3.4f);
            kit.Feather(x - 2f, 4.7f, 2);
            kit.Hens(x + 3f, 2);
            kit.JumpArc(x + 3f);
            return kit.Finish();
        }

        static GameObject AwningsLong(ZoneKit z)
        {
            var kit = new Kit("AwningsLong", 28f, z, 36);
            float x = 2.5f;
            foreach (var stall in new[] { "stall_f_1", "stall_g_2", "stall_h_1", "stall_flowers" }) x = kit.Stall(x, stall) + 0.2f;
            kit.MangoLine(3f, Mathf.FloorToInt((x - 3.5f) / 1.1f), 1.1f, 3.5f);
            kit.Feather(x * 0.5f, 4.8f, 2);
            kit.Chilli(x + 2f, 0.6f);
            return kit.Finish();
        }

        static GameObject Hens(ZoneKit z)
        {
            var kit = new Kit("Hens", 20f, z, 37);
            kit.Hens(5f, 3);
            kit.JumpArc(5f);
            kit.Hop(4.2f, 1.6f, 0.7f);
            kit.HensBasket(11f);
            kit.JumpArc(11f);
            kit.Hop(10.2f, 1.6f, 0.8f);
            kit.Feather(11f, 2.9f, 1);
            kit.Hens(16f, 2);
            kit.JumpArc(16f);
            kit.Hop(15.3f, 1.4f, 0.7f);
            return kit.Finish();
        }

        static GameObject HensBaskets(ZoneKit z)
        {
            var kit = new Kit("HensBaskets", 18f, z, 38);
            kit.HensBasket(4f);
            kit.HensBasket(4.8f);
            kit.JumpArc(4.4f);
            kit.Hop(3.4f, 2f, 0.8f);
            kit.Hens(12f, 3);
            kit.JumpArc(12f);
            kit.Hop(11.2f, 1.6f, 0.7f);
            return kit.Finish();
        }

        /// <summary>The basket fake-out: a stall to bounce off, then the rooster tips a basket of hens into the lane.</summary>
        static GameObject MarketMischief(ZoneKit z)
        {
            var kit = new Kit("MarketMischief", 22f, z, 39);
            float x = kit.Stall(2f, "stall_vessels");
            kit.Feather((2f + x) * 0.5f, 4.5f, 0);
            kit.Art("hens_basket", 14.4f, 1.4f, height: 0.6f);
            var knocked = kit.HensBasket(14f, hiddenUntilMischief: true);
            kit.Mischief(15f, knocked);
            kit.Clothesline(19.5f);
            kit.MangoLine(18.7f, 3, 0.6f, 0.3f);
            return kit.Finish();
        }

        /// <summary>Up the temple steps (they step up on their own), along the lamp-lit landing, down again.</summary>
        static GameObject TempleSteps(ZoneKit z)
        {
            var kit = new Kit("TempleSteps", 30f, z, 40);
            kit.Art("mandapam", 11f, 3f, height: 2.9f);
            float end = kit.Steps(4f, 6, 6f);
            kit.MangoLine(8.8f, 7, 0.75f, 2.05f);
            kit.Feather(11.2f, 3.6f, 0);
            JumpPots(kit, end + 5f);
            return kit.Finish();
        }
    }
}
