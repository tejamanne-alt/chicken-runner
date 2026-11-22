using UnityEngine;

namespace ChickenRunner
{
    /// <summary>
    /// Pooled little cubes for pot shards, feathers, dust and splats. Grey-box stand-in for the particle pass;
    /// it needs no assets, so it renders with whichever render pipeline the project uses.
    /// </summary>
    public sealed class Debris : MonoBehaviour
    {
        const int PoolSize = 96;
        const float Gravity = 14f;

        struct Piece
        {
            public Transform transform;
            public Renderer renderer;
            public Vector3 velocity;
            public Vector3 spin;
            public float size;
            public float age;
            public float lifetime;
            public float gravityScale;
            public bool alive;
        }

        static Debris s_instance;
        static readonly int s_baseColor = Shader.PropertyToID("_BaseColor");
        static readonly int s_color = Shader.PropertyToID("_Color");

        Piece[] _pieces;
        MaterialPropertyBlock _block;
        int _next;

        /// <summary>Throws <paramref name="count"/> pieces outward and upward from <paramref name="position"/>.</summary>
        public static void Burst(Vector3 position, Color color, int count, float speed, float size, float gravityScale = 1f)
        {
            if (!Application.isPlaying) return;
            var debris = Instance;
            for (int i = 0; i < count; i++)
            {
                var direction = new Vector3(Random.Range(-1f, 1f), Random.Range(0.4f, 1.2f), Random.Range(-0.6f, 0.6f));
                float lifetime = (0.6f + Random.value * 0.4f) * (gravityScale < 1f ? 2f : 1f);
                debris.Spawn(position, direction * speed, color, size * Random.Range(0.6f, 1.3f), lifetime, gravityScale);
            }
        }

        /// <summary>Feathers drift: low gravity, air drag and a longer life.</summary>
        public static void Feathers(Vector3 position, Color color, int count) => Burst(position, color, count, 2.5f, 0.09f, 0.15f);

        public static void ClearAll()
        {
            if (s_instance == null) return;
            for (int i = 0; i < s_instance._pieces.Length; i++) s_instance.Kill(i);
        }

        static Debris Instance
        {
            get
            {
                if (s_instance == null) s_instance = new GameObject("Debris").AddComponent<Debris>();
                return s_instance;
            }
        }

        void Awake()
        {
            _block = new MaterialPropertyBlock();
            _pieces = new Piece[PoolSize];
            for (int i = 0; i < PoolSize; i++)
            {
                var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
                DestroyImmediate(cube.GetComponent<Collider>());
                cube.name = "Piece";
                cube.transform.SetParent(transform, false);
                cube.SetActive(false);
                _pieces[i] = new Piece { transform = cube.transform, renderer = cube.GetComponent<Renderer>() };
            }
        }

        void OnDestroy()
        {
            if (s_instance == this) s_instance = null;
        }

        void Spawn(Vector3 position, Vector3 velocity, Color color, float size, float lifetime, float gravityScale)
        {
            ref var piece = ref _pieces[_next];
            _next = (_next + 1) % _pieces.Length;

            piece.alive = true;
            piece.age = 0f;
            piece.lifetime = lifetime;
            piece.size = size;
            piece.velocity = velocity;
            piece.gravityScale = gravityScale;
            piece.spin = Random.insideUnitSphere * (gravityScale < 1f ? 240f : 720f);

            piece.transform.position = position;
            piece.transform.rotation = Random.rotation;
            piece.transform.localScale = Vector3.one * size;
            piece.transform.gameObject.SetActive(true);

            _block.SetColor(s_baseColor, color);
            _block.SetColor(s_color, color);
            piece.renderer.SetPropertyBlock(_block);
        }

        void Update()
        {
            float dt = Time.deltaTime;
            for (int i = 0; i < _pieces.Length; i++)
            {
                ref var piece = ref _pieces[i];
                if (!piece.alive) continue;
                piece.age += dt;
                if (piece.age >= piece.lifetime)
                {
                    Kill(i);
                    continue;
                }
                piece.velocity.y -= Gravity * piece.gravityScale * dt;
                if (piece.gravityScale < 1f) piece.velocity *= Mathf.Max(0f, 1f - 2f * dt);
                piece.transform.position += piece.velocity * dt;
                piece.transform.Rotate(piece.spin * dt);
                piece.transform.localScale = Vector3.one * (piece.size * (1f - piece.age / piece.lifetime));
            }
        }

        void Kill(int index)
        {
            ref var piece = ref _pieces[index];
            piece.alive = false;
            if (piece.transform != null) piece.transform.gameObject.SetActive(false);
        }
    }
}
