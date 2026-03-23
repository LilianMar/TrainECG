#!/usr/bin/env bash
set -uo pipefail

# Uso:
# ./test/run_plan_pruebas.sh --base-url http://localhost:8000 --image backend/train/ecg_case_1.png --predictions test/data/predictions.csv --dataset /ruta/dataset --survey test/usability/usability_survey_template.csv

BASE_URL="http://localhost:8000"
IMAGE="backend/train/ecg_case_1.png"
PREDICTIONS=""
DATASET=""
SURVEY="test/usability/usability_survey_template.csv"
REPORT_DIR="test/reports"
MODE="pilot"
PYTHON_BIN="${PYTHON_BIN:-python3}"
TRUE_LABEL=""

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Uso:
  ./test/run_plan_pruebas.sh [opciones]

Opciones:
  --base-url URL         URL base backend (default: http://localhost:8000)
  --image PATH           Imagen ECG para FN/PR (default: backend/train/ecg_case_1.png)
  --dataset PATH         Dataset por clases para CD
  --predictions PATH     CSV y_true,y_pred para MD
  --survey PATH          CSV de usabilidad para US (default: test/usability/usability_survey_template.csv)
  --report-dir PATH      Carpeta de reportes JSON (default: test/reports)
  --mode MODE            strict|pilot (default: pilot)
  --true-label LABEL     Etiqueta real manual para MD (ej: V, N, S, F, Q, P)
  -h, --help             Mostrar esta ayuda
EOF
  exit 0
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-url) BASE_URL="$2"; shift 2 ;;
    --image) IMAGE="$2"; shift 2 ;;
    --predictions) PREDICTIONS="$2"; shift 2 ;;
    --dataset) DATASET="$2"; shift 2 ;;
    --survey) SURVEY="$2"; shift 2 ;;
    --report-dir) REPORT_DIR="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --true-label) TRUE_LABEL="$2"; shift 2 ;;
    *) echo "Argumento no reconocido: $1"; exit 2 ;;
  esac
done

if [[ "$MODE" != "strict" && "$MODE" != "pilot" ]]; then
  echo "Modo no valido: $MODE (use strict o pilot)"
  exit 2
fi

if [[ "$MODE" == "pilot" ]]; then
  MAX_SECONDS=10
  MAX_IMBALANCE=3.0
  MAX_UNIQUE_SIZES=6
  MAX_UNIQUE_CHANNELS=3
  MIN_ACCURACY=0.70
  MIN_SENSITIVITY=0.65
  MIN_SPECIFICITY=0.65
  MIN_INTUITIVE_RATE=0.65
else
  MAX_SECONDS=5
  MAX_IMBALANCE=1.5
  MAX_UNIQUE_SIZES=1
  MAX_UNIQUE_CHANNELS=1
  MIN_ACCURACY=0.85
  MIN_SENSITIVITY=0.80
  MIN_SPECIFICITY=0.80
  MIN_INTUITIVE_RATE=0.80
fi

mkdir -p "$REPORT_DIR"
OVERALL_PASSED=true

echo "[FN] Pruebas funcionales API"
"$PYTHON_BIN" test/backend/test_functional_api.py \
  --base-url "$BASE_URL" \
  --image "$IMAGE" \
  --report "$REPORT_DIR/functional.json"
if [[ $? -ne 0 ]]; then
  OVERALL_PASSED=false
fi

echo "[PR] Prueba de rendimiento API"
"$PYTHON_BIN" test/backend/test_performance_api.py \
  --base-url "$BASE_URL" \
  --image "$IMAGE" \
  --runs 5 \
  --max-seconds "$MAX_SECONDS" \
  --report "$REPORT_DIR/performance.json"
if [[ $? -ne 0 ]]; then
  OVERALL_PASSED=false
fi

if [[ -n "$DATASET" ]]; then
  echo "[CD] Calidad de datos"
  "$PYTHON_BIN" test/backend/test_data_quality.py \
    --dataset "$DATASET" \
    --max-imbalance-ratio "$MAX_IMBALANCE" \
    --max-unique-sizes "$MAX_UNIQUE_SIZES" \
    --max-unique-channels "$MAX_UNIQUE_CHANNELS" \
    --report "$REPORT_DIR/data_quality.json"
  if [[ $? -ne 0 ]]; then
    OVERALL_PASSED=false
  fi
else
  echo "[CD] Omitido (sin --dataset)"
fi

if [[ -z "$PREDICTIONS" ]]; then
  echo "[MD] Generando predicciones desde imagen (modo $MODE)"
  PREDICTIONS="$REPORT_DIR/predictions_from_image.csv"
  "$PYTHON_BIN" test/backend/build_predictions_from_image.py \
    --base-url "$BASE_URL" \
    --image "$IMAGE" \
    --output "$PREDICTIONS" \
    --true-label "$TRUE_LABEL"
fi

if [[ -n "$PREDICTIONS" ]]; then
  GENERATED_TRUE_LABEL="$(tail -n +2 "$PREDICTIONS" | head -n 1 | cut -d',' -f1 | tr -d '\r')"
  echo "[MD] Metrica de modelo"
  if [[ "$GENERATED_TRUE_LABEL" == "unknown" ]]; then
    echo "[MD] Omitido: y_true=unknown (sin etiqueta real verificable para la imagen)"
    cat > "$REPORT_DIR/model_metrics.json" <<EOF
{
  "test_ids": ["MD-01", "MD-02"],
  "input": "$PREDICTIONS",
  "checks": {
    "MD-01_accuracy": null,
    "MD-02_sensitivity": null,
    "specificity": null
  },
  "passed": true,
  "skipped": true,
  "reason": "No hay etiqueta real verificable (y_true=unknown) para evaluar metricas supervisadas."
}
EOF
  else
    "$PYTHON_BIN" test/backend/test_model_metrics.py \
      --predictions "$PREDICTIONS" \
      --min-accuracy "$MIN_ACCURACY" \
      --min-sensitivity "$MIN_SENSITIVITY" \
      --min-specificity "$MIN_SPECIFICITY" \
      --report "$REPORT_DIR/model_metrics.json"
    if [[ $? -ne 0 ]]; then
      OVERALL_PASSED=false
    fi
  fi
else
  echo "[MD] Omitido (sin --predictions)"
fi

echo "[US] Usabilidad"
"$PYTHON_BIN" test/usability/evaluate_usability.py \
  --survey "$SURVEY" \
  --min-intuitive-rate "$MIN_INTUITIVE_RATE" \
  --report "$REPORT_DIR/usability.json"
if [[ $? -ne 0 ]]; then
  OVERALL_PASSED=false
fi

echo "Reportes generados en: $REPORT_DIR"
if [[ "$OVERALL_PASSED" == "true" ]]; then
  echo "Resultado global: PASS"
  exit 0
fi

echo "Resultado global: FAIL (revise los reportes JSON para detalle)"
exit 1
