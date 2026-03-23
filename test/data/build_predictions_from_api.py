import csv
import json
import time
from pathlib import Path

import requests


def main():
    base = "http://localhost:8000"
    train = Path("backend/train")
    questions = json.loads((train / "ecg_questions.json").read_text(encoding="utf-8"))["questions"]

    labels = {}
    for q in questions:
        img = q.get("image_filename")
        if img and img not in labels:
            labels[img] = q.get("arrhythmia_type", "unknown")

    email = f"auto_md_{int(time.time()*1000)}@example.com"
    password = "QaPassword123!"
    reg = {
        "name": "Auto MD",
        "email": email,
        "password": password,
        "user_type": "student",
        "institution": "QA",
    }

    requests.post(f"{base}/auth/register", json=reg, timeout=30)
    login = requests.post(
        f"{base}/auth/login",
        json={"email": email, "password": password},
        timeout=30,
    )
    login.raise_for_status()
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    out_csv = Path("test/data/predictions_from_api.csv")
    out_debug = Path("test/data/predictions_from_api_debug.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for img_name, y_true in labels.items():
        img_path = train / img_name
        if not img_path.exists():
            continue

        with img_path.open("rb") as f:
            r = requests.post(
                f"{base}/ecg/classify",
                headers=headers,
                files={"file": (img_path.name, f, "image/png")},
                timeout=180,
            )

        if r.status_code == 200:
            y_pred = r.json().get("predicted_class", "unknown")
        else:
            y_pred = "unknown"

        rows.append({
            "image": img_name,
            "y_true": y_true,
            "y_pred": y_pred,
            "status": r.status_code,
        })

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["y_true", "y_pred"])
        w.writeheader()
        for row in rows:
            w.writerow({"y_true": row["y_true"], "y_pred": row["y_pred"]})

    with out_debug.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["image", "y_true", "y_pred", "status"])
        w.writeheader()
        w.writerows(rows)

    print(str(out_csv))
    print(str(out_debug))
    print(f"rows={len(rows)}")


if __name__ == "__main__":
    main()
