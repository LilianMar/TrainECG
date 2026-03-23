#!/usr/bin/env python3
"""US-01: Evaluacion de usabilidad desde encuesta CSV.

Entrada CSV esperada:
- participant_id
- role (doctor|student|resident|other)
- intuitive_score (1-5)

Criterio de aceptacion:
- >= 80% de participantes con intuitive_score >= 4.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalua criterio US-01 desde encuesta")
    parser.add_argument("--survey", required=True, help="CSV de respuestas de usabilidad")
    parser.add_argument("--min-intuitive-rate", type=float, default=0.8)
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    survey_path = Path(args.survey)
    if not survey_path.exists():
        raise SystemExit(f"Archivo de encuesta no encontrado: {survey_path}")

    rows = []
    with survey_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"participant_id", "role", "intuitive_score"}
        if not required.issubset(reader.fieldnames or set()):
            raise SystemExit("CSV invalido. Se requieren columnas: participant_id,role,intuitive_score")
        for row in reader:
            try:
                score = int(row["intuitive_score"])
            except Exception:
                continue
            rows.append({**row, "intuitive_score": score})

    if not rows:
        raise SystemExit("No hay respuestas validas para evaluar")

    intuitive_count = sum(1 for r in rows if r["intuitive_score"] >= 4)
    intuitive_rate = intuitive_count / len(rows)

    checks = {
        "US-01_intuitive_rate": intuitive_rate >= args.min_intuitive_rate,
    }
    passed = all(checks.values())

    report = {
        "test_ids": ["US-01"],
        "survey": str(survey_path),
        "participants": len(rows),
        "intuitive_count": intuitive_count,
        "intuitive_rate": round(intuitive_rate, 4),
        "threshold": args.min_intuitive_rate,
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
