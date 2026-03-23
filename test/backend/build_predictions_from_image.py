#!/usr/bin/env python3
"""Construye CSV y_true,y_pred para una sola imagen usando el endpoint real.

Normaliza etiquetas del dataset (arrhythmia_type) al esquema del backend:
normal, supraventricular_ectopic, ventricular_ectopic, fusion, unknown, paced.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import requests


ARRHYTHMIA_MAP = {
    "v": "ventricular_ectopic",
    "ventricular": "ventricular_ectopic",
    "ventricular_ectopic": "ventricular_ectopic",
    "n": "normal",
    "normal": "normal",
    "s": "supraventricular_ectopic",
    "supraventricular": "supraventricular_ectopic",
    "supraventricular_ectopic": "supraventricular_ectopic",
    "f": "fusion",
    "fusion": "fusion",
    "q": "unknown",
    "unknown": "unknown",
    "p": "paced",
    "paced": "paced",
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


def normalize_true_label(raw_label: str) -> str:
    value = str(raw_label or "").strip().lower()
    if not value:
        return "unknown"
    return ARRHYTHMIA_MAP.get(value, "unknown")


def infer_true_label_from_questions(image_name: str, questions_path: Path) -> str:
    if not questions_path.exists():
        return "unknown"

    data = json.loads(questions_path.read_text(encoding="utf-8"))
    for q in data.get("questions", []):
        if q.get("image_filename") == image_name:
            raw = str(q.get("arrhythmia_type", "unknown"))
            return normalize_true_label(raw)
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera CSV de prediccion para una imagen")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--image", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--questions-json",
        default="backend/train/ecg_questions.json",
        help="Ruta a ecg_questions.json para inferir y_true",
    )
    parser.add_argument(
        "--true-label",
        default="",
        help="Etiqueta real manual (ej. V, N, S, F, Q, P). Si se indica, tiene prioridad.",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"Imagen no encontrada: {image_path}")

    if args.true_label:
        y_true = normalize_true_label(args.true_label)
    else:
        y_true = infer_true_label_from_questions(image_path.name, Path(args.questions_json))

    ts = int(time.time() * 1000)
    email = f"auto_single_{ts}@example.com"
    password = "QaPassword123!"

    reg_payload = {
        "name": "Auto Single",
        "email": email,
        "password": password,
        "user_type": "student",
        "institution": "QA",
    }
    requests.post(f"{base_url}/auth/register", json=reg_payload, timeout=30)

    login = requests.post(
        f"{base_url}/auth/login",
        json={"email": email, "password": password},
        timeout=30,
    )
    login.raise_for_status()

    token = login.json().get("access_token", "")
    if not token:
        raise SystemExit("No se obtuvo token de acceso")

    with image_path.open("rb") as f:
        classify = requests.post(
            f"{base_url}/ecg/classify",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": (image_path.name, f, "image/png")},
            timeout=180,
        )

    if classify.status_code != 200:
        y_pred = "unknown"
    else:
        y_pred = classify.json().get("predicted_class", "unknown")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["y_true", "y_pred"])
        writer.writeheader()
        writer.writerow({"y_true": y_true, "y_pred": y_pred})

    print(str(out))
    print(f"y_true={y_true}")
    print(f"y_pred={y_pred}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
