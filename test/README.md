# Suite de pruebas basada en `plan_pruebas.tex`

Esta carpeta implementa scripts alineados con la sección de Plan de pruebas:

- `CD-01` y `CD-02`: calidad de datos
- `MD-01` y `MD-02`: métricas de modelo
- `FN-01` y `FN-02`: funcionalidad API
- `PR-01`: rendimiento de inferencia
- `US-01`: usabilidad

## Estructura

- `test/backend/test_data_quality.py`
- `test/backend/test_model_metrics.py`
- `test/backend/test_functional_api.py`
- `test/backend/test_performance_api.py`
- `test/usability/evaluate_usability.py`
- `test/usability/usability_survey_template.csv`
- `test/run_plan_pruebas.sh`

## Requisitos

- Backend corriendo en `http://localhost:8000` (o usar `--base-url`).
- Python 3.10+
- Dependencias del backend instaladas (`requests`, `Pillow`).

## Ejecución rápida

Desde `TrainECG_app`:

```bash
chmod +x test/run_plan_pruebas.sh
./test/run_plan_pruebas.sh \
  --base-url http://localhost:8000 \
  --image backend/train/ecg_case_1.png \
  --dataset /ruta/al/dataset_por_clases \
  --predictions /ruta/a/predictions.csv \
  --survey test/usability/usability_survey_template.csv
```

## Formatos de entrada

### Predicciones para métricas (`--predictions`)

CSV con columnas obligatorias:

```csv
y_true,y_pred
N,N
V,N
S,S
```

### Encuesta de usabilidad (`--survey`)

CSV con columnas obligatorias:

```csv
participant_id,role,intuitive_score,comments
P001,student,4,Interfaz clara
```

## Criterios de aceptación implementados

- Calidad de datos: dimensiones y canales uniformes, distribución balanceada.
- Modelo:
  - Accuracy > 0.85
  - Sensitivity (macro) > 0.80
  - Specificity (macro) > 0.80
- Funcionales:
  - Carga de ECG y respuesta de clasificación correcta.
  - Predicción con `predicted_class` y `confidence`.
- Rendimiento:
  - Tiempo promedio de inferencia < 5.0 s
- Usabilidad:
  - >= 80% de respuestas con `intuitive_score >= 4`
