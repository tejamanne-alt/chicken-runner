using ChickenRunner.Core;
using UnityEditor;
using UnityEngine;

namespace ChickenRunner.EditorTools
{
    /// <summary>
    /// Shows what the tuning numbers add up to (jump length, metres per mistake, clean catch time)
    /// and warns where they break a promise in the design doc.
    /// </summary>
    [CustomEditor(typeof(TuningConfig))]
    public sealed class TuningConfigEditor : Editor
    {
        TuningReport _report;

        public override void OnInspectorGUI()
        {
            EditorGUI.BeginChangeCheck();
            DrawDefaultInspector();
            bool changed = EditorGUI.EndChangeCheck();

            var config = (TuningConfig)target;
            if (_report == null || changed) _report = TuningReport.Build(config.Values);

            EditorGUILayout.Space();
            EditorGUILayout.LabelField("What these numbers add up to", EditorStyles.boldLabel);
            foreach (var line in _report.Lines) EditorGUILayout.LabelField(line.Key, line.Value);

            foreach (var warning in _report.Warnings) EditorGUILayout.HelpBox(warning, MessageType.Warning);

            EditorGUILayout.Space();
            if (GUILayout.Button("Reset to design-doc values for zone " + config.Zone))
            {
                Undo.RecordObject(config, "Reset tuning");
                config.ResetToDesignValues();
                EditorUtility.SetDirty(config);
                _report = null;
            }
        }
    }
}
