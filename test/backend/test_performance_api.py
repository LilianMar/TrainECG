#!/usr/bin/env python3
"""PR-01: Medicion de tiempo de inferencia via endpoint /ecg/classify.

Criterio de aceptacion:
- Tiempo promedio < 5 segundos por ECG.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import requests


def register_and_login(base_url: str) -> str:
    ts = int(time.time() * 1000)
    email = f"perf_{ts}@example.com"
    password = "QaPassword123!"

    reg_payload = {
        "name": "Perf User",
        "email": email,
        "password": password,
        "user_type": "student",
        "institution": "QA Institute",
    }
    requests.post(f"{base_url}/auth/register", json=reg_payload, timeout=30)

    r = requests.post(
        f"{base_url}/auth/login",
        json={"email": email, "password": password},
        timeout=30,
    )
    r.raise_for_status()
    token = r.json().get("access_token", "")
    if not token:
        raise RuntimeError("No se obtuvo access_token para prueba de rendimiento")
    return token


def main() -> int:
    parser = argparse.ArgumentParser(description="Prueba de rendimiento de inferencia ECG")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--image", required=True)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--max-seconds", type=float, default=5.0)
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"Imagen no encontrada: {image_path}")

    token = register_and_login(base_url)
    headers = {"Authorization": f"Bearer {token}"}

    timings = []
    status_codes = []

    for _ in range(args.runs):
        start = time.perf_counter()
        with image_path.open("rb") as f:
            files = {"file": (image_path.name, f, "image/png")}
            r = requests.post(f"{base_url}/ecg/classify", files=files, headers=headers, timeout=180)
        elapsed = time.perf_counter() - start
        timings.append(elapsed)
        status_codes.append(r.status_code)

    success = all(code == 200 for code in status_codes)
    avg_s = statistics.mean(timings) if timings else float("inf")
    p95_s = sorted(timings)[max(0, int(round(0.95 * len(timings))) - 1)] if timings else float("inf")

    checks = {
        "all_requests_success": success,
        "PR-01_avg_inference_lt_threshold": avg_s < args.max_seconds,
    }
    passed = all(checks.values())

    report = {
        "test_ids": ["PR-01"],
        "base_url": base_url,
        "runs": args.runs,
        "threshold_seconds": args.max_seconds,
        "status_codes": status_codes,
        "timings_seconds": [round(t, 4) for t in timings],
        "summary": {
            "avg_seconds": round(avg_s, 4),
            "p95_seconds": round(p95_s, 4),
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
