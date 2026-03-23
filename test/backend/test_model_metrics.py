#!/usr/bin/env python3
"""MD-01 / MD-02: Evaluacion de metrica de modelo con etiquetas reales y predichas.

Entrada esperada CSV:
- y_true
- y_pred

Criterios de aceptacion (plan_pruebas):
- Accuracy > 85%
- Sensitivity > 80%
- Specificity > 80%
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set


LABEL_MAP = {
    "atrial_fibrillation": "supraventricular_ectopic",
    "atrial_flutter": "supraventricular_ectopic",
    "svt_paroxysmal": "supraventricular_ectopic",
    "premature_atrial_complex": "supraventricular_ectopic",
    "wandering_atrial_pacemaker": "supraventricular_ectopic",
    "sinus_tachycardia": "normal",
    "sinus_bradycardia": "normal",
    "ventricular_tachycardia": "ventricular_ectopic",
    "ventricular_fibrillation": "ventricular_ectopic",
    "torsade_de_pointes": "ventricular_ectopic",
    "pvc_quadrigeminy": "ventricular_ectopic",
    "av_block": "paced",
    "asystole": "unknown",
}


def normalize_label(label: str) -> str:
    value = str(label or "").strip().lower()
    if not value:
        return "unknown"
    return LABEL_MAP.get(value, value)


def load_labels(csv_path: Path) -> List[Dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"y_true", "y_pred"}
        if not required.issubset(reader.fieldnames or set()):
            raise ValueError("El CSV debe contener columnas: y_true,y_pred")
        rows = [row for row in reader if row.get("y_true") and row.get("y_pred")]
    if not rows:
        raise ValueError("El CSV no contiene filas validas con y_true/y_pred")
    normalized_rows: List[Dict[str, str]] = []
    for row in rows:
        normalized_rows.append(
            {
                "y_true": normalize_label(row["y_true"]),
                "y_pred": normalize_label(row["y_pred"]),
            }
        )
    return normalized_rows


def compute_metrics(rows: List[Dict[str, str]]) -> Dict[str, float]:
    classes: Set[str] = set()
    for r in rows:
        classes.add(r["y_true"])
        classes.add(r["y_pred"])

    labels = sorted(classes)

    confusion = defaultdict(lambda: defaultdict(int))
    correct = 0
    for r in rows:
        y_true = r["y_true"]
        y_pred = r["y_pred"]
        confusion[y_true][y_pred] += 1
        if y_true == y_pred:
            correct += 1

    total = len(rows)
    accuracy = correct / total

    sensitivities: List[float] = []
    specificities: List[float] = []
    specificity_not_applicable = 0

    for cls in labels:
        tp = confusion[cls][cls]
        fn = sum(confusion[cls][c] for c in labels if c != cls)
        fp = sum(confusion[c][cls] for c in labels if c != cls)
        tn = total - tp - fn - fp

        sens = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        if (tn + fp) > 0:
            spec = tn / (tn + fp)
            specificities.append(spec)
        else:
            specificity_not_applicable += 1
        sensitivities.append(sens)

    sensitivity_macro = sum(sensitivities) / len(sensitivities)
    specificity_macro = None
    if specificities:
        specificity_macro = sum(specificities) / len(specificities)

    return {
        "accuracy": accuracy,
        "sensitivity_macro": sensitivity_macro,
        "specificity_macro": specificity_macro,
        "specificity_not_applicable_classes": float(specificity_not_applicable),
        "num_samples": float(total),
        "num_classes": float(len(labels)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalua metricas de clasificacion desde CSV")
    parser.add_argument("--predictions", required=True, help="CSV con y_true,y_pred")
    parser.add_argument("--min-accuracy", type=float, default=0.85)
    parser.add_argument("--min-sensitivity", type=float, default=0.80)
    parser.add_argument("--min-specificity", type=float, default=0.80)
    parser.add_argument("--report", default="", help="Ruta opcional de salida JSON")
    args = parser.parse_args()

    rows = load_labels(Path(args.predictions))
    m = compute_metrics(rows)

    specificity_ok = True
    if m["specificity_macro"] is not None:
        specificity_ok = m["specificity_macro"] > args.min_specificity

    checks = {
        "MD-01_accuracy": m["accuracy"] > args.min_accuracy,
        "MD-02_sensitivity": m["sensitivity_macro"] > args.min_sensitivity,
        "specificity": specificity_ok,
    }
    passed = all(checks.values())

    report = {
        "test_ids": ["MD-01", "MD-02"],
        "input": args.predictions,
        "metrics": {
            "accuracy": round(m["accuracy"], 6),
            "sensitivity_macro": round(m["sensitivity_macro"], 6),
            "specificity_macro": round(m["specificity_macro"], 6) if m["specificity_macro"] is not None else None,
            "specificity_not_applicable_classes": int(m["specificity_not_applicable_classes"]),
            "num_samples": int(m["num_samples"]),
            "num_classes": int(m["num_classes"]),
        },
        "thresholds": {
            "min_accuracy": args.min_accuracy,
            "min_sensitivity": args.min_sensitivity,
            "min_specificity": args.min_specificity,
        },
        "checks": checks,
        "passed": passed,
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.report:
        p = Path(args.report)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
