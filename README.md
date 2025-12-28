# 🎨 Frontend - ML PySpark Web App

Aplicación web moderna de análisis y predicción de datos con Machine Learning, construida con Next.js 15, TypeScript y shadcn/ui.

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

### Componentes UI Implementados
- ✅ Button
- ✅ Input
- ✅ Card
- ✅ Badge
- ✅ Label
- ✅ Select
- ✅ Table
- ✅ Tabs
- ✅ Toast (Notificaciones)
- ✅ Skeleton (Loading states)
- ✅ Sidebar
- ✅ Separator
- ✅ Breadcrumb
- ✅ Sheet
- ✅ Tooltip

## 📁 Estructura del Proyecto

```
mlpysparkfrontend/
├── app/
│   ├── admin/
│   │   ├── layout.tsx              # Layout con sidebar y header
│   │   ├── page.tsx                # Dashboard principal
│   │   └── entrenamiento/
│   │       └── page.tsx            # Página de entrenamiento
│   ├── components/
│   │   ├── app-sidebar.tsx         # Sidebar de navegación
│   │   └── header.tsx              # Header con breadcrumbs
│   ├── globals.css                 # Estilos globales
│   ├── layout.tsx                  # Root layout
│   └── page.tsx                    # Landing page
│
├── components/
│   ├── charts/                     # Componentes de gráficos
│   │   └── histogram-chart.tsx     # Histograma
│   │
│   ├── tables/                     # Componentes de tablas
│   │   ├── data-table.tsx          # Tabla de datos genérica
│   │   └── stats-table.tsx         # Tabla de estadísticas
│   │
│   └── ui/                         # Componentes UI de shadcn
│       ├── badge.tsx
│       ├── breadcrumb.tsx
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── label.tsx
│       ├── select.tsx
│       ├── separator.tsx
│       ├── sheet.tsx
│       ├── sidebar.tsx
│       ├── skeleton.tsx
│       ├── table.tsx
│       ├── tabs.tsx
│       ├── toast.tsx
│       ├── toaster.tsx
│       └── tooltip.tsx
│
├── hooks/
│   ├── use-mobile.ts               # Hook para detección mobile
│   └── use-toast.ts                # Hook para notificaciones
│
├── lib/
│   ├── api-client.ts               # Cliente HTTP para el backend
│   ├── types.ts                    # Tipos TypeScript
│   └── utils.ts                    # Utilidades
│
├── .env.local                      # Variables de entorno
├── components.json                 # Configuración shadcn
├── next.config.ts                  # Configuración Next.js
├── package.json                    # Dependencias
├── postcss.config.mjs              # Configuración PostCSS
├── tailwind.config.ts              # Configuración Tailwind
└── tsconfig.json                   # Configuración TypeScript
```

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

## 📡 Integración con Backend

### API Client

El archivo `lib/api-client.ts` contiene todos los métodos para comunicarse con el backend Flask:

#### Dataset Endpoints
- `uploadDataset(file)` - Subir archivo CSV/Excel
- `listDatasets()` - Listar todos los datasets
- `getDatasetPreview(id, limit)` - Vista previa de datos
- `deleteDataset(id)` - Eliminar dataset
- `loadSampleDataset(name)` - Cargar dataset de ejemplo

#### Exploration Endpoints
- `getStatistics(id)` - Estadísticas descriptivas
- `getHistogram(id, column, bins)` - Histograma

#### Model Endpoints
- `getModelTypes()` - Tipos de modelos disponibles
- `trainModel(request)` - Entrenar nuevo modelo
- `listModels()` - Listar todos los modelos
- `deleteModel(id)` - Eliminar modelo

#### Report Endpoints
- `generateReport(datasetId, modelId)` - Generar reporte Excel

## 🎨 Componentes Personalizados

### HistogramChart
Histograma especializado:

```tsx
<HistogramChart
  data={{
    bins: [0, 1, 2, 3],
    counts: [10, 20, 15, 5],
    column: "edad"
  }}
  height={300}
/>
```

### DataTable
Tabla de datos con paginación:

```tsx
<DataTable
  data={rows}
  columns={columnNames}
  maxRows={10}
/>
```

### StatsTable
Tabla de estadísticas descriptivas:

```tsx
<StatsTable
  statistics={stats}
/>
```

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

## 🎯 Características Avanzadas

### Manejo de Errores
- Notificaciones toast para errores y éxitos
- Mensajes descriptivos de error
- Validación de formularios

### Estados de Carga
- Skeletons durante carga de datos
- Botones deshabilitados durante operaciones
- Indicadores de progreso

### Responsive Design
- Diseño adaptable a móviles y tablets
- Sidebar colapsable
- Grids responsivos

### Accesibilidad
- Componentes Radix UI con ARIA
- Navegación por teclado
- Labels y descripciones

## 🔮 Próximas Mejoras

### Funcionalidades Pendientes
- [ ] Visualización de predicciones
- [ ] Comparación de modelos
- [ ] Exportar gráficos como imágenes
- [ ] Gráficos de correlación interactivos
- [ ] Filtrado avanzado de datos
- [ ] Búsqueda de datasets y modelos
- [ ] Paginación en tablas grandes
- [ ] Modo oscuro/claro

### Optimizaciones
- [ ] Caché de datos
- [ ] Lazy loading de componentes
- [ ] Optimización de imágenes
- [ ] Service Worker para PWA

## 📚 Recursos

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Recharts Documentation](https://recharts.org)
- [Tailwind CSS](https://tailwindcss.com)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)

## 🤝 Contribución

Este proyecto es parte de un sistema completo de análisis y predicción de datos con Machine Learning.

### Backend
- Framework: Flask + PySpark + MLlib
- Arquitectura en capas con mejores prácticas
- Ver: `mlpysparkbackend/README.md`

### Frontend
- Framework: Next.js + TypeScript
- UI moderna y responsive
- Integración completa con backend

---

**¡Frontend completamente implementado y listo para usar!** 🎉
