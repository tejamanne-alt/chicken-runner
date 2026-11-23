// The painted ground: a tile laid in world space (so the lane's chunks and the big plane behind them meet with no seam),
// broken up by a second, turned and larger sample and by slow light and dark drifts so the red earth never shows a
// repeating pattern. Optionally a second texture (zone 2's paddy water) away from the lane band, and the same distance
// haze as the painted cards. Matches earth_material() and haze_amount() in ArtSource/tools/ground.py.
Shader "ChickenRunner/PaintedGround"
{
    Properties
    {
        _MainTex ("Earth tile", 2D) = "white" {}
        _Tile ("Metres per earth tile", Float) = 3.5
        _Tint ("Tint", Color) = (1, 1, 1, 1)
        _Drift ("Light and dark drifts", Range(0, 0.5)) = 0.14
        [Toggle] _UseFar ("Field texture away from the lane", Float) = 0
        _FarTex ("Field tile", 2D) = "white" {}
        _FarTile ("Metres per field tile", Float) = 6
        _BandFront ("Lane band front edge (depth)", Float) = -1.8
        _BandBack ("Lane band back edge (depth)", Float) = 1.8
        _BandSoft ("Band edge softness (m)", Float) = 0.5
        _HazeColor ("Haze colour", Color) = (0.98, 0.765, 0.545, 1)
        _HazeFrom ("Haze starts (depth)", Float) = 6
        _HazeTo ("Haze is full (depth)", Float) = 40
        _HazePower ("Haze curve", Float) = 0.85
    }
    SubShader
    {
        Tags { "Queue" = "Geometry" "RenderType" = "Opaque" }

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            sampler2D _MainTex;
            sampler2D _FarTex;
            float _Tile;
            float _FarTile;
            fixed4 _Tint;
            float _Drift;
            float _UseFar;
            float _BandFront;
            float _BandBack;
            float _BandSoft;
            fixed4 _HazeColor;
            float _HazeFrom;
            float _HazeTo;
            float _HazePower;

            struct appdata { float4 vertex : POSITION; };
            struct v2f { float4 pos : SV_POSITION; float3 world : TEXCOORD0; };

            v2f vert (appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                o.world = mul(unity_ObjectToWorld, v.vertex).xyz;
                return o;
            }

            // Two samples of one tile, the second turned and larger, mixed by a slow wave: no visible repeat.
            fixed3 Tiled (sampler2D tex, float2 p, float tile)
            {
                float2 uv = p / tile;
                float2 turned = float2(uv.x * 0.8 - uv.y * 0.6, uv.x * 0.6 + uv.y * 0.8) * 0.63 + 0.37;
                float mixer = 0.5 + 0.5 * sin(p.x * 0.21 + sin(p.y * 0.17) * 2.3) * sin(p.y * 0.13 + p.x * 0.05);
                return lerp(tex2D(tex, uv).rgb, tex2D(tex, turned).rgb, smoothstep(0.25, 0.75, mixer));
            }

            fixed4 frag (v2f i) : SV_Target
            {
                float2 p = i.world.xz;
                fixed3 c = Tiled(_MainTex, p, _Tile);
                // Broad drifts of lighter and darker earth, metres across.
                float drift = sin(p.x * 0.09 + p.y * 0.05) * sin(p.x * 0.031 - p.y * 0.11 + 1.7);
                c *= 1 + _Drift * drift;

                if (_UseFar > 0.5)
                {
                    float band = smoothstep(_BandFront - _BandSoft, _BandFront, p.y)
                        * (1 - smoothstep(_BandBack, _BandBack + _BandSoft, p.y));
                    c = lerp(Tiled(_FarTex, p, _FarTile), c, band);
                }

                c *= _Tint.rgb;
                float haze = pow(saturate((p.y - _HazeFrom) / max(0.01, _HazeTo - _HazeFrom)), _HazePower);
                c = lerp(c, _HazeColor.rgb, haze);
                return fixed4(c, 1);
            }
            ENDCG
        }
    }
}
