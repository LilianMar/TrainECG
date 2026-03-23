#!/usr/bin/env python3
"""CD-01 / CD-02: Validacion de calidad de datos para imagenes ECG.

Criterios (configurables):
- Todas las imagenes con la misma dimension y canales.
- Distribucion de clases balanceada (ratio max/min <= umbral).
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

from PIL import Image

VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def find_class_dirs(dataset_root: Path) -> List[Path]:
    return sorted([p for p in dataset_root.iterdir() if p.is_dir()])


def find_images(class_dir: Path) -> List[Path]:
    files: List[Path] = []
    for root, _, filenames in os.walk(class_dir):
        for name in filenames:
            p = Path(root) / name
            if p.suffix.lower() in VALID_EXTENSIONS:
                files.append(p)
    return sorted(files)


def inspect_image(path: Path) -> Tuple[Tuple[int, int], str]:
    with Image.open(path) as img:
        return img.size, img.mode


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida calidad de dataset ECG por clases")
    parser.add_argument("--dataset", required=True, help="Ruta raiz del dataset (clases en subcarpetas)")
    parser.add_argument(
        "--max-imbalance-ratio",
        type=float,
        default=1.5,
        help="Maximo ratio permitido entre clase mayoritaria y minoritaria (default: 1.5)",
    )
    parser.add_argument(
        "--max-unique-sizes",
        type=int,
        default=1,
        help="Maximo numero de dimensiones distintas permitidas (default: 1)",
    )
    parser.add_argument(
        "--max-unique-channels",
        type=int,
        default=1,
        help="Maximo numero de modos/canales distintos permitidos (default: 1)",
    )
    parser.add_argument("--report", default="", help="Ruta opcional para guardar reporte JSON")
    args = parser.parse_args()

    dataset_root = Path(args.dataset).resolve()
    if not dataset_root.exists() or not dataset_root.is_dir():
        raise SystemExit(f"Dataset no valido: {dataset_root}")

    class_dirs = find_class_dirs(dataset_root)
    if not class_dirs:
        raise SystemExit("No se encontraron subcarpetas de clases en el dataset")

    class_counts: Dict[str, int] = {}
    dimensions = Counter()
    channels = Counter()
    invalid_files: List[str] = []

    for class_dir in class_dirs:
        images = find_images(class_dir)
        class_counts[class_dir.name] = len(images)

        for image_path in images:
            try:
                size, mode = inspect_image(image_path)
                dimensions[f"{size[0]}x{size[1]}"] += 1
                channels[mode] += 1
            except Exception:
                invalid_files.append(str(image_path))

    non_empty_counts = [c for c in class_counts.values() if c > 0]
    if not non_empty_counts:
        raise SystemExit("No se encontraron imagenes validas en el dataset")

    max_count = max(non_empty_counts)
    min_count = min(non_empty_counts)
    imbalance_ratio = float(max_count) / float(min_count)

    dominant_dim = dimensions.most_common(1)[0][0] if dimensions else "N/A"
    dominant_mode = channels.most_common(1)[0][0] if channels else "N/A"

    size_ok = len(dimensions) <= args.max_unique_sizes
    channels_ok = len(channels) <= args.max_unique_channels
    balance_ok = imbalance_ratio <= args.max_imbalance_ratio
    files_ok = len(invalid_files) == 0

    passed = size_ok and channels_ok and balance_ok and files_ok

    report = {
        "test_ids": ["CD-01", "CD-02"],
        "dataset_root": str(dataset_root),
        "class_counts": class_counts,
        "dominant_size": dominant_dim,
        "dominant_channels": dominant_mode,
        "unique_sizes": dict(dimensions),
        "unique_channels": dict(channels),
        "invalid_files": invalid_files,
        "imbalance_ratio": round(imbalance_ratio, 4),
        "max_imbalance_ratio": args.max_imbalance_ratio,
        "max_unique_sizes": args.max_unique_sizes,
        "max_unique_channels": args.max_unique_channels,
        "checks": {
            "uniform_size": size_ok,
            "uniform_channels": channels_ok,
            "balanced_distribution": balance_ok,
            "readable_images": files_ok,
        },
        "passed": passed,
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
