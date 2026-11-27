using System;
using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// A zone's painted surroundings, built by Chicken Runner > Build Game from the Blender scene's layout
    /// (Assets/ChickenRunner/Art/Layouts): tracks of painted cards that the <see cref="BackdropStreamer"/> repeats along
    /// the course, the ground's material and the colour behind everything.
    /// </summary>
    [CreateAssetMenu(menuName = "Chicken Runner/Zone Art", fileName = "ZoneArt_", order = 3)]
    public sealed class ZoneArt : ScriptableObject
    {
        /// <summary>A prefab of cards laid out in course metres, repeated every <see cref="period"/> metres.</summary>
        [Serializable]
        public sealed class Track
        {
            public GameObject prefab;
            [Min(1f)] public float period = 100f;
            [Tooltip("Leftmost and rightmost edge of the prefab's cards, in its own metres.")]
            public float contentMin;
            public float contentMax = 100f;
            [Tooltip("How far either side of the camera this track must be filled; deeper tracks need more.")]
            [Min(10f)] public float reach = 80f;
            [Tooltip("Laid for every other copy: the same scenery in the reverse order along the lane (the pictures not "
                + "flipped), so the street repeats only every two periods. Empty: every copy the same.")]
            public GameObject alternate;
        }

        [SerializeField, Range(1, 3)] internal int zone = 1;
        [SerializeField] internal Track[] tracks = new Track[0];
        [Tooltip("PaintedGround material for the big ground behind the lane and for the chunks' own ground.")]
        [SerializeField] internal Material ground;
        [SerializeField] internal Color sky = new Color(0.98f, 0.84f, 0.6f);
        [Tooltip("The ground plane behind the lane runs from this depth...")]
        [SerializeField] internal float groundFrom = 4.4f;
        [Tooltip("...to this one, where the far painting takes over.")]
        [SerializeField] internal float groundTo = 95f;

        public int Zone => zone;
        public Track[] Tracks => tracks;
        public Material Ground => ground;
        public Color Sky => sky;
        public float GroundFrom => groundFrom;
        public float GroundTo => groundTo;
    }
}
