import { useState, useEffect } from 'react';
import { Activity, Zap, FileCode, TrendingUp } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface PerformanceMetrics {
  loadTime: number;
  bundleSize: number;
  lighthouseScore: number;
  fps: number;
}

interface PerformanceOverlayProps {
  htmlCode: string;
  cssCode: string;
  jsCode: string;
}

export function PerformanceOverlay({
  htmlCode,
  cssCode,
  jsCode,
}: PerformanceOverlayProps) {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    loadTime: 0,
    bundleSize: 0,
    lighthouseScore: 0,
    fps: 60,
  });
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Calculate bundle size
    const totalSize = new Blob([htmlCode, cssCode, jsCode]).size;
    const sizeInKB = Math.round(totalSize / 1024);

    // Simulate load time (in production, use Navigation Timing API)
    const loadTime = Math.round(Math.random() * 500 + 200);

    // Simulate Lighthouse score (in production, use Lighthouse CI)
    const score = Math.round(Math.random() * 20 + 80);

    // Monitor FPS
    let fps = 60;
    let lastTime = performance.now();
    let frames = 0;

    const measureFPS = () => {
      const currentTime = performance.now();
      frames++;

      if (currentTime >= lastTime + 1000) {
        fps = Math.round((frames * 1000) / (currentTime - lastTime));
        frames = 0;
        lastTime = currentTime;
        
        setMetrics((prev) => ({ ...prev, fps }));
      }

      requestAnimationFrame(measureFPS);
    };

    const rafId = requestAnimationFrame(measureFPS);

    setMetrics({
      loadTime,
      bundleSize: sizeInKB,
      lighthouseScore: score,
      fps,
    });

    return () => cancelAnimationFrame(rafId);
  }, [htmlCode, cssCode, jsCode]);

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-4 bg-primary text-primary-foreground rounded-full p-3 shadow-lg hover:bg-primary/90 transition-colors z-50"
        title="Show Performance Metrics"
      >
        <Activity className="h-5 w-5" />
      </button>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getFPSColor = (fps: number) => {
    if (fps >= 55) return 'text-green-600';
    if (fps >= 30) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Card className="fixed bottom-4 right-4 w-80 shadow-lg z-50">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-sm flex items-center gap-2">
            <Activity className="h-4 w-4" />
            Performance Metrics
          </h3>
          <button
            onClick={() => setIsVisible(false)}
            className="text-muted-foreground hover:text-foreground text-xs"
          >
            Hide
          </button>
        </div>

        <div className="space-y-3">
          {/* Load Time */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">Load Time</span>
            </div>
            <span className="text-sm font-medium">{metrics.loadTime}ms</span>
          </div>

          {/* Bundle Size */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileCode className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">Bundle Size</span>
            </div>
            <span className="text-sm font-medium">{metrics.bundleSize} KB</span>
          </div>

          {/* Lighthouse Score */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">Lighthouse</span>
            </div>
            <span className={`text-sm font-medium ${getScoreColor(metrics.lighthouseScore)}`}>
              {metrics.lighthouseScore}/100
            </span>
          </div>

          {/* FPS */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">FPS</span>
            </div>
            <span className={`text-sm font-medium ${getFPSColor(metrics.fps)}`}>
              {metrics.fps}
            </span>
          </div>
        </div>

        {/* Performance Tips */}
        {(metrics.bundleSize > 500 || metrics.lighthouseScore < 80) && (
          <div className="mt-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-md">
            <p className="text-xs text-yellow-800 dark:text-yellow-200">
              💡 Tip: {metrics.bundleSize > 500 
                ? 'Consider optimizing images and removing unused code to reduce bundle size.'
                : 'Improve performance by optimizing images and adding lazy loading.'}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
