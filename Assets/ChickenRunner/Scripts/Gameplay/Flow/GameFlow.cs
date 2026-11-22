using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    public enum FlowState
    {
        /// <summary>Kid and rooster in place, waiting for the first tap.</summary>
        Ready,
        Chase,
        /// <summary>The dive and the wriggle-free gag.</summary>
        Grab,
        /// <summary>The rooster got away; the kid runs out of steam.</summary>
        Escape,
        Result,
    }

    /// <summary>
    /// The level's state machine (ready, chase, grab, result) and the fixed-rate simulation clock.
    /// Kid, rooster and director are ticked here in a fixed order at <see cref="simulationRate"/> Hz,
    /// and their transforms are interpolated between ticks, so timing never depends on the frame rate.
    /// </summary>
    [DefaultExecutionOrder(-100)]
    public sealed class GameFlow : MonoBehaviour
    {
        const int MaxStepsPerFrame = 12;

        [SerializeField] internal LevelDefinition level;
        [SerializeField] internal KidController kid;
        [SerializeField] internal RoosterBrain rooster;
        [SerializeField] internal ChaseDirector director;
        [SerializeField] internal LevelStreamer streamer;
        [SerializeField] internal KidInput input;
        [SerializeField] internal ChaseCamera chaseCamera;

        [SerializeField, Range(30, 240)] internal int simulationRate = 120;
        [SerializeField] internal float grabSequenceDuration = 1.4f;
        [SerializeField] internal float escapeSequenceDuration = 1.6f;
        [Tooltip("Ignore taps for this long on the result screen, so frantic tapping at the end does not skip it.")]
        [SerializeField] internal float resultInputDelay = 0.6f;
        [SerializeField] internal bool showDebug;

        float _accumulator;
        bool _ready;

        public FlowState State { get; private set; }
        public float StateTime { get; private set; }
        public bool Paused { get; private set; }
        public bool ShowDebug => showDebug;
        public LevelDefinition Level => level;
        public KidController Kid => kid;
        public RoosterBrain Rooster => rooster;
        public ChaseDirector Director => director;
        public ChaseCamera ChaseCamera => chaseCamera;
        public bool CanDismissResult => State == FlowState.Result && StateTime >= resultInputDelay;

        void Awake()
        {
            // Phones default to 30 fps; a runner needs 60.
            Application.targetFrameRate = 60;
        }

        void Start()
        {
            if (!Validate()) return;
            var tuning = level.Tuning.Values;
            kid.Init(tuning);
            rooster.Init(tuning);
            streamer.Init(level);
            director.Init(level, kid, rooster, streamer);
            _ready = true;
            ResetLevel();
        }

        bool Validate()
        {
            bool ok = level != null && level.Tuning != null && kid != null && rooster != null && director != null
                && streamer != null && input != null;
            if (!ok)
            {
                Debug.LogError("GameFlow is missing references (level with tuning, kid, rooster, director, streamer, input). "
                    + "Run Chicken Runner > Build Grey-box Level to regenerate the scene.", this);
                enabled = false;
            }
            return ok;
        }

        void OnDisable()
        {
            Time.timeScale = 1f;
        }

        void OnApplicationPause(bool paused)
        {
            if (paused && State == FlowState.Chase) SetPaused(true);
        }

        void Update()
        {
            if (!_ready) return;
            input.ReservePauseButton = State == FlowState.Chase;
            input.Sample();
            StateTime += Time.deltaTime;
            WorldBarks.Tick(Time.deltaTime);

            if (input.DebugTogglePressed) showDebug = !showDebug;
            if (input.RetryPressed)
            {
                Retry();
                return;
            }
            if (input.PausePressed && State == FlowState.Chase) TogglePause();
            if (Paused)
            {
                if (input.AnyPress) SetPaused(false);
                return;
            }

            switch (State)
            {
                case FlowState.Ready:
                    if (input.AnyPress)
                    {
                        input.CancelGesture(); // the starting tap is not a jump
                        StartChase();
                    }
                    break;
                case FlowState.Chase:
                    FeedInput();
                    break;
                case FlowState.Result:
                    if (CanDismissResult && input.AnyPress)
                    {
                        Retry();
                        return;
                    }
                    break;
            }

            Simulate(Time.deltaTime);
            // Once the chase is over, stream around the kid only, so the fleeing rooster does not load the rest of the course.
            bool chasing = State == FlowState.Ready || State == FlowState.Chase;
            streamer.Refresh(kid.X, chasing ? rooster.X : kid.X);

            float alpha = _accumulator * simulationRate;
            kid.ApplyVisual(alpha);
            rooster.ApplyVisual(alpha);
        }

        public void TogglePause() => SetPaused(!Paused);

        public void SetPaused(bool paused)
        {
            if (paused && State != FlowState.Chase) return;
            Paused = paused;
            Time.timeScale = paused ? 0f : 1f;
            input.CancelGesture();
        }

        /// <summary>Losing costs only a retry: one tap puts the kid back at the start, already running.</summary>
        public void Retry()
        {
            ResetLevel();
            StartChase();
        }

        /// <summary>Back to the start of the level, waiting for the first tap.</summary>
        public void ResetLevel()
        {
            Paused = false;
            Time.timeScale = 1f;
            State = FlowState.Ready;
            StateTime = 0f;
            _accumulator = 0f;

            WorldBarks.Clear();
            Debris.ClearAll();
            streamer.ResetCourse();
            streamer.Refresh(0f, level.StartGap);
            kid.ResetTo(0f);
            rooster.ResetTo(level.StartGap);
            director.ResetChase();
            input.CancelGesture();
            if (chaseCamera != null) chaseCamera.Snap();
        }

        void StartChase()
        {
            Enter(FlowState.Chase);
            rooster.StartChase();
        }

        void FeedInput()
        {
            foreach (var e in input.Events)
            {
                switch (e)
                {
                    case GestureEvent.JumpPress:
                        kid.PressJump();
                        break;
                    case GestureEvent.SwipeDown:
                        kid.PressSlide();
                        break;
                    // SwipeUp is followed by a JumpPress; it becomes a climb when ladders arrive in milestone 2.
                }
            }
            kid.SetJumpHeld(input.JumpHeld);
        }

        void Simulate(float frameDt)
        {
            if (State == FlowState.Ready)
            {
                _accumulator = 0f;
                return;
            }

            float step = 1f / simulationRate;
            _accumulator += Mathf.Min(frameDt, 0.1f);
            int steps = 0;
            while (_accumulator >= step && steps < MaxStepsPerFrame)
            {
                Tick(step);
                _accumulator -= step;
                steps++;
            }
            if (steps == MaxStepsPerFrame) _accumulator = 0f;
        }

        void Tick(float dt)
        {
            kid.Tick(dt);
            rooster.Tick(dt, director.Gap, kid.X);

            switch (State)
            {
                case FlowState.Chase:
                    var outcome = director.Tick(dt);
                    if (outcome == ChaseOutcome.Caught) EnterGrab();
                    else if (ChaseRules.IsEscape(outcome)) EnterEscape();
                    break;
                case FlowState.Grab:
                    if (StateTime >= grabSequenceDuration) Enter(FlowState.Result);
                    break;
                case FlowState.Escape:
                    if (StateTime >= escapeSequenceDuration) Enter(FlowState.Result);
                    break;
            }
        }

        void EnterGrab()
        {
            Enter(FlowState.Grab);
            director.Finish();
            kid.BeginDive();
            rooster.BeginWriggle();
            WorldBarks.Show("GOTCHA!", kid.transform.position + Vector3.up * 1.5f, new Color(0.15f, 0.45f, 0.85f));
        }

        void EnterEscape()
        {
            Enter(FlowState.Escape);
            director.Finish();
            kid.BeginStop();
            rooster.BeginFlee();
        }

        void Enter(FlowState state)
        {
            State = state;
            StateTime = 0f;
        }
    }
}
