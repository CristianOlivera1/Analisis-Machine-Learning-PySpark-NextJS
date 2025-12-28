"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface StatsTableProps {
  statistics: any; // { numeric: {...}, categorical: {...} }
}

export function StatsTable({ statistics }: StatsTableProps) {
  if (!statistics || (!statistics.numeric && !statistics.categorical)) {
    return (
      <div className="flex items-center justify-center h-32 text-muted-foreground border rounded-md">
        No hay estadísticas para mostrar
      </div>
    );
  }

  const numericStats = statistics.numeric || {};
  const categoricalStats = statistics.categorical || {};
  const hasNumeric = Object.keys(numericStats).length > 0;
  const hasCategorical = Object.keys(categoricalStats).length > 0;

  if (!hasNumeric && !hasCategorical) {
    return (
      <div className="flex items-center justify-center h-32 text-muted-foreground border rounded-md">
        No hay estadísticas para mostrar
      </div>
    );
  }

  return (
    <Tabs defaultValue={hasNumeric ? "numeric" : "categorical"} className="w-full">
      <TabsList>
        {hasNumeric && <TabsTrigger value="numeric">Numéricas ({Object.keys(numericStats).length})</TabsTrigger>}
        {hasCategorical && <TabsTrigger value="categorical">Categóricas ({Object.keys(categoricalStats).length})</TabsTrigger>}
      </TabsList>

      {hasNumeric && (
        <TabsContent value="numeric" className="mt-4">
          <div className="rounded-md border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Columna</TableHead>
                  <TableHead className="text-right">Count</TableHead>
                  <TableHead className="text-right">Media</TableHead>
                  <TableHead className="text-right">Desv. Est.</TableHead>
                  <TableHead className="text-right">Mín</TableHead>
                  <TableHead className="text-right">Q1</TableHead>
                  <TableHead className="text-right">Mediana</TableHead>
                  <TableHead className="text-right">Q3</TableHead>
                  <TableHead className="text-right">Máx</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(numericStats).map(([column, stat]: [string, any]) => (
                  <TableRow key={column}>
                    <TableCell className="font-medium">{column}</TableCell>
                    <TableCell className="text-right">{stat.count}</TableCell>
                    <TableCell className="text-right">{formatNumber(stat.mean)}</TableCell>
                    <TableCell className="text-right">{formatNumber(stat.std)}</TableCell>
                    <TableCell className="text-right">{formatNumber(stat.min)}</TableCell>
                    <TableCell className="text-right">{formatNumber(stat.quartiles?.q1)}</TableCell>
                    <TableCell className="text-right">{formatNumber(stat.quartiles?.median)}</TableCell>
                    <TableCell className="text-right">{formatNumber(stat.quartiles?.q3)}</TableCell>
                    <TableCell className="text-right">{formatNumber(stat.max)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      )}

      {hasCategorical && (
        <TabsContent value="categorical" className="mt-4">
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Columna</TableHead>
                  <TableHead className="text-right">Count</TableHead>
                  <TableHead className="text-right">Únicos</TableHead>
                  <TableHead>Más Frecuente</TableHead>
                  <TableHead className="text-right">Frecuencia</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(categoricalStats).map(([column, stat]: [string, any]) => (
                  <TableRow key={column}>
                    <TableCell className="font-medium">{column}</TableCell>
                    <TableCell className="text-right">{stat.count}</TableCell>
                    <TableCell className="text-right">{stat.unique}</TableCell>
                    <TableCell>{stat.top || 'N/A'}</TableCell>
                    <TableCell className="text-right">{stat.freq}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      )}
    </Tabs>
  );
}

function formatNumber(value: number | string | undefined | null): string {
  if (value === undefined || value === null) return '-';
  const num = typeof value === 'string' ? parseFloat(value) : value;
  if (isNaN(num)) return '-';
  return num.toFixed(4);
}
