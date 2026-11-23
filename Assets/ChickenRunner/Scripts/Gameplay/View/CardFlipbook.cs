using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// A painted cut-out on a quad whose picture can be swapped at runtime, for the kid's and the rooster's poses.
    /// Every frame is drawn at the same <see cref="pixelsPerMetre"/>, so poses keep their sizes relative to each other,
    /// and stands with its bottom centre on this object's parent origin (the character's feet).
    /// Uses the PaintedCard shader through a property block, so all frames share one material.
    /// </summary>
    [RequireComponent(typeof(MeshFilter), typeof(MeshRenderer))]
    public sealed class CardFlipbook : MonoBehaviour
    {
        static readonly int MainTexId = Shader.PropertyToID("_MainTex");
        static readonly int TintId = Shader.PropertyToID("_Tint");

        [Tooltip("Art pixels per metre in the world, the same for every frame.")]
        [SerializeField, Min(1f)] internal float pixelsPerMetre = 300f;
        [Tooltip("Metres to shift every frame, e.g. to sink feet drawn above the picture's bottom edge.")]
        [SerializeField] internal Vector2 offset;

        MeshRenderer _renderer;
        MaterialPropertyBlock _block;
        Texture2D _frame;
        bool _mirror;
        Color _tint = Color.white;

        public Texture2D Frame => _frame;
        public Vector2 Size { get; private set; }

        /// <summary>Shows <paramref name="frame"/>; does nothing for a missing frame, so a gap in the art keeps the last pose.</summary>
        public void Show(Texture2D frame, bool mirror = false)
        {
            if (frame == null || (frame == _frame && mirror == _mirror)) return;
            _frame = frame;
            _mirror = mirror;
            Apply();
            float w = frame.width / pixelsPerMetre;
            float h = frame.height / pixelsPerMetre;
            Size = new Vector2(w, h);
            transform.localScale = new Vector3(mirror ? -w : w, h, 1f);
            transform.localPosition = new Vector3(offset.x, h * 0.5f + offset.y, transform.localPosition.z);
        }

        /// <summary>Multiplies the art by <paramref name="tint"/> (the chilli glow).</summary>
        public void SetTint(Color tint)
        {
            if (tint == _tint) return;
            _tint = tint;
            Apply();
        }

        void Apply()
        {
            if (_renderer == null) _renderer = GetComponent<MeshRenderer>();
            if (_block == null) _block = new MaterialPropertyBlock();
            _renderer.GetPropertyBlock(_block);
            if (_frame != null) _block.SetTexture(MainTexId, _frame);
            _block.SetColor(TintId, _tint);
            _renderer.SetPropertyBlock(_block);
        }
    }
}
