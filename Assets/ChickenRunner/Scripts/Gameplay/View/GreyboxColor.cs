using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Tints a grey-box mesh through a property block, so every prop can share one material
    /// in either the Built-in or the Universal render pipeline (it sets both _Color and _BaseColor).
    /// </summary>
    [ExecuteAlways, RequireComponent(typeof(Renderer))]
    public sealed class GreyboxColor : MonoBehaviour
    {
        static readonly int s_baseColor = Shader.PropertyToID("_BaseColor");
        static readonly int s_color = Shader.PropertyToID("_Color");
        static MaterialPropertyBlock s_block;

        [SerializeField] internal Color color = Color.white;

        public Color Color => color;

        public void SetColor(Color value)
        {
            color = value;
            Apply();
        }

        void OnEnable() => Apply();
        void OnValidate() => Apply();

        void Apply()
        {
            var target = GetComponent<Renderer>();
            if (target == null) return;
            s_block ??= new MaterialPropertyBlock();
            target.GetPropertyBlock(s_block);
            s_block.SetColor(s_baseColor, color);
            s_block.SetColor(s_color, color);
            target.SetPropertyBlock(s_block);
        }
    }
}
