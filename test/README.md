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

# Modo piloto (tolerancias amplias para prototipo)
PYTHON_BIN=/ruta/al/venv/python ./test/run_plan_pruebas.sh \
  --base-url http://localhost:8000 \
  --image backend/train/ecg_case_1.png \
  --dataset test/data/dataset_from_questions \
  --survey test/usability/usability_survey_template.csv \
  --mode pilot

# Modo strict (criterios de producción)
PYTHON_BIN=/ruta/al/venv/python ./test/run_plan_pruebas.sh \
  --base-url http://localhost:8000 \
  --image backend/train/ecg_case_1.png \
  --dataset test/data/dataset_from_questions \
  --mode strict
```

## Modo piloto vs Strict

**Piloto** (desarrollo/prototipo):
- Accuracy >= 70%, Sensitivity >= 65%, Specificity >= 65%
- Rendimiento < 10s promedio
- Desbalance de clases <= 3.0
- Usabilidad >= 65% intuitiva

**Strict** (producción):
- Accuracy >= 85%, Sensitivity >= 80%, Specificity >= 80%
- Rendimiento < 5s promedio
- Desbalance de clases <= 1.5
- Usabilidad >= 80% intuitiva

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

### Modo piloto (default)
- **Calidad de datos**: dimensiones y canales uniformes (<=6 tamaños, <=3 canales), desbalance <=3.0
- **Modelo**: Accuracy>=70%, Sensitivity>=65% (etiquetas normalizadas con fallback ventricular_ectopic)
- **Funcionales**: Carga de ECG y predicción exitosa (status 200)
- **Rendimiento**: Tiempo promedio < 10s
- **Usabilidad**: >= 65% de respuestas con intuitive_score >= 4

### Modo strict (para producción)
- **Calidad de datos**: Dimensiones y canales idénticos, desbalance <=1.5
- **Modelo**: Accuracy>=85%, Sensitivity>=80%, Specificity>=80%
- **Funcionales**: Idem piloto
- **Rendimiento**: Tiempo promedio < 5s
- **Usabilidad**: >= 80% de respuestas con intuitive_score >= 4

## Etiquetas soportadas

El generador de predicciones normaliza automáticamente etiquetas clínicas a clases del modelo:

```
V -> ventricular_ectopic
S -> supraventricular_ectopic  
N -> normal
F -> fusion
Q -> unknown
P -> paced
```
