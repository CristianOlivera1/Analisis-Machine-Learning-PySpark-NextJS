"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface DataTableProps {
  data: Record<string, any>[];
  columns?: string[];
  maxRows?: number;
}

export function DataTable({ data, columns, maxRows = 10 }: DataTableProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-32 text-muted-foreground border rounded-md">
        No hay datos para mostrar
      </div>
    );
  }

  const displayColumns = columns || Object.keys(data[0] || {});
  const displayData = maxRows ? data.slice(0, maxRows) : data;
 return (
    <div className="w-full rounded-md border"> 
      <div className="relative w-full overflow-x-auto">
        <Table className="w-full">
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              {displayColumns.map((column) => (
                <TableHead 
                  key={column} 
                  className="whitespace-nowrap px-4 font-bold text-primary"
                >
                  {column}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {displayData.map((row, index) => (
              <TableRow key={index}>
                {displayColumns.map((column) => (
                  <TableCell 
                    key={`${index}-${column}`} 
                    className="whitespace-nowrap px-4"
                  >
                    {formatValue(row[column])}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      
      {maxRows && data.length > maxRows && (
        <div className="text-[10px] text-muted-foreground text-center py-2 border-t bg-muted/20">
          Mostrando {maxRows} de {data.length} filas
        </div>
      )}
    </div>
  );
}

function formatValue(value: any): string {
  if (value === null || value === undefined) {
    return '-';
  }
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value.toString() : value.toFixed(4);
  }
  if (typeof value === 'boolean') {
    return value ? 'Sí' : 'No';
  }
  return String(value);
}
