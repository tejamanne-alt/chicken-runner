using System;
using ChickenRunner.Core;
using UnityEngine;

namespace ChickenRunner
{
    public enum FlowState
    {
        /// <summary>
        /// Level 1's opening in the neighbour's yard (<see cref="BasketIntro"/>): the kid tiptoes to the basket, the
        /// player holds to lift it, the rooster bursts out and the neighbour wakes. A smooth lift gives the rooster the
        /// short head start, a dropped one the long one. Played once per level load; a retry starts at the chase.
        /// </summary>
        Intro,
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
    /// On its own it plays its <see cref="level"/> and a tap on the result retries; in the full game a
    /// <see cref="GameSession"/> loads levels with <see cref="LoadLevel"/> and handles the result itself.
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
        [Tooltip("A tap on the result screen retries, and any tap ends a pause. Off when a GameSession shows its own "
            + "result and pause buttons (a tap that ended the pause would take the button away before it was clicked).")]
        [SerializeField] internal bool tapToRetry = true;

        [Header("Basket intro (level 1)")]
        [Tooltip("The kid's tiptoe past the sleeping neighbour, m/s.")]
        [SerializeField] internal float tiptoeSpeed = 1.1f;
        [Tooltip("Seconds of holding to lift the basket all the way.")]
        [SerializeField] internal float liftSeconds = 1.6f;
        [Tooltip("How fast the basket drops back when the hold is let go, per second.")]
        [SerializeField] internal float dropRate = 2.5f;
        [Tooltip("The rooster's average speed as he bursts out to his head start, m/s (he peaks at about 1.4 times this).")]
        [SerializeField] internal float burstSpeed = 8f;

        enum IntroPhase { Walk, Hold, Burst }

        IntroPhase _introPhase;
        BasketLift _lift;
        bool _introDone;
        bool _neighbourWoke;
        float _introGap;
        float _introTimer;
        float _burstLength;
        float _accumulator;
        bool _ready;
        bool _started;

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
        /// <summary>In the basket intro, sneaking up to the basket.</summary>
        public bool IntroWalking => State == FlowState.Intro && _introPhase == IntroPhase.Walk;
        /// <summary>In the basket intro, waiting for (or during) the hold that lifts the basket.</summary>
        public bool IntroHolding => State == FlowState.Intro && _introPhase == IntroPhase.Hold;
        /// <summary>The basket lift, 0 to 1.</summary>
        public float IntroLift => _lift.Lift;
        /// <summary>How many times the basket was dropped back (any drop makes the lift clumsy).</summary>
        public int IntroDrops => _lift.Drops;
        public bool TapToRetry
        {
            get => tapToRetry;
            set => tapToRetry = value;
        }

        /// <summary>The chase is over and the result is showing.</summary>
        public event Action Finished;

        void Awake()
        {
            // Phones default to 30 fps; a runner needs 60.
            Application.targetFrameRate = 60;
        }

        void Start()
        {
            _started = true;
            // A session loads its own levels; a scene with only a GameFlow plays the level it was given.
            if (level != null && !_ready) LoadLevel(level);
        }

        /// <summary>Sets up <paramref name="newLevel"/> with its zone's tuning and waits at the start for the first tap.</summary>
        public void LoadLevel(LevelDefinition newLevel)
        {
            level = newLevel;
            _introDone = false;
            if (!Validate()) return;
            var tuning = level.Tuning.Values;
            kid.Init(tuning);
            rooster.Init(tuning);
            streamer.Init(level);
            director.Init(level, kid, rooster, streamer);
            _ready = true;
            enabled = true;
            ResetLevel();
        }

        bool Validate()
        {
            bool ok = level != null && level.Tuning != null && kid != null && rooster != null && director != null
                && streamer != null && input != null;
            if (!ok)
            {
                Debug.LogError("GameFlow is missing references (level with tuning, kid, rooster, director, streamer, input). "
                    + "Run Chicken Runner > Build Game to regenerate the scene.", this);
                _ready = false;
            }
            return ok;
        }

        /// <summary>Whether Start has run, so a session knows the scene is set up.</summary>
        public bool IsStarted => _started;

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
                if (tapToRetry && input.AnyPress) SetPaused(false);
                return;
            }

            switch (State)
            {
                case FlowState.Intro:
                    TickIntro(Time.deltaTime);
                    break;
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
                    if (tapToRetry && CanDismissResult && input.AnyPress)
                    {
                        Retry();
                        return;
                    }
                    break;
            }

            Simulate(Time.deltaTime);
            // Once the chase is over, stream around the kid only, so the fleeing rooster does not load the rest of the course.
            bool chasing = State == FlowState.Intro || State == FlowState.Ready || State == FlowState.Chase;
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
            // A retry before the basket intro has finished plays the intro again; after it, straight into the chase.
            if (State != FlowState.Intro) StartChase();
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
            float gap = _introDone ? _introGap : level.StartGap;
            streamer.Refresh(0f, gap);
            kid.IntroPose = KidIntroPose.None;
            kid.ResetTo(0f);
            rooster.ResetTo(gap);
            director.ResetChase();
            input.CancelGesture();

            // Level 1 opens in the neighbour's yard: the first time, the basket intro; on a retry, the yard as it was
            // left (the basket flung aside, the neighbour awake) and the head start the lift earned.
            // Before the chase the camera pulls back to show the rooster ahead too (not in the basket intro, which is close).
            if (chaseCamera != null) chaseCamera.Establishing = true;
            var intro = BasketIntro.Active;
            if (intro != null && !_introDone) BeginIntro(intro);
            else if (intro != null)
            {
                intro.SetLift(1f);
                intro.SetToss(1f);
                intro.Wake(true);
            }
            if (chaseCamera != null) chaseCamera.Snap();
        }

        void BeginIntro(BasketIntro intro)
        {
            Enter(FlowState.Intro);
            if (chaseCamera != null) chaseCamera.Establishing = false;
            _introPhase = IntroPhase.Walk;
            _lift.Reset();
            _neighbourWoke = false;
            _introTimer = 0f;
            intro.ResetPart();
            kid.ResetTo(intro.WalkFrom);
            kid.IntroPose = KidIntroPose.Tiptoe;
            kid.IntroLift = 0f;
            rooster.ResetTo(intro.RoosterX);
        }

        void TickIntro(float dt)
        {
            var intro = BasketIntro.Active;
            if (intro == null)
            {
                FinishIntro(level.StartGap);
                return;
            }
            switch (_introPhase)
            {
                case IntroPhase.Walk:
                {
                    // A tap skips the walk (and a press held on from it starts the lift).
                    float x = input.AnyPress ? 0f : Mathf.MoveTowards(kid.X, 0f, tiptoeSpeed * dt);
                    kid.ResetTo(x);
                    if (x >= -1e-3f)
                    {
                        _introPhase = IntroPhase.Hold;
                        kid.IntroPose = KidIntroPose.Lift;
                        kid.IntroLift = 0f;
                        _lift.Reset(input.JumpHeld);
                    }
                    break;
                }
                case IntroPhase.Hold:
                {
                    if (_lift.Step(input.JumpHeld, dt, liftSeconds, dropRate))
                    {
                        // Let go part way up: the basket drops back with a clunk and the neighbour stirs.
                        var rim = new Vector3(intro.RoosterX, 0.9f, intro.transform.position.z);
                        WorldBarks.Show("CLUNK!", rim, new Color(0.55f, 0.35f, 0.12f));
                        WorldBarks.Show(_lift.Drops == 1 ? "Hmm..?" : "Mmph!", intro.NeighbourPosition + Vector3.up * 1.3f,
                            new Color(0.25f, 0.3f, 0.55f));
                    }
                    kid.IntroLift = _lift.Lift;
                    intro.SetLift(_lift.Lift);
                    if (_lift.Done) BeginBurst();
                    break;
                }
                case IntroPhase.Burst:
                {
                    _introTimer += dt;
                    intro.SetToss(Mathf.Clamp01((_introTimer - 0.15f) / 0.45f));
                    if (_introTimer >= 0.15f) kid.IntroPose = KidIntroPose.None;
                    if (_introTimer >= 0.3f && !_neighbourWoke)
                    {
                        _neighbourWoke = true;
                        intro.Wake(true);
                        WorldBarks.Show("OI! MY ROOSTER!", intro.NeighbourPosition + Vector3.up * 1.5f, new Color(0.25f, 0.3f, 0.55f), 1.6f);
                    }
                    if (_introTimer >= _burstLength) FinishIntro(_introGap);
                    break;
                }
            }
        }

        void BeginBurst()
        {
            _introPhase = IntroPhase.Burst;
            _introTimer = 0f;
            var t = level.Tuning.Values;
            _introGap = _lift.Gap(t);
            // Out from under the basket to his head start (9 to 13 m) at a startled sprint, arriving at his running
            // speed just as the kid sets off.
            _burstLength = RoosterBrain.BurstBeat + Mathf.Abs(_introGap - rooster.X) / Mathf.Max(1f, burstSpeed);
            rooster.BeginBurst(_introGap, _burstLength, t.roosterRunSpeed);
        }

        void FinishIntro(float gap)
        {
            _introDone = true;
            _introGap = gap;
            kid.IntroPose = KidIntroPose.None;
            input.CancelGesture(); // the hold that lifted the basket is not a jump
            var intro = BasketIntro.Active;
            if (intro != null)
            {
                intro.SetLift(1f);
                intro.SetToss(1f);
                intro.Wake(true);
            }
            StartChase();
        }

        void StartChase()
        {
            Enter(FlowState.Chase);
            if (chaseCamera != null) chaseCamera.Establishing = false;   // eases in to the close framing
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
            if (State == FlowState.Ready || (State == FlowState.Intro && _introPhase != IntroPhase.Burst))
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
            if (State == FlowState.Intro)
            {
                // The burst: only the rooster moves; the kid stays where the lift left her.
                rooster.Tick(dt, director.Gap, kid.X);
                return;
            }
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
                    if (StateTime >= grabSequenceDuration) EnterResult();
                    break;
                case FlowState.Escape:
                    if (StateTime >= escapeSequenceDuration) EnterResult();
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

        void EnterResult()
        {
            Enter(FlowState.Result);
            Finished?.Invoke();
        }

        void Enter(FlowState state)
        {
            State = state;
            StateTime = 0f;
        }
    }
}
