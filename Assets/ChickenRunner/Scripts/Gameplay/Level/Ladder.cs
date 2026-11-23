using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// A bamboo ladder against a wall. Put it on the wall's solid collider (or a parent of it): running into that wall
    /// climbs it in ladderClimbDuration at ladderSpeedFactor of the run speed, instead of the slow vault.
    /// </summary>
    public sealed class Ladder : MonoBehaviour
    {
    }
}
