# 🎨 Frontend - ML PySpark Web App

Aplicación web moderna de análisis y predicción de datos con Machine Learning, construida con Next.js 16, TypeScript y shadcn/ui.

## 🚀 Características Implementadas

### ✨ Funcionalidades Principales

#### 📊 Dashboard
- **Resumen del Sistema**: Visualización de métricas clave
  - Total de datasets cargados
  - Modelos entrenados
  - Archivos en el sistema
  - Reportes generados
- **Datasets Recientes**: Lista de los últimos datasets cargados
- **Modelos Recientes**: Lista de los últimos modelos entrenados
- **Actualización en Tiempo Real**: Información actualizada del backend

#### 🎯 Página de Entrenamiento (4 Pestañas)

##### 1️⃣ Cargar Datos
- **Upload de Archivos**: Soporta CSV, Excel (.xlsx, .xls)
- **Datasets de Ejemplo**: Carga rápida de datasets (Iris, Wine, Diabetes)
- **Gestión de Datasets**: Lista completa con información detallada
  - Número de filas y columnas
  - ID único del dataset
  - Nombre del archivo
- **Eliminación de Datasets**: Borrado individual

##### 2️⃣ Explorar
- **Selector de Dataset**: Dropdown para seleccionar dataset activo
- **Vista Previa**: Tabla con las primeras 10 filas
- **Estadísticas Descriptivas**: Tabla completa con:
  - Media, Desviación Estándar
  - Mínimo, Máximo
  - Percentiles (25%, 50%, 75%)
- **Histogramas**: Visualización de distribución por columna
  - Selector de columna
  - Gráfico interactivo con Recharts
- **Análisis de Datos**: Información detallada de cada columna

##### 3️⃣ Entrenar
- **Configuración de Modelo**:
  - Selección de dataset
  - Nombre personalizado del modelo
  - Tipo de modelo (Clasificación, Regresión, Clustering)
  - Algoritmo específico
  - Columna objetivo (target)
  - Selección múltiple de características (features)
- **Validación de Formulario**: Validación antes de entrenar
- **Feedback en Tiempo Real**: Notificaciones de progreso

##### 4️⃣ Modelos
- **Lista de Modelos**: Todos los modelos entrenados
- **Información Detallada**:
  - Nombre y tipo de modelo
  - Algoritmo utilizado
  - Dataset asociado
  - Columna objetivo
  - Features utilizados
  - Métricas de evaluación
- **Acciones**:
  - Descargar reporte en Excel
  - Eliminar modelo

## 🛠️ Stack Tecnológico

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Lenguaje**: TypeScript
- **Estilos**: Tailwind CSS
- **Componentes UI**: shadcn/ui + Radix UI
- **Gráficos**: Recharts
- **Tablas**: Custom components con Radix UI
- **Formularios**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Fechas**: date-fns

## 🔧 Instalación y Configuración

### 1. Instalar Dependencias

```bash
pnpm install
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env.local` en la raíz del proyecto:

```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### 3. Iniciar el Servidor de Desarrollo

```bash
pnpm dev
```

El frontend estará disponible en: `http://localhost:3000`

## 🚀 Flujo de Trabajo

### 1. Cargar Datos
1. Ir a **Entrenamiento** → **Cargar Datos**
2. Subir archivo CSV/Excel o cargar dataset de ejemplo
3. Ver confirmación de carga exitosa

### 2. Explorar Datos
1. Ir a pestaña **Explorar**
2. Seleccionar dataset del dropdown
3. Ver vista previa de datos
4. Analizar estadísticas descriptivas
5. Generar histogramas por columna

### 3. Entrenar Modelo
1. Ir a pestaña **Entrenar**
2. Seleccionar dataset
3. Elegir tipo de modelo (Clasificación/Regresión/Clustering)
4. Seleccionar algoritmo
5. Elegir columna objetivo (si aplica)
6. Seleccionar características (features)
7. Click en "Entrenar Modelo"
8. Esperar confirmación

### 4. Gestionar Modelos
1. Ir a pestaña **Modelos**
2. Ver lista de modelos entrenados
3. Ver métricas de cada modelo
4. Descargar reportes en Excel
5. Eliminar modelos no necesarios