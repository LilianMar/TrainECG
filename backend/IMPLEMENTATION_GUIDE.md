# 🚀 PRÓXIMOS PASOS - IMPLEMENTACIÓN ROUTES FALTANTES

## 📍 Ubicación del Trabajo

Tu carpeta de trabajo:
```
/Users/lilianestefaniamaradiagocorrea/Desktop/Tesis/BACK/ecg-backend/
```

## 📋 3 Routes por Implementar

### 1️⃣ CLASIFICACIÓN DE ECG (2 endpoints)

**Archivo**: `app/routes/ecg.py`  
**Template**: `app/routes/ecg.py.template`

```python
POST   /ecg/classify          - Clasificar imagen de ECG
GET    /ecg/history           - Ver historial de clasificaciones
```

**Paso a paso**:
1. Copiar contenido de `ecg.py.template` a `ecg.py`
2. Descomentar el código
3. Ajustar imports según tu estructura
4. En `app/main.py`, agregar:
   ```python
   from app.routes import ecg
   app.include_router(ecg.router)
   ```

**Depende de**:
- ✅ `ModelManager` (ya existe)
- ✅ `ImagePreprocessor` (ya existe)
- ✅ `GradCAM` (ya existe)
- [ ] Implementar LLM call

---

### 2️⃣ MODO PRÁCTICA (3 endpoints)

**Archivo**: `app/routes/practice.py`  
**Template**: `app/routes/practice.py.template`

```python
GET    /practice/questions    - Obtener preguntas
GET    /practice/questions/{id} - Obtener pregunta específica
POST   /practice/answer       - Responder pregunta
GET    /practice/stats        - Ver estadísticas
```

**Paso a paso**:
1. Copiar contenido de `practice.py.template` a `practice.py`
2. Descomentar el código
3. Ajustar imports
4. En `app/main.py`, agregar:
   ```python
   from app.routes import practice
   app.include_router(practice.router)
   ```

**Depende de**:
- ✅ `ECGService` (ya existe)
- ✅ `ProgressService` (ya existe)

---

### 3️⃣ PROGRESO Y RECOMENDACIONES (3 endpoints)

**Archivo**: `app/routes/progress.py`  
**Template**: `app/routes/progress.py.template`

```python
GET    /progress              - Ver progreso general
GET    /progress/detailed     - Progreso detallado
GET    /progress/recommendations - Recomendaciones personalizadas
GET    /progress/stats/by-arrhythmia - Stats por tipo
```

**Paso a paso**:
1. Copiar contenido de `progress.py.template` a `progress.py`
2. Descomentar el código
3. Ajustar imports
4. En `app/main.py`, agregar:
   ```python
   from app.routes import progress
   app.include_router(progress.router)
   ```

**Depende de**:
- ✅ `ProgressService` (ya existe)

---

## 🔗 Cómo Incluir Routes en main.py

**Archivo**: `app/main.py`  
**Línea actual**: ~65

Busca la sección de routers:
```python
# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
# Agregar aquí:
app.include_router(ecg.router)
app.include_router(practice.router)
app.include_router(progress.router)
```

---

## 🔧 Integración con LLM

En `ecg.py`, necesitarás implementar:

```python
async def get_llm_explanation(arrhythmia_class: str) -> str:
    """
    Obtener explicación del LLM sobre la arritmia detectada.
    
    Opciones:
    - OpenAI (gpt-3.5-turbo, gpt-4)
    - Anthropic (Claude)
    - Local (Ollama, LLaMA)
    """
    # Implementar llamada a LLM API
    pass
```

**Ejemplo con OpenAI**:
```python
from openai import OpenAI

client = OpenAI(api_key=settings.LLM_API_KEY)

async def get_llm_explanation(arrhythmia_class: str) -> str:
    prompt = f"""
    Explicar brevemente (2-3 oraciones) qué es {arrhythmia_class} 
    en un electrocardiograma, sus características principales y 
    por qué el modelo la detectó.
    """
    
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=200
    )
    
    return response.choices[0].message.content
```

---

## 📂 Estructura Después de Implementar

```
app/routes/
├── __init__.py
├── health.py           ✅ (listo)
├── auth.py             ✅ (listo)
├── users.py            ✅ (listo)
├── ecg.py              🚧 (por hacer)
├── practice.py         🚧 (por hacer)
├── progress.py         🚧 (por hacer)
├── ecg.py.template     📄 (referencia)
├── practice.py.template 📄 (referencia)
└── progress.py.template 📄 (referencia)
```

---

## ✅ Checklist de Implementación

### ECG Classification
- [ ] Crear `app/routes/ecg.py`
- [ ] Copiar contenido del template
- [ ] Implementar LLM integration
- [ ] Incluir router en `main.py`
- [ ] Probar en Swagger (/docs)
- [ ] Escribir tests

### Practice Mode
- [ ] Crear `app/routes/practice.py`
- [ ] Copiar contenido del template
- [ ] Incluir router en `main.py`
- [ ] Cargar preguntas de ejemplo en DB
- [ ] Probar en Swagger (/docs)
- [ ] Escribir tests

### Progress Tracking
- [ ] Crear `app/routes/progress.py`
- [ ] Copiar contenido del template
- [ ] Mejorar lógica de recomendaciones
- [ ] Incluir router en `main.py`
- [ ] Probar en Swagger (/docs)
- [ ] Escribir tests

---

## 🧪 Testing de Nuevos Endpoints

```python
# En tests/test_endpoints.py, agregar:

def test_classify_ecg(client):
    """Test ECG classification endpoint."""
    # Crear archivo de prueba
    with open("test_ecg.jpg", "rb") as f:
        response = client.post(
            "/ecg/classify",
            files={"file": f}
        )
    
    assert response.status_code == 200
    assert "predicted_class" in response.json()
    assert "confidence" in response.json()

def test_get_practice_questions(client):
    """Test get practice questions endpoint."""
    response = client.get("/practice/questions")
    
    assert response.status_code == 200
    assert "total" in response.json()
    assert "questions" in response.json()

def test_get_progress(client):
    """Test get progress endpoint."""
    response = client.get("/progress")
    
    assert response.status_code == 200
    assert "practice_accuracy" in response.json()
```

---

## 🐛 Debugging Tips

```bash
# Ver logs mientras desarrollo
tail -f logs/app.log

# Ejecutar con debugging
python -m pdb run.py

# Probar endpoints con curl
curl -X GET http://localhost:8000/progress \
  -H "Authorization: Bearer <token>"
```

---

## 📊 Cargar Datos de Ejemplo

Para que funcione la práctica, necesitas preguntas en la DB:

```python
# En tests o script separado:
from app.database import SessionLocal
from app.services.ecg_service import ECGService
from app.models.ecg import ArrhythmiaClassEnum

db = SessionLocal()

# Crear preguntas de ejemplo
ECGService.create_practice_question(
    db=db,
    image_filename="af_001.jpg",
    image_path="/uploads/af_001.jpg",
    question_text="¿Qué tipo de arritmia observas en este ECG?",
    correct_answer=0,  # Index 0 = opción A
    option_a="Fibrilación Auricular",
    option_b="Taquicardia Ventricular",
    option_c="Bloqueo AV",
    option_d="Ritmo Sinusal Normal",
    explanation="La fibrilación auricular se caracteriza por...",
    correct_class=ArrhythmiaClassEnum.ATRIAL_FIBRILLATION,
    difficulty_level=2
)

db.commit()
```

---

## 🚀 Timeline Sugerido

**Semana 1 (Feb 14-21)**
- [ ] Implementar rutas básicas de ECG
- [ ] Conectar modelo ML
- [ ] Cargar datos de prueba

**Semana 2 (Feb 21-28)**
- [ ] Integrar LLM
- [ ] Completar rutas de práctica
- [ ] Escribir tests

**Semana 3 (Feb 28 - Mar 7)**
- [ ] Completar rutas de progreso
- [ ] Optimizaciones
- [ ] Deployment test

**Semana 4 (Mar 7-14)**
- [ ] Deployment a producción
- [ ] Documentación final
- [ ] Presentación

---

## 📞 Recursos Útiles

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Pydantic**: https://docs.pydantic.dev/
- **OpenAI Python**: https://github.com/openai/openai-python
- **TensorFlow**: https://www.tensorflow.org/

---

## 💡 Pro Tips

1. **Usa Swagger para probar**: Abre http://localhost:8000/docs
2. **Activa logging**: Ver `app/utils/logger.py`
3. **Escribe tests mientras desarrollas**: TDD es tu amigo
4. **Versionea con Git**: Commit frecuente
5. **Documenta mientras avanzas**: Docstrings en funciones

---

**¡Adelante con la implementación! Tienes una base sólida para construir.** 🎯

