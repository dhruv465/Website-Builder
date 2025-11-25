import { Monitor, Smartphone, Tablet, RotateCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export type DeviceType = 'desktop' | 'tablet' | 'mobile';
export type Orientation = 'portrait' | 'landscape';

interface Device {
  type: DeviceType;
  name: string;
  width: number;
  height: number;
  icon: typeof Monitor;
}

const devices: Device[] = [
  { type: 'desktop', name: 'Desktop', width: 1920, height: 1080, icon: Monitor },
  { type: 'tablet', name: 'iPad Pro', width: 1024, height: 1366, icon: Tablet },
  { type: 'tablet', name: 'iPad', width: 768, height: 1024, icon: Tablet },
  { type: 'mobile', name: 'iPhone 14 Pro', width: 393, height: 852, icon: Smartphone },
  { type: 'mobile', name: 'iPhone SE', width: 375, height: 667, icon: Smartphone },
];

interface DeviceEmulatorProps {
  selectedDevice: string;
  orientation: Orientation;
  onDeviceChange: (device: string) => void;
  onOrientationChange: (orientation: Orientation) => void;
}

export function DeviceEmulator({
  selectedDevice,
  orientation,
  onDeviceChange,
  onOrientationChange,
}: DeviceEmulatorProps) {
  const currentDevice = devices.find((d) => d.name === selectedDevice) || devices[0];
  const Icon = currentDevice.icon;

  const toggleOrientation = () => {
    onOrientationChange(orientation === 'portrait' ? 'landscape' : 'portrait');
  };

  return (
    <div className="flex items-center gap-2 px-4 py-2 border-b border-border bg-muted/30">
      <Icon className="h-4 w-4 text-muted-foreground" />
      
      <Select value={selectedDevice} onValueChange={onDeviceChange}>
        <SelectTrigger className="w-[180px] h-8 text-sm">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {devices.map((device) => (
            <SelectItem key={device.name} value={device.name}>
              {device.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Button
        variant="ghost"
        size="sm"
        onClick={toggleOrientation}
        className="h-8 w-8 p-0"
        title={`Switch to ${orientation === 'portrait' ? 'landscape' : 'portrait'}`}
      >
        <RotateCw className="h-4 w-4" />
      </Button>

      <span className="text-xs text-muted-foreground ml-2">
        {orientation === 'portrait'
          ? `${currentDevice.width} × ${currentDevice.height}`
          : `${currentDevice.height} × ${currentDevice.width}`}
      </span>
    </div>
  );
}

export function getDeviceDimensions(deviceName: string, orientation: Orientation) {
  const device = devices.find((d) => d.name === deviceName) || devices[0];
  
  if (orientation === 'landscape') {
    return { width: device.height, height: device.width };
  }
  
  return { width: device.width, height: device.height };
}
