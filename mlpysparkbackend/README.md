# ML PySpark Backend

Backend Flask con PySpark y MLlib para análisis y predicción de datos.

## Arquitectura

```
mlpysparkbackend/
├── app/
│   ├── __init__.py          # Application Factory
│   ├── config.py            # Configuración
│   ├── extensions.py        # Extensiones de Flask
│   ├── api/                 # Capa de API
│   │   ├── routes/          # Blueprints de rutas
│   │   │   ├── health.py
│   │   │   ├── datasets.py
│   │   │   ├── exploration.py
│   │   │   ├── models.py
│   │   │   └── reports.py
│   │   └── schemas/         # Validación de datos
│   │       ├── dataset_schemas.py
│   │       ├── exploration_schemas.py
│   │       ├── model_schemas.py
│   │       └── report_schemas.py
│   ├── core/                # Núcleo de la aplicación
│   │   ├── spark_manager.py # Gestor de Spark Session
│   │   └── storage.py       # Almacenamiento en memoria
│   ├── services/            # Lógica de negocio
│   │   ├── dataset_service.py
│   │   ├── exploration_service.py
│   │   ├── training_service.py
│   │   └── report_service.py
│   └── utils/               # Utilidades
│       ├── decorators.py    # Decoradores
│       ├── exceptions.py    # Excepciones personalizadas
│       ├── validators.py    # Validadores
│       └── helpers.py       # Funciones auxiliares
├── storage/                 # Carpetas de almacenamiento
│   ├── uploads/
│   ├── models/
│   └── reports/
├── app.py                   # Entry point legacy (compatibilidad)
├── run.py                   # Entry point principal
├── requirements.txt         # Dependencias
└── .env.example             # Ejemplo de variables de entorno
```

## Características

### ✨ Patrones y Prácticas

- **Application Factory Pattern**: Inicialización modular de la aplicación
- **Separation of Concerns**: Separación clara entre API, lógica de negocio y datos
- **Repository Pattern**: Gestión centralizada de almacenamiento
- **Singleton Pattern**: Gestión de Spark Session
- **Dependency Injection**: Inyección de configuración
- **Error Handling**: Manejo centralizado de errores
- **Logging**: Sistema de logging comprehensivo
- **Type Hints**: Tipado estático para mejor mantenibilidad
- **Docstrings**: Documentación completa de código

### 🛡️ Validaciones

- Validación de archivos (tipo, tamaño)
- Validación de esquemas de datos
- Validación de parámetros
- Sanitización de entradas
- Manejo de errores descriptivos

### 📊 Funcionalidades ML

**Modelos soportados:**
- Clasificación: Logistic Regression, Decision Tree, Random Forest, GBT
- Regresión: Linear Regression, Decision Tree, Random Forest, GBT
- Clustering: K-Means, Bisecting K-Means

**Métricas:**
- Clasificación: Accuracy, Precision, Recall, F1, Confusion Matrix, ROC AUC
- Regresión: RMSE, MAE, R²
- Clustering: Silhouette Score, Cluster Distribution

## Instalación

```bash
# Clonar repositorio
cd mlpysparkbackend

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
```

## Configuración

### Variables de Entorno (.env)

```env
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=your-secret-key
DEBUG=True

CORS_ORIGINS=http://localhost:3000

UPLOAD_FOLDER=storage/uploads
MODELS_FOLDER=storage/models
REPORTS_FOLDER=storage/reports

MAX_CONTENT_LENGTH=104857600  # 100MB
MAX_PREVIEW_ROWS=1000
MAX_CHART_POINTS=10000

SPARK_APP_NAME=MLPySparkApp
SPARK_DRIVER_MEMORY=4g
SPARK_EXECUTOR_MEMORY=4g
```

## Uso

### Iniciar Servidor

```bash
# Desarrollo
python run.py

# Producción (con gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

### API Endpoints

#### Health
- `GET /api/health` - Estado del servidor
- `GET /api/health/spark` - Estado de Spark

#### Datasets
- `POST /api/datasets/upload` - Subir archivo CSV/Excel
- `POST /api/datasets/upload-json` - Subir datos JSON
- `GET /api/datasets` - Listar datasets
- `GET /api/datasets/<id>` - Info de dataset
- `GET /api/datasets/<id>/preview` - Vista previa
- `DELETE /api/datasets/<id>` - Eliminar dataset
- `GET /api/datasets/samples` - Datasets de ejemplo
- `POST /api/datasets/samples/<id>/load` - Cargar ejemplo

#### Exploración
- `GET /api/datasets/<id>/statistics` - Estadísticas descriptivas
- `GET /api/datasets/<id>/histogram` - Datos de histograma
- `GET /api/datasets/<id>/chart` - Datos para gráficos
- `GET /api/datasets/<id>/correlation` - Matriz de correlación
- `POST /api/datasets/<id>/filter` - Filtrar datos
- `GET /api/datasets/<id>/describe` - Describir columna
- `GET /api/datasets/<id>/missing` - Valores faltantes

#### Modelos
- `GET /api/models/types` - Tipos de modelos disponibles
- `POST /api/models/train` - Entrenar modelo
- `GET /api/models` - Listar modelos
- `GET /api/models/<id>` - Info de modelo
- `POST /api/models/<id>/predict` - Hacer predicciones
- `DELETE /api/models/<id>` - Eliminar modelo
- `GET /api/models/<id>/feature-importance` - Importancia de features
- `POST /api/models/<id>/evaluate` - Evaluar modelo

#### Reportes
- `POST /api/reports/generate` - Generar reporte (Excel/JSON)
- `GET /api/reports/export-dataset/<id>` - Exportar dataset
- `GET /api/reports/model/<id>/metrics` - Métricas de modelo
- `GET /api/reports/summary` - Resumen del sistema

## Testing

```bash
# Ejecutar tests (cuando estén implementados)
pytest

# Con cobertura
pytest --cov=app
```

## Estructura de Respuesta

### Éxito
```json
{
  "success": true,
  "data": { ... },
  ...
}
```

### Error
```json
{
  "error": "Mensaje de error",
  "field": "campo_con_error"  // opcional
}
```

## Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

MIT

## Contacto

Tu Nombre - [@tu_twitter](https://twitter.com/tu_twitter)

Project Link: [https://github.com/tu-usuario/mlpysparkbackend](https://github.com/tu-usuario/mlpysparkbackend)
