// Toon shading for the 3D kid, rooster and pickups, matching how ArtSource/tools/characters renders them: flat
// colour in two tones split by a fixed light from the front-left-top (the painted art's light, not the scene's), a
// soft cool shadow, an optional small hard highlight, and a dark ink outline from an inverted hull. Unlit otherwise, so
// the characters sit with the painted cards. Works on skinned meshes.
// Leaf cards (the scenery models' M_<name>_Leaves): _Cutoff > 0 cuts the texture out by its alpha, _Cull 0 draws both
// sides (their normals point out of the crown, so both sides light alike), and _OutlineWidth 0 (cards have no hull).
// The outline pass draws nothing at width 0 and cuts out by alpha like the toon pass: otherwise it drew every card
// whose back faced the camera (a tuft's turned cards, a crown's leaves) as a solid ink square, with no cut-out.
Shader "ChickenRunner/Toon"
{
    Properties
    {
        _MainTex ("Albedo", 2D) = "white" {}
        _Color ("Colour", Color) = (1, 1, 1, 1)
        _ShadowTint ("Shadow tint", Color) = (0.7, 0.62, 0.78, 1)
        _LightDir ("Light direction (world, toward the light)", Vector) = (-0.45, 0.7, -0.55, 0)
        _Threshold ("Shadow edge", Range(-1, 1)) = 0.05
        _Softness ("Shadow edge softness", Range(0.001, 0.5)) = 0.04
        _Gloss ("Highlight strength", Range(0, 1)) = 0
        _OutlineColor ("Outline", Color) = (0.13, 0.07, 0.05, 1)
        _OutlineWidth ("Outline width (m)", Range(0, 0.02)) = 0.004
        _HazeColor ("Haze colour", Color) = (0.98, 0.765, 0.545, 1)
        _Haze ("Haze (distance)", Range(0, 1)) = 0
        _Cutoff ("Alpha cut-out (0 = opaque)", Range(0, 1)) = 0
        [Enum(UnityEngine.Rendering.CullMode)] _Cull ("Cull", Float) = 2
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" }

        Pass
        {
            Name "Outline"
            Cull Front
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            sampler2D _MainTex;
            float4 _MainTex_ST;
            fixed4 _OutlineColor;
            float _OutlineWidth;
            fixed4 _HazeColor;
            float _Haze;
            float _Cutoff;
            struct appdata { float4 vertex : POSITION; float3 normal : NORMAL; float2 uv : TEXCOORD0; };
            struct v2f { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; };
            v2f vert (appdata v)
            {
                v2f o;
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                // No outline (leaf cards): every vertex outside the clip volume on the same side, so nothing is drawn.
                if (_OutlineWidth <= 0) { o.pos = float4(2, 2, 2, 1); return o; }
                float3 world = mul(unity_ObjectToWorld, v.vertex).xyz;
                float3 n = normalize(mul((float3x3)unity_ObjectToWorld, v.normal));
                o.pos = UnityWorldToClipPos(world + n * _OutlineWidth);
                return o;
            }
            fixed4 frag (v2f i) : SV_Target
            {
                if (_Cutoff > 0) clip(tex2D(_MainTex, i.uv).a - _Cutoff);
                return fixed4(lerp(_OutlineColor.rgb, _HazeColor.rgb, _Haze), 1);
            }
            ENDCG
        }

        Pass
        {
            Name "Toon"
            Cull [_Cull]
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            sampler2D _MainTex;
            float4 _MainTex_ST;
            fixed4 _Color;
            fixed4 _ShadowTint;
            float4 _LightDir;
            float _Threshold;
            float _Softness;
            float _Gloss;
            fixed4 _HazeColor;
            float _Haze;
            float _Cutoff;
            struct appdata { float4 vertex : POSITION; float3 normal : NORMAL; float2 uv : TEXCOORD0; };
            struct v2f { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; float3 normal : TEXCOORD1; float3 view : TEXCOORD2; };
            v2f vert (appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                o.normal = UnityObjectToWorldNormal(v.normal);
                o.view = normalize(_WorldSpaceCameraPos - mul(unity_ObjectToWorld, v.vertex).xyz);
                return o;
            }
            fixed4 frag (v2f i) : SV_Target
            {
                fixed4 base = tex2D(_MainTex, i.uv) * _Color;
                if (_Cutoff > 0) clip(base.a - _Cutoff);
                float3 n = normalize(i.normal);
                float3 l = normalize(_LightDir.xyz);
                float lit = smoothstep(_Threshold - _Softness, _Threshold + _Softness, dot(n, l));
                fixed3 c = lerp(base.rgb * _ShadowTint.rgb, base.rgb, lit);
                if (_Gloss > 0)
                {
                    float spec = smoothstep(0.93, 0.96, dot(n, normalize(l + i.view)));
                    c = 1 - (1 - c) * (1 - spec * _Gloss * 0.9);
                }
                return fixed4(lerp(c, _HazeColor.rgb, _Haze), 1);
            }
            ENDCG
        }
    }
    Fallback "Unlit/Texture"
}
