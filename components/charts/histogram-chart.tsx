"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface HistogramChartProps {
  data: {
    column: string;
    bins: number;
    data: Array<{
      bin: string;
      count: number;
      min: number;
      max: number;
    }>;
  };
  height?: number;
}

export function HistogramChart({ data, height = 300 }: HistogramChartProps) {
  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] text-muted-foreground">
        No hay datos para mostrar
      </div>
    );
  }

  return (
    <div className="space-y-2 pb-8">
      <h4 className="text-sm font-medium">Histograma: {data.column} ({data.bins} bins)</h4>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data.data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="bin" 
            label={{ value: 'Rango', position: 'insideBottom', offset: -5 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis label={{ value: 'Frecuencia', angle: -90, position: 'insideLeft' }} />
          <Tooltip 
            formatter={(value) => [`${value ?? 0} registros`, 'Frecuencia']}
            labelFormatter={(label) => `Rango: ${label}`}
          />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
