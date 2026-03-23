#!/usr/bin/env python3
"""FN-01 / FN-02: Pruebas funcionales de API para carga y clasificacion ECG.

Flujo:
1) /health
2) /auth/register (usuario temporal)
3) /auth/login
4) /ecg/classify (multipart con imagen)
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests


def main() -> int:
    parser = argparse.ArgumentParser(description="Prueba funcional de API TrainECG")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--image", required=True, help="Ruta a imagen ECG para clasificar")
    parser.add_argument("--report", default="", help="Ruta opcional para reporte JSON")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"Imagen no encontrada: {image_path}")

    ts = int(time.time() * 1000)
    email = f"qa_{ts}@example.com"
    password = "QaPassword123!"

    checks = {}
    details = {}

    # 1. Health
    r = requests.get(f"{base_url}/health", timeout=20)
    checks["health_200"] = r.status_code == 200
    details["health_status"] = r.status_code

    # 2. Register
    reg_payload = {
        "name": "QA User",
        "email": email,
        "password": password,
        "user_type": "student",
        "institution": "QA Institute",
    }
    r = requests.post(f"{base_url}/auth/register", json=reg_payload, timeout=30)
    checks["register_success"] = r.status_code in (200, 201)
    details["register_status"] = r.status_code

    # 3. Login
    login_payload = {"email": email, "password": password}
    r = requests.post(f"{base_url}/auth/login", json=login_payload, timeout=30)
    checks["login_success"] = r.status_code == 200
    details["login_status"] = r.status_code

    token = ""
    if r.status_code == 200:
        token = r.json().get("access_token", "")
    checks["token_present"] = bool(token)

    # 4. Classify
    classify_status = None
    classify_json = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        with image_path.open("rb") as f:
            files = {"file": (image_path.name, f, "image/png")}
            r = requests.post(f"{base_url}/ecg/classify", files=files, headers=headers, timeout=120)
        classify_status = r.status_code
        details["classify_status"] = classify_status
        if r.headers.get("content-type", "").startswith("application/json"):
            classify_json = r.json()

    checks["FN-01_upload_and_display_pipeline"] = classify_status == 200
    checks["FN-02_prediction_generated"] = bool(classify_json.get("predicted_class")) and (
        classify_json.get("confidence") is not None
    )

    passed = all(checks.values())

    report = {
        "test_ids": ["FN-01", "FN-02"],
        "base_url": base_url,
        "image": str(image_path),
        "checks": checks,
        "details": details,
        "response_excerpt": {
            "predicted_class": classify_json.get("predicted_class"),
            "confidence": classify_json.get("confidence"),
            "processing_time_ms": classify_json.get("processing_time_ms"),
        },
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
