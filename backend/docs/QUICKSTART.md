# ECG Backend - Guía de Inicio Rápido

## Primeros Pasos (5 minutos)

### 1. Setup Inicial
```bash
# Clonar proyecto
cd ~/Desktop/Tesis/BACK/ecg-backend

# Crear virtual env
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con valores locales
# SECRET_KEY: genera uno seguro con: openssl rand -hex 32
# DATABASE_URL: mantener default para desarrollo
# MODELO_PATH: Ajustar según ubicación de archivos .h5
```

### 3. Iniciar Servidor
```bash
python run.py

# O con recarga automática
uvicorn app.main:app --reload

# La API estará en: http://localhost:8000
```

### 4. Verificar que Funcione
```bash
# En otra terminal
curl http://localhost:8000/health

# Resultado esperado
{
  "status": "healthy",
  "app": "ECG Insight Mentor API",
  "version": "1.0.0"
}
```

### 5. Ver Documentación
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Estructura Explicada Brevemente

| Carpeta | Función |
|---------|---------|
| `core/` | Configuración global |
| `database/` | SQLAlchemy y sesiones |
| `models/` | Definiciones de tablas |
| `schemas/` | Validación con Pydantic |
| `routes/` | Endpoints de la API |
| `services/` | Lógica de negocio |
| `security/` | Autenticación JWT |
| `ml_pipeline/` | Modelo + preprocesamiento |
| `utils/` | Funciones auxiliares |

## Próximos Pasos

1. **Conectar Frontend** → Actualizar CORS en `.env`
2. **Agregar Modelo ML** → Copiar `.h5` a carpeta `models/`
3. **Completar Rutas** → Implementar `routes/ecg.py`, `practice.py`, `progress.py`
4. **Testear Endpoints** → Usar Swagger o Postman
5. **Deployar** → Docker + servidor remoto (marzo)

## Troubleshooting

**Error: "No module named 'tensorflow'"**
```bash
pip install -r requirements.txt --upgrade
```

**Error: "Database is locked"**
```bash
# SQLite tiene límites. Para producción usar PostgreSQL
# En desarrollo: reiniciar servidor
```

**Puerto 8000 en uso**
```bash
# Cambiar en run.py o:
uvicorn app.main:app --port 8001
```

---

¿Preguntas? Revisar `README.md` completo.
