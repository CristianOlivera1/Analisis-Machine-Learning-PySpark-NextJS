"use client";

import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Upload, Database, BarChart3, BrainCircuit, Download, Trash2 } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import type { Dataset, Model, ModelType, TrainingRequest } from "@/lib/types";
import { DataTable } from "@/components/tables/data-table";
import { StatsTable } from "@/components/tables/stats-table";
import { HistogramChart } from "@/components/charts/histogram-chart";
import { useToast } from "@/hooks/use-toast";

export default function Training() {
  const [activeTab, setActiveTab] = useState("upload");
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [models, setModels] = useState<Model[]>([]);
  const [modelTypes, setModelTypes] = useState<ModelType[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadDatasets();
    loadModels();
    loadModelTypes();
  }, []);

  const loadDatasets = async () => {
    try {
      const data = await apiClient.listDatasets();
      setDatasets(data);
    } catch (error) {
      console.error('Error loading datasets:', error);
    }
  };

  const loadModels = async () => {
    try {
      const data = await apiClient.listModels();
      setModels(data);
    } catch (error) {
      console.error('Error loading models:', error);
    }
  };

  const loadModelTypes = async () => {
    try {
      const data = await apiClient.getModelTypes();
      console.log('Model types loaded:', data);
      setModelTypes(data);
    } catch (error) {
      console.error('Error loading model types:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setLoading(true);
      const dataset = await apiClient.uploadDataset(file);
      toast({
        title: "Dataset cargado",
        description: `${dataset.name} se cargó correctamente`,
      });
      loadDatasets();
      setActiveTab("explore");
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Error al cargar el dataset",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const loadSampleDataset = async (sampleName: string) => {
    try {
      setLoading(true);
      const dataset = await apiClient.loadSampleDataset(sampleName);
      toast({
        title: "Dataset de ejemplo cargado",
        description: `${dataset.name} se cargó correctamente`,
      });
      loadDatasets();
      setActiveTab("explore");
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Error al cargar el dataset",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const deleteDataset = async (datasetId: string) => {
    try {
      await apiClient.deleteDataset(datasetId);
      toast({
        title: "Dataset eliminado",
        description: "El dataset se eliminó correctamente",
      });
      loadDatasets();
      if (selectedDataset?.id === datasetId) {
        setSelectedDataset(null);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Error al eliminar el dataset",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Entrenamiento de Modelos</h1>
        <p className="text-muted-foreground">
          Carga datos, explora y entrena modelos de Machine Learning
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="upload">
            <Upload className="h-4 w-4 mr-2" />
            Cargar Datos
          </TabsTrigger>
          <TabsTrigger value="explore">
            <BarChart3 className="h-4 w-4 mr-2" />
            Explorar
          </TabsTrigger>
          <TabsTrigger value="train">
            <BrainCircuit className="h-4 w-4 mr-2" />
            Entrenar
          </TabsTrigger>
          <TabsTrigger value="models">
            <Database className="h-4 w-4 mr-2" />
            Modelos
          </TabsTrigger>
        </TabsList>

        <TabsContent value="upload" className="space-y-4">
          <UploadTab
            datasets={datasets}
            loading={loading}
            onFileUpload={handleFileUpload}
            onLoadSample={loadSampleDataset}
            onDeleteDataset={deleteDataset}
          />
        </TabsContent>

        <TabsContent value="explore" className="space-y-4">
          <ExploreTab
            datasets={datasets}
            selectedDataset={selectedDataset}
            onSelectDataset={setSelectedDataset}
          />
        </TabsContent>

        <TabsContent value="train" className="space-y-4">
          <TrainTab
            datasets={datasets}
            modelTypes={modelTypes}
            onModelTrained={loadModels}
          />
        </TabsContent>

        <TabsContent value="models" className="space-y-4">
          <ModelsTab models={models} onRefresh={loadModels} />
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Componente para la pestaña de carga
function UploadTab({
  datasets,
  loading,
  onFileUpload,
  onLoadSample,
  onDeleteDataset,
}: {
  datasets: Dataset[];
  loading: boolean;
  onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onLoadSample: (sampleName: string) => void;
  onDeleteDataset: (id: string) => void;
}) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Subir Dataset</CardTitle>
          <CardDescription>
            Carga un archivo CSV o Excel con tus datos
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid w-full items-center gap-1.5">
            <Label htmlFor="file">Archivo</Label>
            <Input
              id="file"
              type="file"
              accept=".csv,.xlsx,.xls"
              onChange={onFileUpload}
              disabled={loading}
            />
            <p className="text-xs text-muted-foreground">
              Formatos soportados: CSV, Excel (.xlsx, .xls)
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Datasets de Ejemplo</CardTitle>
          <CardDescription>
            Carga datos de ejemplo para probar
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {['iris', 'wine', 'diabetes'].map((sample) => (
            <Button
              key={sample}
              variant="outline"
              className="w-full justify-start"
              onClick={() => onLoadSample(sample)}
              disabled={loading}
            >
              <Database className="h-4 w-4 mr-2" />
              {sample.charAt(0).toUpperCase() + sample.slice(1)}
            </Button>
          ))}
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Datasets Cargados ({datasets.length})</CardTitle>
          <CardDescription>
            Gestiona tus conjuntos de datos
          </CardDescription>
        </CardHeader>
        <CardContent>
          {datasets.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No hay datasets cargados aún
            </div>
          ) : (
            <div className="space-y-2">
              {datasets?.map((dataset) => (
                <div
                  key={dataset.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent"
                >
                  <div className="space-y-1">
                    <p className="font-medium">{dataset.name}</p>
                    <div className="flex gap-2 text-xs text-muted-foreground">
                      <span>{dataset.rows} filas</span>
                      <span>×</span>
                      <span>{dataset.columns} columnas</span>
                      <Badge variant="outline" className="ml-2">{dataset.id}</Badge>
                    </div>
                  </div>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => onDeleteDataset(dataset.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// Componente para la pestaña de exploración
function ExploreTab({
  datasets,
  selectedDataset,
  onSelectDataset,
}: {
  datasets: Dataset[];
  selectedDataset: Dataset | null;
  onSelectDataset: (dataset: Dataset | null) => void;
}) {
  const [preview, setPreview] = useState<any>(null);
  const [statistics, setStatistics] = useState<any>(null);
  const [histogram, setHistogram] = useState<any>(null);
  const [selectedColumn, setSelectedColumn] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedDataset) {
      loadPreview();
      loadStatistics();
    }
  }, [selectedDataset]);

  const loadPreview = async () => {
    if (!selectedDataset) return;
    try {
      setLoading(true);
      const data = await apiClient.getDatasetPreview(selectedDataset.id, 10);
      setPreview(data);
    } catch (error) {
      console.error('Error loading preview:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    if (!selectedDataset) return;
    try {
      const data = await apiClient.getStatistics(selectedDataset.id);
      setStatistics(data);
    } catch (error) {
      console.error('Error loading statistics:', error);
    }
  };

  const loadHistogram = async (column: string) => {
    if (!selectedDataset) return;
    try {
      const data = await apiClient.getHistogram(selectedDataset.id, column, 20);
      setHistogram(data);
    } catch (error) {
      console.error('Error loading histogram:', error);
    }
  };

  if (datasets.length === 0) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-muted-foreground">
            <Database className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p>No hay datasets disponibles</p>
            <p className="text-sm">Carga un dataset primero</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Seleccionar Dataset</CardTitle>
        </CardHeader>
        <CardContent>
          <Select
            value={selectedDataset?.id || ""}
            onValueChange={(value) => {
              const dataset = datasets.find((d) => d.id === value);
              onSelectDataset(dataset || null);
            }}
          >
            <SelectTrigger>
              <SelectValue placeholder="Selecciona un dataset" />
            </SelectTrigger>
            <SelectContent>
              {datasets?.map((dataset) => (
                <SelectItem key={dataset.id} value={dataset.id}>
                  {dataset.name} ({dataset.rows} × {dataset.columns})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {selectedDataset && (
        <>
          <Card className="w-full max-w-[1200px] overflow-hidden">
            <CardHeader>
              <CardTitle>Vista Previa</CardTitle>
              <CardDescription>
                Primeras 10 filas del dataset
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0 sm:p-6"> {/* p-0 en móvil ayuda al scroll */}
              {loading ? (
                <Skeleton className="h-64 w-full" />
              ) : preview ? (
                <div className="w-full">
                  <DataTable data={preview.data} maxRows={10} />
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No se pudo cargar la vista previa
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="w-full max-w-[1200px] overflow-hidden">
            <CardHeader>
              <CardTitle>Estadísticas Descriptivas</CardTitle>
              <CardDescription>
                Análisis estadístico de las columnas numéricas
              </CardDescription>
            </CardHeader>
            <CardContent>
              {statistics ? (
                <StatsTable statistics={statistics} />
              ) : (
                <Skeleton className="h-48 w-full" />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Histograma</CardTitle>
              <CardDescription>
                Distribución de valores de una columna
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Select
                value={selectedColumn}
                onValueChange={(value) => {
                  setSelectedColumn(value);
                  loadHistogram(value);
                }}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecciona una columna" />
                </SelectTrigger>
                <SelectContent>
                  {selectedDataset.column_names?.map((column) => (
                    <SelectItem key={column} value={column}>
                      {column}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {histogram && <HistogramChart data={histogram} />}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

// Componente para la pestaña de entrenamiento
function TrainTab({
  datasets,
  modelTypes,
  onModelTrained,
}: {
  datasets: Dataset[];
  modelTypes: ModelType[];
  onModelTrained: () => void;
}) {
  const [selectedDataset, setSelectedDataset] = useState<string>("");
  const [modelType, setModelType] = useState<string>("");
  const [algorithm, setAlgorithm] = useState<string>("");
  const [targetColumn, setTargetColumn] = useState<string>("");
  const [featureColumns, setFeatureColumns] = useState<string[]>([]);
  const [modelName, setModelName] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const selectedDatasetObj = datasets?.find((d) => d.id === selectedDataset);
  const selectedModelType = modelTypes?.find((mt) => mt.type === modelType);

  const handleTrain = async () => {
    if (!selectedDataset || !modelType || !algorithm || featureColumns.length === 0) {
      toast({
        title: "Error",
        description: "Completa todos los campos requeridos",
        variant: "destructive",
      });
      return;
    }

    if (modelType !== 'clustering' && !targetColumn) {
      toast({
        title: "Error",
        description: "Selecciona una columna objetivo",
        variant: "destructive",
      });
      return;
    }

    try {
      setLoading(true);
      const request: TrainingRequest = {
        dataset_id: selectedDataset,
        model_type: modelType as any,
        algorithm,
        feature_columns: featureColumns,
        model_name: modelName || undefined,
      };

      if (modelType !== 'clustering') {
        request.target_column = targetColumn;
      }

      await apiClient.trainModel(request);
      toast({
        title: "Modelo entrenado",
        description: "El modelo se entrenó correctamente",
      });
      onModelTrained();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Error al entrenar el modelo",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const toggleFeatureColumn = (column: string) => {
    setFeatureColumns((prev) =>
      prev.includes(column)
        ? prev.filter((c) => c !== column)
        : [...prev, column]
    );
  };

  if (datasets.length === 0) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-muted-foreground">
            <BrainCircuit className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p>No hay datasets disponibles</p>
            <p className="text-sm">Carga un dataset primero</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Entrenar Nuevo Modelo</CardTitle>
        <CardDescription>
          Configura y entrena un modelo de Machine Learning
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="dataset">Dataset</Label>
            <Select value={selectedDataset} onValueChange={setSelectedDataset}>
              <SelectTrigger id="dataset">
                <SelectValue placeholder="Selecciona un dataset" />
              </SelectTrigger>
              <SelectContent>
                {datasets?.map((dataset) => (
                  <SelectItem key={dataset.id} value={dataset.id}>
                    {dataset.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="model-name">Nombre del Modelo (opcional)</Label>
            <Input
              id="model-name"
              placeholder="Mi modelo"
              value={modelName}
              onChange={(e) => setModelName(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="model-type">Tipo de Modelo</Label>
            <Select value={modelType} onValueChange={setModelType}>
              <SelectTrigger id="model-type">
                <SelectValue placeholder="Selecciona el tipo" />
              </SelectTrigger>
              <SelectContent>
                {modelTypes?.map((type) => (
                  <SelectItem key={type.type} value={type.type}>
                    {type.type.charAt(0).toUpperCase() + type.type.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="algorithm">Algoritmo</Label>
            <Select
              value={algorithm}
              onValueChange={setAlgorithm}
              disabled={!modelType}
            >
              <SelectTrigger id="algorithm">
                <SelectValue placeholder="Selecciona el algoritmo" />
              </SelectTrigger>
              <SelectContent>
                {selectedModelType?.algorithms.map((algo) => (
                  <SelectItem key={algo.name} value={algo.name}>
                    {algo.displayName || algo.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {selectedDatasetObj && modelType !== 'clustering' && (
          <div className="space-y-2">
            <Label htmlFor="target">Columna Objetivo</Label>
            <Select value={targetColumn} onValueChange={setTargetColumn}>
              <SelectTrigger id="target">
                <SelectValue placeholder="Selecciona la columna objetivo" />
              </SelectTrigger>
              <SelectContent>
                {selectedDatasetObj?.column_names?.map((column) => (
                  <SelectItem key={column} value={column}>
                    {column}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {selectedDatasetObj && (
          <div className="space-y-2">
            <Label>Características (Features)</Label>
            <div className="border rounded-lg p-4 space-y-2 max-h-48 overflow-y-auto">
              {selectedDatasetObj?.column_names
                .filter((col) => col !== targetColumn)
                .map((column) => (
                  <div key={column} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={column}
                      checked={featureColumns.includes(column)}
                      onChange={() => toggleFeatureColumn(column)}
                      className="rounded"
                    />
                    <Label htmlFor={column} className="cursor-pointer">
                      {column}
                    </Label>
                  </div>
                ))}
            </div>
            <p className="text-xs text-muted-foreground">
              {featureColumns.length} columnas seleccionadas
            </p>
          </div>
        )}

        <Button
          onClick={handleTrain}
          disabled={loading}
          className="w-full"
        >
          {loading ? "Entrenando..." : "Entrenar Modelo"}
        </Button>
      </CardContent>
    </Card>
  );
}

// Componente para la pestaña de modelos
function ModelsTab({
  models,
  onRefresh,
}: {
  models: Model[];
  onRefresh: () => void;
}) {
  const { toast } = useToast();

  const deleteModel = async (modelId: string) => {
    try {
      await apiClient.deleteModel(modelId);
      toast({
        title: "Modelo eliminado",
        description: "El modelo se eliminó correctamente",
      });
      onRefresh();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Error al eliminar el modelo",
        variant: "destructive",
      });
    }
  };

  const downloadReport = async (modelId: string) => {
    try {
      const blob = await apiClient.generateReport(undefined, modelId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `model-${modelId}-report.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast({
        title: "Reporte descargado",
        description: "El reporte se descargó correctamente",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Error al descargar el reporte",
        variant: "destructive",
      });
    }
  };

  if (models.length === 0) {
    return (
      <Card>
        <CardContent className="py-8">
          <div className="text-center text-muted-foreground">
            <BrainCircuit className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p>No hay modelos entrenados aún</p>
            <p className="text-sm">Entrena tu primer modelo</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Modelos Entrenados ({models.length})</CardTitle>
          <CardDescription>
            Gestiona y utiliza tus modelos de ML
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {models?.map((model) => (
              <div
                key={model.id}
                className="border rounded-lg p-4 space-y-3"
              >
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <h3 className="font-semibold">{model.name}</h3>
                    <div className="flex gap-2">
                      <Badge variant="secondary">{model.model_type}</Badge>
                      <Badge variant="outline">{model.algorithm}</Badge>
                      <Badge variant="outline" className="text-xs">
                        {model.id}
                      </Badge>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => downloadReport(model.id)}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => deleteModel(model.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Dataset:</span>{" "}
                    {model.dataset_id}
                  </div>
                  <div>
                    <span className="text-muted-foreground">Target:</span>{" "}
                    {model.target_column || 'N/A'}
                  </div>
                  <div className="col-span-2">
                    <span className="text-muted-foreground">Features:</span>{" "}
                    {model.feature_columns?.join(', ') || 'N/A'}
                  </div>
                </div>

                {model.metrics && Object.keys(model.metrics).length > 0 && (
                  <div className="border-t pt-3">
                    <p className="text-sm font-medium mb-2">Métricas:</p>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {Object.entries(model.metrics).map(([key, value]) => (
                        <div key={key}>
                          <span className="text-muted-foreground">{key}:</span>{" "}
                          {typeof value === 'number' 
                            ? value.toFixed(4) 
                            : typeof value === 'object' 
                              ? JSON.stringify(value)
                              : String(value)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}