// A painted cut-out card from the Blender scenes: the art as painted (unlit), alpha-blended, faded into the
// distance haze by _Haze (0 near, 1 where the ground ends), and optionally faded out at its foot and sides so it melts
// into the ground. Matches card_material() in ArtSource/tools/stage.py.
Shader "ChickenRunner/PaintedCard"
{
    Properties
    {
        _MainTex ("Art", 2D) = "white" {}
        _Tint ("Tint", Color) = (1, 1, 1, 1)
        _HazeColor ("Haze colour", Color) = (0.98, 0.765, 0.545, 1)
        _Haze ("Haze amount", Range(0, 1)) = 0
        _FadeBottom ("Fade at the foot (fraction of height)", Range(0, 0.5)) = 0
        _FadeSides ("Fade at the sides (fraction of width)", Range(0, 0.5)) = 0
    }
    SubShader
    {
        Tags { "Queue" = "Transparent" "RenderType" = "Transparent" "IgnoreProjector" = "True" }
        Cull Off
        ZWrite Off
        Blend SrcAlpha OneMinusSrcAlpha

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            float4 _MainTex_ST;
            fixed4 _Tint;
            fixed4 _HazeColor;
            float _Haze;
            float _FadeBottom;
            float _FadeSides;

            struct appdata { float4 vertex : POSITION; float2 uv : TEXCOORD0; };
            struct v2f { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; float2 raw : TEXCOORD1; };

            v2f vert (appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                o.raw = v.uv;
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                fixed4 c = tex2D(_MainTex, i.uv) * _Tint;
                if (_FadeBottom > 0) c.a *= smoothstep(0, _FadeBottom, i.raw.y);
                if (_FadeSides > 0) c.a *= smoothstep(0, _FadeSides, min(i.raw.x, 1 - i.raw.x));
                c.rgb = lerp(c.rgb, _HazeColor.rgb, _Haze);
                return c;
            }
            ENDCG
        }
    }
}
