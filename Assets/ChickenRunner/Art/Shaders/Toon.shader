// Toon shading for the 3D kid, rooster and pickups, matching how ArtSource/tools/characters renders them: flat
// colour in two tones split by a fixed light from the front-left-top (the painted art's light, not the scene's), a
// soft cool shadow, an optional small hard highlight, and a dark ink outline from an inverted hull. Unlit otherwise, so
// the characters sit with the painted cards. Works on skinned meshes.
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
            fixed4 _OutlineColor;
            float _OutlineWidth;
            struct appdata { float4 vertex : POSITION; float3 normal : NORMAL; };
            float4 vert (appdata v) : SV_POSITION
            {
                float3 world = mul(unity_ObjectToWorld, v.vertex).xyz;
                float3 n = normalize(mul((float3x3)unity_ObjectToWorld, v.normal));
                return UnityWorldToClipPos(world + n * _OutlineWidth);
            }
            fixed4 frag () : SV_Target { return _OutlineColor; }
            ENDCG
        }

        Pass
        {
            Name "Toon"
            Cull Back
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
                float3 n = normalize(i.normal);
                float3 l = normalize(_LightDir.xyz);
                float lit = smoothstep(_Threshold - _Softness, _Threshold + _Softness, dot(n, l));
                fixed3 c = lerp(base.rgb * _ShadowTint.rgb, base.rgb, lit);
                if (_Gloss > 0)
                {
                    float spec = smoothstep(0.93, 0.96, dot(n, normalize(l + i.view)));
                    c = 1 - (1 - c) * (1 - spec * _Gloss * 0.9);
                }
                return fixed4(c, 1);
            }
            ENDCG
        }
    }
    Fallback "Unlit/Texture"
}
