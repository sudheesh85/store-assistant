'use client';

import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Download, FileSpreadsheet } from 'lucide-react';
import { useState } from 'react';

interface DataVisualizationProps {
  data: {
    columns: string[];
    rows: any[][];
  };
  visualization?: 'bar' | 'line' | 'pie' | 'table';
}

const COLORS = ['#0ea5e9', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#ef4444', '#6366f1'];

export default function DataVisualization({ data, visualization }: DataVisualizationProps) {
  const [showTable, setShowTable] = useState(true);

  // Convert rows to chart data format
  const chartData = data.rows.map((row, index) => {
    const obj: any = { name: `Item ${index + 1}` };
    data.columns.forEach((col, colIndex) => {
      obj[col] = row[colIndex];
    });
    return obj;
  });

  // Auto-detect best visualization if not specified
  const getVisualizationType = (): 'bar' | 'line' | 'pie' | 'table' => {
    if (visualization) return visualization;
    
    // Default to table for small datasets, bar chart for larger ones
    if (data.rows.length <= 5 && data.columns.length === 2) {
      return 'pie';
    }
    if (data.rows.length > 20) {
      return 'table';
    }
    return 'bar';
  };

  const visType = getVisualizationType();

  // Export to CSV
  const exportToCSV = () => {
    const headers = data.columns.join(',');
    const rows = data.rows.map(row => 
      row.map(cell => `"${cell}"`).join(',')
    ).join('\n');
    const csv = `${headers}\n${rows}`;
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `data-export-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  // Prepare data for charts
  const firstColumn = data.columns[0];
  const secondColumn = data.columns[1] || data.columns[0];

  // For pie chart, use first two columns
  const pieData = data.rows.slice(0, 10).map((row, index) => ({
    name: String(row[0] || `Item ${index + 1}`),
    value: Number(row[1]) || 0,
  }));

  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Results</h3>
        <div className="flex gap-2">
          <button
            onClick={() => setShowTable(!showTable)}
            className="px-3 py-1.5 text-sm bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          >
            {showTable ? 'Hide' : 'Show'} Table
          </button>
          <button
            onClick={exportToCSV}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            Download CSV
          </button>
        </div>
      </div>

      {/* Chart Visualization */}
      {visType !== 'table' && (
        <div className="mb-4" style={{ height: '300px' }}>
          <ResponsiveContainer width="100%" height="100%">
            {visType === 'bar' ? (
              <BarChart data={chartData.slice(0, 20)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey={firstColumn} 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Legend />
                {data.columns.slice(1).map((col, index) => (
                  <Bar 
                    key={col} 
                    dataKey={col} 
                    fill={COLORS[index % COLORS.length]} 
                  />
                ))}
              </BarChart>
            ) : visType === 'line' ? (
              <LineChart data={chartData.slice(0, 20)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey={firstColumn}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Legend />
                {data.columns.slice(1).map((col, index) => (
                  <Line 
                    key={col} 
                    type="monotone" 
                    dataKey={col} 
                    stroke={COLORS[index % COLORS.length]}
                    strokeWidth={2}
                  />
                ))}
              </LineChart>
            ) : (
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            )}
          </ResponsiveContainer>
        </div>
      )}

      {/* Table View */}
      {showTable && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                {data.columns.map((col, index) => (
                  <th
                    key={index}
                    className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                  >
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
              {data.rows.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                  {row.map((cell, cellIndex) => (
                    <td
                      key={cellIndex}
                      className="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100"
                    >
                      {cell !== null && cell !== undefined ? String(cell) : '-'}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {data.rows.length === 0 && (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              No data available
            </div>
          )}
        </div>
      )}
    </div>
  );
}

