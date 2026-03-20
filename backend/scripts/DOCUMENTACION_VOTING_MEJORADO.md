# Documentación Completa: Voting_final_MEJORADO.ipynb

## Pipeline CRISP-ML(Q) para Clasificación de ECG - TrainECG

---

## 1. Objetivo General del Script

Este notebook implementa un **pipeline completo de entrenamiento, evaluación y selección de modelos de deep learning** para clasificar imágenes ECG en escala de grises en **6 clases** de tipos de latidos según la base de datos MIT-BIH. El script sigue la metodología **CRISP-ML(Q)** (Cross-Industry Standard Process for the development of Machine Learning applications with Quality assurance) y genera todas las métricas, gráficas, tablas comparativas y justificaciones necesarias para documentar la selección del modelo en la tesis.

### Clases del modelo (MIT-BIH beat types)

| Clase | Código | Descripción |
|-------|--------|-------------|
| Normal | N | Latido sinusal normal |
| Supraventricular Ectopic | S | Latido ectópico supraventricular |
| Ventricular Ectopic | V | Latido ectópico ventricular |
| Fusion | F | Latido de fusión |
| Unknown | Q | Latido no clasificable |
| Paced | P | Latido por marcapasos |

---

## 2. Configuración Global

```python
SEED = 42                # Semilla para reproducibilidad total
IMG_SIZE = (128, 128)    # Tamaño de las imágenes de entrada
BATCH_SIZE = 32          # Tamaño de lote para entrenamiento
EPOCHS = 30              # Épocas máximas (controlado por early stopping)
N_SPLITS = 3             # Número de folds en validación cruzada estratificada
USE_PERCENTAGE = 0.20    # Usa el 20% del dataset para acelerar entrenamiento
VAL_SPLIT = 0.15         # 15% del train se separa como validación interna
```

### Dataset

- **Ruta**: `backend/scripts/2D ECG grayscale Images/`
- **Estructura**: Dos carpetas principales `train/` y `test/`, cada una con subcarpetas por clase (N, S, V, F, Q, P)
- **Formato**: Imágenes PNG/JPG en escala de grises de trazos ECG 2D
- **Origen**: Dataset balanceado derivado de MIT-BIH Arrhythmia Database

### Reproducibilidad

Se fijan semillas en tres niveles:
```python
np.random.seed(42)
tf.random.set_seed(42)
random.seed(42)
```

---

## 3. Preprocesamiento de Imágenes

### Clase: `BalancedECGDataLoader`

Cada imagen ECG pasa por el siguiente pipeline de preprocesamiento (idéntico al del script original `Voting_final`):

| Paso | Operación | Función OpenCV | Propósito |
|------|-----------|----------------|-----------|
| 1 | Carga de imagen | `cv2.imread()` | Lee la imagen en formato BGR |
| 2 | Conversión a grises | `cv2.cvtColor(img, BGR2GRAY)` | Convierte a un solo canal |
| 3 | Redimensionamiento | `cv2.resize(img, (128,128), INTER_AREA)` | Tamaño uniforme para la red |
| 4 | Suavizado gaussiano | `cv2.GaussianBlur(img, (3,3), 0)` | Reduce ruido de alta frecuencia |
| 5 | Normalización de rango | `cv2.normalize(img, None, 0, 255, NORM_MINMAX)` | Estandariza contraste a [0, 255] |
| 6 | Umbral de Otsu | `cv2.threshold(img, 0, 255, THRESH_OTSU)` | Binariza: separa trazo ECG del fondo |
| 7 | Normalización a [0,1] | `thr.astype(float32) / 255.0` | Escala para la red neuronal |
| 8 | Expansión de canal | `np.expand_dims(img, axis=-1)` | Forma final: (128, 128, 1) |

### Carga del dataset

- `load_dataset('train')`: Itera las subcarpetas de clase dentro de `train/`, filtra directorios (ignora `.DS_Store`), y aplica muestreo aleatorio del 20%
- `load_dataset('test')`: Mismo proceso para `test/`
- Retorna: `X` (array de imágenes), `y_labels` (etiquetas numéricas), `class_names` (lista de nombres), `distribution` (diccionario con conteos por clase)
- Imágenes corruptas se cuentan pero se descartan silenciosamente

---

## 4. Función de Pérdida: Focal Loss

```python
def focal_loss(gamma=2., alpha=None):
```

### Qué es

La **Focal Loss** es una modificación de la cross-entropy estándar que **reduce el peso de los ejemplos fáciles** (alta confianza) y **aumenta el peso de los difíciles** (baja confianza). Fue propuesta por Lin et al. (2017) para detección de objetos con desbalance extremo.

### Fórmula

```
FL(p_t) = -α_t * (1 - p_t)^γ * log(p_t)
```

Donde:
- `p_t`: probabilidad predicha para la clase correcta
- `γ (gamma=2)`: factor de enfoque. A mayor gamma, más se penalizan los ejemplos difíciles
- `α (alpha)`: peso por clase para compensar desbalance

### Configuración en el script

- `gamma = 2.0` (valor estándar)
- `alpha`: vector donde la clase N recibe peso 2.0 y las demás 1.0
- Se usa como función de pérdida en `model.compile(loss=focal_loss(...))`

---

## 5. Métrica Custom: F1Score

```python
class F1Score(tf.keras.metrics.Metric):
```

Métrica de Keras que calcula el F1-Score durante el entrenamiento como:

```
F1 = 2 * (Precision * Recall) / (Precision + Recall + ε)
```

Se usa internamente por los callbacks (especialmente `ModelCheckpoint` que monitorea `val_f1_score`) para guardar el mejor modelo.

---

## 6. Data Augmentation Dirigida

### Función: `augment_class_examples`

Genera muestras sintéticas **exclusivamente para la clase N** (Normal) usando `ImageDataGenerator` de Keras:

| Transformación | Valor | Propósito |
|----------------|-------|-----------|
| `rotation_range` | ±8° | Simula variaciones de orientación |
| `width_shift_range` | 5% | Desplazamiento horizontal leve |
| `height_shift_range` | 5% | Desplazamiento vertical leve |
| `zoom_range` | 8% | Variación de escala |
| `shear_range` | 4% | Deformación de cizallamiento |
| `brightness_range` | (0.9, 1.1) | Variación de brillo ±10% |
| `fill_mode` | 'nearest' | Relleno de píxeles nuevos |

**Factor de augmentación**: 2 (cada imagen de clase N genera 2 imágenes extra).

**Razón**: La clase N (latido normal) es la más importante clínicamente y frecuentemente se confunde con otras clases en el modelo.

---

## 7. Funciones Auxiliares de Evaluación

### 7.1. Threshold Optimization

```python
def compute_optimal_threshold(y_true, y_pred_proba, class_names, target_metric='f1'):
```

- Barre thresholds de 0.10 a 0.95 (paso 0.05)
- Para cada threshold, calcula el F1-Macro global
- Reporta el threshold que maximiza el F1
- **Uso para la tesis**: Permite reportar el punto óptimo de operación del modelo

### 7.2. Hard Sample Mining

```python
def find_hard_samples(X, y_true, y_pred_proba, class_names, top_n=10):
```

- Ordena las muestras por **confianza de predicción ascendente** (menor confianza primero)
- Retorna las top-N muestras con: índice, clase real, clase predicha, confianza, si fue error
- **Uso para la tesis**: Análisis cualitativo de los errores del modelo

### 7.3. Curvas ROC

```python
def plot_roc_curves(y_true, y_pred_proba, class_names, title):
```

- Calcula curvas ROC **One-vs-Rest** para cada clase
- Muestra FPR vs TPR con el área bajo la curva (AUC) por clase
- Incluye línea diagonal (clasificador aleatorio) como referencia
- **Uso para la tesis**: Demuestra la capacidad discriminativa por tipo de arritmia

---

## 8. Arquitecturas de Modelos Evaluados

Se evalúan **5 arquitecturas** de complejidad creciente:

### 8.1. Simple_CNN (Línea Base)

```
Input(128,128,1)
→ Conv2D(16,3) + BN + MaxPool(2)
→ Conv2D(32,3) + BN + MaxPool(2)
→ Conv2D(64,3) + BN
→ GlobalAveragePooling2D
→ Dropout(0.3) → Dense(128) → Dropout(0.2)
→ Dense(6, softmax)
```

**Propósito**: Línea base de baja complejidad. Confirma si arquitecturas más complejas son necesarias.

### 8.2. CNN_Mejorada_Usuario (CNN Profunda)

```
Input(128,128,1)
→ Conv2D(32,3) + MaxPool(2)
→ Conv2D(32,3) + MaxPool(2)
→ Conv2D(64,3) + MaxPool(2)
→ Conv2D(64,3) + MaxPool(2)
→ Conv2D(128,3)
→ Conv2D(128,3)
→ GlobalAveragePooling2D
→ Dense(256) → Dropout(0.5)
→ Dense(6, softmax)
```

**Propósito**: Mayor profundidad y capacidad de representación espacial. 6 capas convolucionales.

### 8.3. LSTM_Attention (Secuencial con Atención)

```
Input(128,128,1)
→ Reshape(128, 128)           # Trata filas como pasos temporales
→ LSTM(128, return_sequences) + Dropout(0.25)
→ Attention manual (Dense→softmax→multiply)
→ LSTM(64) + Dropout(0.25)
→ Dense(128) → Dropout(0.3)
→ Dense(6, softmax)
```

**Propósito**: Captura dependencias secuenciales en el ECG. La atención pondera qué filas de la imagen son más relevantes.

### 8.4. Hybrid_CNN_LSTM_Attention (Modelo Principal)

```
Input(128,128,1)
→ Conv2D(32,3) + BN + MaxPool(2) + SpatialAttention + Dropout(0.2)
→ Conv2D(64,3) + BN + MaxPool(2) + SpatialAttention + Dropout(0.25)
→ Conv2D(128,3) + BN + MaxPool(2) + Dropout(0.2)
→ Reshape(H, W*C)             # Aplanar espacialmente para secuencia
→ Bidirectional LSTM(96, return_sequences) + Dropout(0.2)
→ AttentionLayer (Self-Attention Q,K,V + residual)
→ GlobalAveragePooling1D
→ Dense(256) → Dropout(0.3)
→ Dense(128) → Dropout(0.25)
→ Dense(64) → Dropout(0.2)
→ Dense(6, softmax)
```

**Propósito**: Combina extracción espacial (CNN con atención espacial), modelado secuencial (BiLSTM) y mecanismo de self-attention. Es la arquitectura más expresiva y la que se despliega en producción.

#### Capas Custom:

**SpatialAttentionLayer**:
- Conv2D(64, 3x3, relu) → Conv2D(1, 1x1, sigmoid)
- Genera un mapa de atención espacial que pondera regiones de la imagen
- Multiplica element-wise con la entrada: `x * attention_map`

**AttentionLayer** (Self-Attention):
- Matrices aprendibles W_q, W_k, W_v
- Q = input @ W_q, K = input @ W_k, V = input @ W_v
- Attention = softmax(Q @ K^T / √d) @ V
- Conexión residual: output = Dense(attended) + input

### 8.5. ResNet50_Spatial (Transfer Learning)

```
Input(128,128,1)
→ Conv2D(3, 1x1)              # Convierte 1 canal a 3 canales (para ResNet)
→ ResNet50(ImageNet, fine-tune desde capa 140)
→ SpatialAttentionLayer
→ GlobalAveragePooling2D
→ Dense(256) → Dropout(0.4)
→ Dense(128) → Dropout(0.3)
→ Dense(6, softmax)
```

**Propósito**: Aprovecha features pre-entrenados de ImageNet. Fine-tuning parcial (solo capas ≥140 son entrenables). Mayor costo computacional pero aprovecha representaciones visuales aprendidas.

---

## 9. Pipeline de Entrenamiento (Dos Fases por Modelo)

### 9.1. FASE A: K-Fold Cross-Validation

**Función**: `train_and_evaluate_kfold`

Se ejecutan **3 folds** de `StratifiedKFold` (mantiene proporciones de clase):

```
Para cada fold (1..3):
  1. Split: train_fold (67%) / test_fold (33%)
  2. Subdivisión: train_cv (85% de train_fold) / val_cv (15% de train_fold)
  3. Data augmentation dirigida para clase N (x2)
  4. Cálculo de class weights balanceados + boost x2 para N
  5. Compilación del modelo:
     - Optimizador: Adam(lr=3e-4)
     - Loss: Focal Loss(gamma=2, alpha con boost para N)
     - Métricas: accuracy, precision, recall, F1Score
  6. Callbacks:
     - EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
     - ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7)
  7. Entrenamiento: model.fit() con class_weight
  8. Evaluación en test_fold:
     - accuracy, F1-macro, F1-weighted
     - Threshold óptimo
     - Hard samples (5 muestras más difíciles)
  9. Almacena resultados del fold
```

**Resultado del K-Fold**: DataFrame con métricas por fold + promedios y desviaciones estándar:
```
Accuracy: 0.XXXX ± 0.XXXX
F1-Macro: 0.XXXX ± 0.XXXX
Tiempo promedio: XX.Xs
```

**Para la tesis**: La desviación estándar baja indica que el modelo es **robusto** y no depende de un split particular de datos.

### 9.2. FASE B: Entrenamiento Final con Diagnóstico Completo

**Función**: `train_final_model_with_diagnostics`

Se entrena **un modelo definitivo** usando todo el conjunto de train:

```
1. Split: train_fit (85%) / val_fit (15%) - estratificado
2. Data augmentation para clase N (x2)
3. Class weights balanceados + boost x2 para N
4. Compilación (misma configuración que K-Fold)
5. Callbacks adicionales:
   - ModelCheckpoint(monitor='val_f1_score', mode='max', save_best_only=True)
     → Guarda el mejor modelo a .h5
   - EarlyStopping y ReduceLROnPlateau (mismos que K-Fold)
6. Entrenamiento completo
7. Selección de mejor época: argmin(val_loss)
8. Generación de diagnósticos:
   a. Gráficas de historia (loss y accuracy por época)
   b. Evaluación en TRAIN (classification report + ROC + confusion matrix)
   c. Evaluación en TEST (classification report + ROC + confusion matrix)
   d. 10 predicciones visuales de ejemplo
```

---

## 10. Cómo se Guardan los Modelos

### 10.1. Durante el Entrenamiento (ModelCheckpoint)

```python
ModelCheckpoint(
    filepath='models/best_model_{model_name}.h5',
    monitor='val_f1_score',
    mode='max',
    save_best_only=True,
    save_weights_only=False  # Guarda modelo COMPLETO
)
```

- Se guarda automáticamente cada vez que `val_f1_score` mejora
- Formato: `.h5` (HDF5 de Keras)
- Contenido: arquitectura completa + pesos + estado del optimizador
- Se sobrescribe la versión anterior del mismo modelo

### 10.2. Después del Pipeline (save_top_models)

```python
def save_top_models(all_trained_models, top_n=3, output_dir='models/'):
```

1. Ordena todos los modelos finales por `f1_macro` en test (descendente)
2. Para cada modelo: `model.save(filepath, overwrite=True)`
3. Imprime tabla con: rank, nombre, fold, F1-macro, accuracy, mejor época, val_accuracy, val_loss, ruta

### 10.3. Archivos Generados

```
models/
├── best_model_Simple_CNN.h5
├── best_model_CNN_Mejorada_Usuario.h5
├── best_model_LSTM_Attention.h5
├── best_model_Hybrid_CNN_LSTM_Attention.h5
└── best_model_ResNet50_Spatial.h5
```

### 10.4. Cómo se Cargan los Modelos (en la aplicación)

En el backend de TrainECG (`backend/app/ml_pipeline/model_manager.py`), el modelo se carga con:

```python
from tensorflow.keras.models import load_model

model = load_model(
    'models/best_model_Hybrid_CNN_LSTM_Attention.h5',
    custom_objects={
        'AttentionLayer': AttentionLayer,
        'SpatialAttentionLayer': SpatialAttentionLayer,
        'focal': focal_loss(gamma=2.0)
    }
)
```

Se requiere pasar `custom_objects` porque el modelo usa capas y funciones de pérdida personalizadas que Keras no reconoce por defecto.

---

## 11. Gráficas y Visualizaciones Generadas

### 11.1. Por cada modelo (entrenamiento final)

| Gráfica | Función | Descripción |
|---------|---------|-------------|
| **Curvas de Loss** | `plot_training_history` | Loss de train vs validación por época. Permite detectar overfitting (divergencia entre curvas) |
| **Curvas de Accuracy** | `plot_training_history` | Accuracy de train vs validación por época. Muestra convergencia del modelo |
| **Curvas ROC-AUC (TRAIN)** | `plot_roc_curves` | ROC One-vs-Rest para cada clase en datos de entrenamiento. Muestra capacidad discriminativa |
| **Curvas ROC-AUC (TEST)** | `plot_roc_curves` | ROC One-vs-Rest para cada clase en datos de test. Evaluación real del modelo |
| **Matriz de Confusión (TRAIN)** | `plot_confusion_matrix_normalized` | Heatmap normalizado. Muestra patrones de confusión entre clases en train |
| **Matriz de Confusión (TEST)** | `plot_confusion_matrix_normalized` | Heatmap normalizado. Muestra dónde falla el modelo en datos no vistos |
| **10 Predicciones Visuales** | `show_test_predictions` | Grid 2x5 de imágenes ECG con clase real, predicha y confianza. Verde=correcto, rojo=error |

### 11.2. Comparación global (al final del pipeline)

| Gráfica | Función | Descripción |
|---------|---------|-------------|
| **Barplot F1-Macro en Test** | `plot_comparison_horizontal` | Compara F1-Macro entre los 5 modelos |
| **Barplot Accuracy en Test** | `plot_comparison_horizontal` | Compara Accuracy entre los 5 modelos |
| **Barplot CV F1-Macro Promedio** | `plot_comparison_horizontal` | Compara robustez (media de K-Fold) |
| **Barplot Tiempo de Entrenamiento** | `plot_comparison_horizontal` | Compara costo computacional en minutos |

---

## 12. Informe Final del Pipeline (Voting)

### 12.1. Tabla Comparativa

La función `build_comparison_table` genera un DataFrame con estas columnas:

| Columna | Significado |
|---------|-------------|
| `Modelo` | Nombre de la arquitectura |
| `Train_Accuracy` | Accuracy en datos de entrenamiento |
| `Train_F1_Macro` | F1-Macro en datos de entrenamiento |
| `Test_Accuracy` | Accuracy en datos de test (holdout) |
| `Test_F1_Macro` | F1-Macro en datos de test (métrica principal) |
| `Test_F1_Weighted` | F1-Weighted en datos de test (ponderado por soporte) |
| `CV_F1_Macro_Mean` | Promedio de F1-Macro en K-Fold (robustez) |
| `CV_F1_Macro_Std` | Desviación estándar de F1-Macro en K-Fold (estabilidad) |
| `Tiempo_min` | Tiempo de entrenamiento final en minutos |
| `Epochs` | Número de épocas entrenadas (antes de early stopping) |
| `Params` | Número total de parámetros del modelo |

La tabla se ordena por: `Test_F1_Macro` > `Test_Accuracy` > `CV_F1_Macro_Mean` (descendente).

### 12.2. Selección y Justificación del Mejor Modelo

La función `print_model_selection_justification` genera:

1. **Tabla completa** de comparación
2. **Nombre del modelo ganador** (primera fila de la tabla ordenada)
3. **Métricas clave**: Test F1-Macro, Test Accuracy, CV F1-Macro promedio, tiempo, parámetros
4. **Justificación para la tesis** (texto pre-escrito por arquitectura):

> *"Se selecciona {modelo} porque obtuvo el mejor balance entre desempeño en test, estabilidad en validación cruzada y costo computacional. En el contexto de TrainECG, esto es valioso porque el sistema debe clasificar trazos ECG de forma confiable y consistente, incluso cuando existen variaciones morfológicas entre clases."*

### 12.3. Classification Report (por modelo, por split)

Para cada modelo, en TRAIN y TEST, se imprime el reporte de scikit-learn:

```
                    precision    recall  f1-score   support

              F       0.XXXX    0.XXXX    0.XXXX      XXX
              N       0.XXXX    0.XXXX    0.XXXX      XXX
              Q       0.XXXX    0.XXXX    0.XXXX      XXX
              S       0.XXXX    0.XXXX    0.XXXX      XXX
              V       0.XXXX    0.XXXX    0.XXXX      XXX
              P       0.XXXX    0.XXXX    0.XXXX      XXX

       accuracy                           0.XXXX     XXXX
      macro avg       0.XXXX    0.XXXX    0.XXXX     XXXX
   weighted avg       0.XXXX    0.XXXX    0.XXXX     XXXX
```

---

## 13. Flujo Completo del Pipeline (`run_crisp_ml_improved`)

```
┌─────────────────────────────────────────────────────────────────┐
│ FASE 1: COMPRENSIÓN DE NEGOCIO Y CARGA DE DATOS                │
│  ├─ Instanciar BalancedECGDataLoader(20%)                       │
│  ├─ Cargar train → X_train, y_train_labels, class_names        │
│  ├─ Cargar test  → X_test, y_test_labels                       │
│  ├─ Imprimir distribución por clase                             │
│  └─ to_categorical (one-hot encoding)                           │
├─────────────────────────────────────────────────────────────────┤
│ FASE 2: MODELADO Y EVALUACIÓN (por cada modelo x5)             │
│  ├─ [1/3] K-Fold Cross-Validation (3 folds)                    │
│  │   ├─ Entrenar 3 modelos independientes                       │
│  │   ├─ Evaluar en fold de test                                 │
│  │   ├─ Threshold optimization + hard sample mining             │
│  │   └─ Reportar media ± std de métricas                        │
│  ├─ [2/3] Entrenamiento final con diagnósticos                  │
│  │   ├─ Entrenar modelo definitivo (train completo)             │
│  │   ├─ ModelCheckpoint guarda mejor .h5                        │
│  │   ├─ Gráficas: loss, accuracy, ROC, confusion matrix        │
│  │   ├─ Classification report (TRAIN y TEST)                    │
│  │   └─ 10 predicciones visuales de ejemplo                     │
│  └─ Almacenar modelo para guardado posterior                    │
├─────────────────────────────────────────────────────────────────┤
│ FASE 3: ANÁLISIS COMPARATIVO GLOBAL                             │
│  ├─ Tabla comparativa (11 columnas)                             │
│  ├─ 4 barplots horizontales de comparación                      │
│  └─ Selección + justificación del mejor modelo                  │
├─────────────────────────────────────────────────────────────────┤
│ FASE 4: GUARDADO DE MODELOS                                     │
│  ├─ Ordenar por F1-Macro en test                                │
│  ├─ model.save() para cada modelo → .h5                         │
│  └─ Tabla de modelos guardados con métricas y rutas             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 14. Estrategias para Manejo del Desbalance de Clases

El script aplica **4 estrategias complementarias**:

| Estrategia | Cómo funciona | Dónde se aplica |
|------------|---------------|-----------------|
| **Focal Loss** | Penaliza más los ejemplos difíciles (baja confianza) | Función de pérdida (compilación) |
| **Alpha weights en Focal Loss** | Peso 2.0 para clase N, 1.0 para las demás | Función de pérdida (compilación) |
| **Class weights balanceados** | `compute_class_weight('balanced')` + boost x2 para N | `model.fit(class_weight=...)` |
| **Data augmentation dirigida** | Genera x2 muestras sintéticas solo para clase N | Antes del entrenamiento |

**Nota**: La función `apply_smote_to_fold` existe pero **no aplica SMOTE** porque el dataset ya está balanceado. Simplemente retorna los datos originales.

---

## 15. Callbacks y Regularización

### Callbacks durante el entrenamiento

| Callback | Monitor | Configuración | Propósito |
|----------|---------|---------------|-----------|
| `EarlyStopping` | `val_loss` (min) | patience=10, restore_best_weights=True | Detiene el entrenamiento cuando val_loss deja de mejorar. Restaura los pesos de la mejor época |
| `ReduceLROnPlateau` | `val_loss` (min) | factor=0.5, patience=5, min_lr=1e-7 | Reduce learning rate a la mitad cuando val_loss se estanca |
| `ModelCheckpoint` | `val_f1_score` (max) | save_best_only=True, save_weights_only=False | Guarda el modelo completo cuando F1 en validación mejora (solo en entrenamiento final) |

### Regularización en las arquitecturas

| Técnica | Dónde se usa | Valores |
|---------|-------------|---------|
| **Dropout** | Todas las arquitecturas | 0.2 a 0.5 según la capa |
| **BatchNormalization** | Simple_CNN, Hybrid_CNN_LSTM_Attention | Después de cada Conv2D |
| **Recurrent Dropout** | LSTM_Attention, Hybrid | 0.15 en capas LSTM |
| **GlobalAveragePooling** | Todas (excepto LSTM pura) | Reduce parámetros vs Flatten |

---

## 16. Para la Metodología CRISP-ML(Q) de la Tesis

### 16.1. Comprensión del Negocio (Business Understanding)

- **Problema**: Clasificación automática de tipos de latidos en imágenes ECG para una plataforma educativa
- **Usuarios finales**: Estudiantes de medicina, residentes, enfermeros
- **Requisito**: El modelo debe clasificar de forma confiable y consistente, con explicaciones adaptadas al nivel del usuario
- **Dataset**: "2D ECG grayscale Images" derivado de MIT-BIH Arrhythmia Database
- **Clases**: 6 tipos de latidos (N, S, V, F, Q, P)
- **Métrica principal**: F1-Macro (trata todas las clases por igual, importante en contexto clínico)

### 16.2. Comprensión de los Datos (Data Understanding)

- Imágenes 2D en escala de grises de trazos ECG
- Dataset pre-balanceado con subcarpetas por clase
- Se usa 20% del dataset por restricciones computacionales
- Muestreo estratificado para mantener proporciones de clase
- Archivos corruptos se detectan y descartan

### 16.3. Preparación de los Datos (Data Preparation)

- Preprocesamiento en 8 pasos: carga → grises → resize → GaussianBlur → normalización → Otsu → [0,1] → canal
- One-hot encoding de etiquetas (`to_categorical`)
- Data augmentation dirigida para clase N (rotación, desplazamiento, zoom, brillo)
- Splits: StratifiedKFold (3 folds) para CV + train/val (85/15) para entrenamiento final

### 16.4. Modelado (Modeling)

- 5 arquitecturas evaluadas de complejidad creciente
- Optimizador: Adam (lr=3e-4, con reducción adaptativa)
- Loss: Focal Loss (gamma=2) con pesos alpha por clase
- Regularización: Dropout, BatchNormalization, EarlyStopping
- Class weights balanceados con boost para clase N

### 16.5. Evaluación (Evaluation)

- **Validación cruzada estratificada** (3 folds): media ± std de F1-Macro y Accuracy
- **Evaluación en test holdout**: Accuracy, F1-Macro, F1-Weighted
- **Classification report** por clase: precision, recall, F1-score, support
- **Curvas ROC-AUC** One-vs-Rest por clase
- **Matrices de confusión normalizadas** (TRAIN y TEST)
- **Threshold optimization** para F1-Score
- **Hard sample mining**: análisis de muestras difíciles
- **Tabla comparativa global** de 5 modelos con 11 métricas
- **Selección justificada** del mejor modelo

### 16.6. Despliegue (Deployment)

- Modelo guardado en formato `.h5` (Keras HDF5)
- El modelo ganador (Hybrid_CNN_LSTM_Attention) se integra en backend FastAPI
- Se carga con `load_model()` + `custom_objects` para capas personalizadas
- Pipeline de inferencia en producción: carga imagen → preprocesamiento Otsu → ventanas deslizantes → predicción por ventana → voting → clase principal → explicación LLM

### 16.7. Monitoreo y Mantenimiento (Monitoring)

- Las métricas de K-Fold (std baja) demuestran estabilidad del modelo
- El ModelCheckpoint asegura que solo se guarda el mejor estado
- Los hard samples identifican áreas de mejora para futuras iteraciones
- La tabla comparativa permite re-evaluar la selección si se añaden nuevas arquitecturas

---

## 17. Resumen de Métricas Clave para Reportar

| Métrica | Qué mide | Dónde aparece |
|---------|----------|---------------|
| **Accuracy** | % de predicciones correctas | Classification report, tabla comparativa |
| **F1-Macro** | Media aritmética del F1 por clase (sin ponderar) | Tabla comparativa, K-Fold, selección |
| **F1-Weighted** | F1 ponderado por soporte de cada clase | Tabla comparativa |
| **Precision** | TP / (TP + FP) por clase | Classification report |
| **Recall (Sensitivity)** | TP / (TP + FN) por clase | Classification report |
| **AUC-ROC** | Área bajo la curva ROC (capacidad discriminativa) | Curvas ROC por clase |
| **CV F1-Macro Mean ± Std** | Robustez y estabilidad del modelo | Resumen K-Fold |
| **Optimal Threshold** | Umbral de confianza que maximiza F1 | Threshold optimization |
| **Training Time** | Costo computacional | Tabla comparativa |
| **Parameters** | Complejidad del modelo | Tabla comparativa |

---

## 18. Dependencias del Script

```python
# Core
numpy, pandas, matplotlib, seaborn

# Machine Learning
scikit-learn (model_selection, metrics, preprocessing, utils)
imbalanced-learn (SMOTE - declarado pero no usado activamente)

# Deep Learning
tensorflow / keras (models, layers, callbacks, preprocessing, applications)

# Computer Vision
opencv-python (cv2)
```

---

## 19. Notas Importantes

1. **El preprocesamiento Otsu es obligatorio**: Si se omite en producción, las predicciones serán incorrectas porque el modelo fue entrenado con imágenes binarizadas.

2. **SMOTE no se aplica**: La función `apply_smote_to_fold` existe pero retorna datos sin modificar porque el dataset ya está balanceado.

3. **El "voting" del nombre** se refiere a que se evalúan múltiples arquitecturas y se selecciona la mejor por votación de métricas (no es un ensemble voting en producción).

4. **ResNet50 usa batch_size=16** (en vez de 32) por su mayor consumo de memoria.

5. **Los modelos se guardan con `overwrite=True`**: Cada ejecución sobrescribe los .h5 anteriores.

6. **La clase N recibe tratamiento especial**: boost en class weights (x2), boost en alpha de focal loss (x2), y data augmentation dirigida (x2). Esto porque los latidos normales son clínicamente los más relevantes para descartar patología.
