import React, { Suspense, lazy } from 'react';
import { LoadingSpinner } from '@/components/ui/loading-spinner';

// Lazy load Recharts (heavy dependency)
const LineChart = lazy(() => 
  import('recharts').then(module => ({
    default: module.LineChart
  }))
);

const Line = lazy(() => 
  import('recharts').then(module => ({
    default: module.Line
  }))
);

const XAxis = lazy(() => 
  import('recharts').then(module => ({
    default: module.XAxis
  }))
);

const YAxis = lazy(() => 
  import('recharts').then(module => ({
    default: module.YAxis
  }))
);

const CartesianGrid = lazy(() => 
  import('recharts').then(module => ({
    default: module.CartesianGrid
  }))
);

const Tooltip = lazy(() => 
  import('recharts').then(module => ({
    default: module.Tooltip
  }))
);

const Legend = lazy(() => 
  import('recharts').then(module => ({
    default: module.Legend
  }))
);

interface LazyChartProps {
  data: any[];
  dataKey: string;
  xAxisKey: string;
  width?: number;
  height?: number;
  color?: string;
}

/**
 * Lazy-loaded chart component
 * Recharts library is only loaded when this component is rendered
 */
export const LazyChart: React.FC<LazyChartProps> = ({
  data,
  dataKey,
  xAxisKey,
  width = 600,
  height = 300,
  color = '#8884d8',
}) => {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center" style={{ width, height }}>
          <LoadingSpinner size="lg" />
        </div>
      }
    >
      <LineChart width={width} height={height} data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xAxisKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey={dataKey} stroke={color} />
      </LineChart>
    </Suspense>
  );
};
