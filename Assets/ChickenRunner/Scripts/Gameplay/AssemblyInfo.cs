using System.Runtime.CompilerServices;

// The grey-box builder wires serialized fields directly instead of by string name.
[assembly: InternalsVisibleTo("ChickenRunner.Editor")]
