# ECG Insight Mentor — Backend

API RESTful para la plataforma de entrenamiento en lectura de electrocardiogramas con apoyo de inteligencia artificial.

## Descripción General

Construida con **FastAPI** y **SQLite** (SQLAlchemy), proporciona:

- Autenticación y gestión de usuarios (JWT + bcrypt)
- Clasificación de ECG con modelo Hybrid CNN+LSTM+Attention
- Anotación visual de regiones relevantes por ventana deslizante
- Módulo de práctica con preguntas clínicas y retroalimentación
- Test posterior a la práctica con ajuste de nivel de habilidad
- Seguimiento de progreso y logros (badges)
- Integración con OpenAI para explicaciones clínicas adaptadas al nivel del usuario
- Pipeline de preprocesamiento que replica exactamente el proceso de entrenamiento

## Estructura del Proyecto

```
backend/
├── app/
│   ├── main.py                      # Punto de entrada FastAPI
│   ├── core/
│   │   └── config.py                # Configuración y variables de entorno
│   ├── database/
│   │   ├── base.py                  # Base declarativa SQLAlchemy
│   │   └── session.py               # Gestión de sesiones
│   ├── models/
│   │   ├── user.py                  # Modelo de usuario
│   │   ├── ecg.py                   # ECG, preguntas de práctica, intentos
│   │   └── progress.py              # Progreso y logros
│   ├── schemas/
│   │   ├── user.py                  # Schemas Pydantic — usuario
│   │   ├── ecg.py                   # Schemas Pydantic — ECG y práctica
│   │   └── progress.py              # Schemas Pydantic — progreso
│   ├── routes/
│   │   ├── auth.py                  # POST /auth/register, /auth/login
│   │   ├── users.py                 # GET/PUT /users/me
│   │   ├── ecg.py                   # POST /ecg/classify, GET /ecg/history
│   │   ├── practice.py              # GET /practice/questions, POST /practice/answer
│   │   ├── progress.py              # GET /progress
│   │   ├── achievements.py          # GET /achievements
│   │   └── health.py                # GET /health
│   ├── services/
│   │   ├── user_service.py
│   │   ├── ecg_service.py
│   │   ├── progress_service.py
│   │   ├── achievement_service.py
│   │   └── llm_service.py           # Explicaciones vía OpenAI
│   ├── ml_pipeline/
│   │   ├── model_manager.py         # Carga del modelo H5 y predicción
│   │   ├── image_preprocessor.py    # Preprocesamiento (Blur+Normalize+Otsu)
│   │   ├── image_annotator.py       # Anotación de imagen con ventanas
│   │   └── grad_cam.py              # Interpretabilidad (no activo en clasificación)
│   ├── middleware/
│   │   ├── cors.py
│   │   └── logging.py
│   ├── security/
│   │   └── auth.py                  # JWT y hashing de contraseñas
│   └── utils/
│       ├── file_handler.py
│       └── logger.py
│
├── models/                          # Modelos ML — versionados con Git LFS
│   └── best_model_Hybrid_CNN_LSTM_Attention.h5
│
├── db/                              # Base de datos SQLite (montada como volumen)
│   └── ecg_app.db                   # Generada en runtime (ignorada en git)
│
├── uploads/                         # Imágenes subidas por usuarios (ignorado en git)
│   └── practice_ecgs/               # ECGs para las preguntas de práctica
│
├── scripts/                         # Scripts de utilidad y carga de datos
│   ├── retrain_ecg.ipynb            # Notebook de reentrenamiento del modelo
│   ├── corpus.json                  # Corpus de preguntas clínicas
│   ├── model_classes_output.txt     # Referencia de clases del modelo
│   └── _archive/                    # Notebooks experimentales (no producción)
│
├── tests/                           # Suite de tests
├── seed.js                          # Seed inicial de base de datos (Bun)
├── requirements.txt
├── Dockerfile
└── run.py
```

## Despliegue con Docker (recomendado)

El despliegue completo se gestiona desde la **raíz del repositorio** con `docker-compose.yml`.

```bash
# Desde la raíz de TrainECG_app/
docker compose up --build
```

Esto ejecuta en orden:
1. **backend** — construye la imagen Python, inicia uvicorn, crea tablas SQLAlchemy
2. **frontend** — construye Vite + nginx, sirve en puerto 9000
3. **seed** — espera a que el backend esté healthy, luego inyecta las 20 preguntas de práctica y el usuario demo

La base de datos se persiste en `./backend/db/ecg_app.db` (bind mount).

### Variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=una-clave-larga-y-secreta
OPENAI_API_KEY=sk-...
VITE_API_URL=http://localhost:8000   # Para servidor remoto: http://IP:8000
```

## Instalación local (desarrollo sin Docker)

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Variables de entorno
cp .env.example .env  # Editar con tus valores

# Ejecutar
python run.py
```

API disponible en `http://localhost:8000`

## Documentación de la API

Con la aplicación corriendo:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/auth/register` | Registrar usuario |
| POST | `/auth/login` | Iniciar sesión |

### Usuarios
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/users/me` | Perfil del usuario actual |
| PUT | `/users/me` | Actualizar perfil |

### Clasificación de ECG
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/ecg/classify` | Clasificar imagen ECG |
| GET | `/ecg/history` | Historial de clasificaciones |

### Práctica
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/practice/questions` | Listar preguntas |
| POST | `/practice/answer` | Enviar respuesta |
| GET | `/practice/stats` | Estadísticas de práctica |
| POST | `/practice/post-test` | Test posterior a práctica |

### Progreso y Logros
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/progress` | Progreso del usuario |
| GET | `/achievements` | Logros desbloqueados |

### Sistema
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado de la aplicación |

## Modelo de Clasificación

El modelo **Hybrid CNN+LSTM+Attention** (`best_model_Hybrid_CNN_LSTM_Attention.h5`) clasifica latidos ECG en 6 clases MIT-BIH:

| Índice | Clase | Descripción |
|--------|-------|-------------|
| 0 | `fusion` | Latido de fusión (F) |
| 1 | `paced` | Latido con marcapasos (M) |
| 2 | `normal` | Latido normal (N) |
| 3 | `unknown` | No clasificable (Q) |
| 4 | `supraventricular_ectopic` | Extrasístole supraventricular (S) |
| 5 | `ventricular_ectopic` | Extrasístole ventricular (V) |

**Preprocesamiento** (idéntico al entrenamiento):
1. Escala de grises → resize 128×128 (`INTER_AREA`)
2. GaussianBlur(3,3) → normalización 0-255 → umbralización Otsu
3. Escalado a [0, 1]

## Variables de Entorno (referencia)

| Variable | Default | Descripción |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./db/ecg_app.db` | URL de conexión a la BD |
| `SECRET_KEY` | *(sin default seguro)* | Clave para firmar JWT |
| `OPENAI_API_KEY` | — | API key de OpenAI para explicaciones |
| `MODEL_PATH` | `./models/best_model_Hybrid_CNN_LSTM_Attention.h5` | Ruta al modelo H5 |
| `IMAGE_SIZE` | `128` | Tamaño de entrada del modelo |
| `ENVIRONMENT` | `production` | `production` o `development` |
| `LOG_LEVEL` | `INFO` | Nivel de logging |

## Modelos ML y Git LFS

Los archivos `.h5` están versionados con **Git LFS**. En un clone fresco:

```bash
git lfs pull   # descarga los modelos reales (~27 MB)
```

Si Git LFS no está instalado: https://git-lfs.com

## Tests

```bash
pytest
pytest --cov=app        # Con cobertura
pytest tests/ -v        # Verbose
```

## Seguridad

- JWT con expiración configurable
- Contraseñas hasheadas con bcrypt
- CORS configurable vía `BACKEND_CORS_ORIGINS`
- Validación de archivos: extensión + tamaño máximo
- Sin `--reload` en producción

---

**Proyecto**: Tesis de trabajo de grado — ECG Insight Mentor  
**Última actualización**: Abril 2026
