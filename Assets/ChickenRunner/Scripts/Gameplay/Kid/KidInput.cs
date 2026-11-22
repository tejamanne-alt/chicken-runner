using System.Collections.Generic;
using ChickenRunner.Core;
using UnityEngine;
#if CR_INPUT_SYSTEM && ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace ChickenRunner
{
    /// <summary>
    /// Reads one thumb anywhere on the screen (or the mouse, in the editor) plus the editor keyboard keys,
    /// and turns them into gestures. Works with either the Input System package or the old Input Manager.
    /// </summary>
    public sealed class KidInput : MonoBehaviour
    {
        [Header("Touch gestures")]
        [Tooltip("Seconds a touch waits before it counts as a jump, so a swipe down never starts with one.")]
        [SerializeField, Range(0f, 0.15f)] internal float commitTime = 0.06f;
        [Tooltip("Swipe length in screen heights.")]
        [SerializeField, Range(0.01f, 0.2f)] internal float swipeThreshold = 0.05f;
        [Tooltip("A swipe down this soon after a touch became a jump still counts (as a fast drop).")]
        [SerializeField, Range(0f, 0.4f)] internal float lateSwipeWindow = 0.2f;

        readonly GestureRecognizer _gestures = new GestureRecognizer();
        readonly List<GestureEvent> _events = new List<GestureEvent>(8);
        Vector2 _pointerPosition;
        bool _pointerWasDown;
        bool _ignoringPointer;
        bool _keyboardJumpHeld;

        /// <summary>Gestures recognised this frame, in order.</summary>
        public IReadOnlyList<GestureEvent> Events => _events;

        /// <summary>A jump is being held by touch or key, for the higher jump.</summary>
        public bool JumpHeld => _gestures.IsHolding || _keyboardJumpHeld;

        /// <summary>Any new press this frame: used to start a level or dismiss a screen.</summary>
        public bool AnyPress { get; private set; }

        public bool PausePressed { get; private set; }
        public bool RetryPressed { get; private set; }
        public bool DebugTogglePressed { get; private set; }

        /// <summary>Reads devices; call once per frame before gameplay consumes <see cref="Events"/>.</summary>
        public void Sample()
        {
            _gestures.CommitTime = commitTime;
            _gestures.SwipeThreshold = swipeThreshold;
            _gestures.LateSwipeWindow = lateSwipeWindow;
            _events.Clear();
            AnyPress = false;

            ReadPointer(out bool down, out Vector2 position);
            bool pressedNow = down && !_pointerWasDown;
            if (pressedNow) _ignoringPointer = HudLayout.IsReserved(position);
            if (down) _pointerPosition = position;

            if (!_ignoringPointer)
            {
                float h = Mathf.Max(1, Screen.height);
                _gestures.Process(down, _pointerPosition.x / h, _pointerPosition.y / h, Time.unscaledTime, _events);
                if (pressedNow) AnyPress = true;
            }
            if (!down) _ignoringPointer = false;
            _pointerWasDown = down;

            ReadKeyboard();
        }

        /// <summary>Forget the current touch, for example when the game pauses mid-hold.</summary>
        public void CancelGesture()
        {
            _gestures.Cancel();
            _keyboardJumpHeld = false;
        }

        void ReadKeyboard()
        {
            bool jumpDown = false, jumpUp = false, jumpHeld = false, slideDown = false;
            bool pause = false, retry = false, debug = false;
            // Up and W also climb when the kid is beside a ladder; ladders arrive in milestone 2, so for now they jump.
#if CR_INPUT_SYSTEM && ENABLE_INPUT_SYSTEM
            var k = Keyboard.current;
            if (k != null)
            {
                jumpDown = k.spaceKey.wasPressedThisFrame || k.upArrowKey.wasPressedThisFrame || k.wKey.wasPressedThisFrame;
                jumpUp = k.spaceKey.wasReleasedThisFrame || k.upArrowKey.wasReleasedThisFrame || k.wKey.wasReleasedThisFrame;
                jumpHeld = k.spaceKey.isPressed || k.upArrowKey.isPressed || k.wKey.isPressed;
                slideDown = k.downArrowKey.wasPressedThisFrame || k.sKey.wasPressedThisFrame;
                pause = k.escapeKey.wasPressedThisFrame || k.pKey.wasPressedThisFrame;
                retry = k.rKey.wasPressedThisFrame;
                debug = k.f1Key.wasPressedThisFrame || k.backquoteKey.wasPressedThisFrame;
            }
#elif ENABLE_LEGACY_INPUT_MANAGER
            jumpDown = Input.GetKeyDown(KeyCode.Space) || Input.GetKeyDown(KeyCode.UpArrow) || Input.GetKeyDown(KeyCode.W);
            jumpUp = Input.GetKeyUp(KeyCode.Space) || Input.GetKeyUp(KeyCode.UpArrow) || Input.GetKeyUp(KeyCode.W);
            jumpHeld = Input.GetKey(KeyCode.Space) || Input.GetKey(KeyCode.UpArrow) || Input.GetKey(KeyCode.W);
            slideDown = Input.GetKeyDown(KeyCode.DownArrow) || Input.GetKeyDown(KeyCode.S);
            pause = Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.P);
            retry = Input.GetKeyDown(KeyCode.R);
            debug = Input.GetKeyDown(KeyCode.F1) || Input.GetKeyDown(KeyCode.BackQuote);
#endif
            if (jumpDown)
            {
                _events.Add(GestureEvent.JumpPress);
                AnyPress = true;
            }
            if (jumpUp && _keyboardJumpHeld) _events.Add(GestureEvent.JumpRelease);
            _keyboardJumpHeld = jumpHeld;
            if (slideDown)
            {
                _events.Add(GestureEvent.SwipeDown);
                AnyPress = true;
            }
            PausePressed = pause;
            RetryPressed = retry;
            DebugTogglePressed = debug;
        }

        static void ReadPointer(out bool down, out Vector2 position)
        {
            down = false;
            position = default;
#if CR_INPUT_SYSTEM && ENABLE_INPUT_SYSTEM
            var touchscreen = Touchscreen.current;
            if (touchscreen != null)
            {
                var touch = touchscreen.primaryTouch;
                position = touch.position.ReadValue();
                if (touch.press.isPressed)
                {
                    down = true;
                    return;
                }
            }
            var mouse = Mouse.current;
            if (mouse != null && mouse.leftButton.isPressed)
            {
                down = true;
                position = mouse.position.ReadValue();
            }
#elif ENABLE_LEGACY_INPUT_MANAGER
            if (Input.touchCount > 0)
            {
                var touch = Input.GetTouch(0);
                position = touch.position;
                down = touch.phase != TouchPhase.Ended && touch.phase != TouchPhase.Canceled;
                return;
            }
            if (Input.GetMouseButton(0))
            {
                down = true;
                position = Input.mousePosition;
            }
#endif
        }
    }
}
