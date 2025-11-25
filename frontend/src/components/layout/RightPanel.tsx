import React, { useState } from 'react';
import { 
  Type, 
  Palette, 
  Layout,
  Lightbulb,
  MousePointer2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function RightPanel() {
  return (
    <aside className="w-80 bg-card border-l border-border h-full flex flex-col">
      <Tabs defaultValue="properties" className="w-full h-full flex flex-col">
        <div className="px-4 pt-4 pb-2 border-b border-border">
          <TabsList className="w-full grid grid-cols-2">
            <TabsTrigger value="properties">Properties</TabsTrigger>
            <TabsTrigger value="assistant">Assistant</TabsTrigger>
          </TabsList>
        </div>

        <ScrollArea className="flex-1">
          <TabsContent value="properties" className="p-5 space-y-8 mt-0">
            {/* Typography Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                  <Type className="h-3 w-3" /> Typography
                </h3>
              </div>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs font-medium text-foreground">Font Family</label>
                  <Select defaultValue="inter">
                    <SelectTrigger>
                      <SelectValue placeholder="Select Font" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="inter">Inter</SelectItem>
                      <SelectItem value="roboto">Roboto</SelectItem>
                      <SelectItem value="playfair">Playfair Display</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-foreground">Size (px)</label>
                    <Input type="number" defaultValue="16" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-medium text-foreground">Weight</label>
                    <Select defaultValue="400">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="400">Regular</SelectItem>
                        <SelectItem value="500">Medium</SelectItem>
                        <SelectItem value="600">Semibold</SelectItem>
                        <SelectItem value="700">Bold</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
            </div>

            <Separator />

            {/* Colors Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                  <Palette className="h-3 w-3" /> Colors
                </h3>
              </div>
              
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-xs font-medium text-foreground">Text Color</label>
                  <div className="flex gap-2 items-center">
                    <div className="h-9 w-9 rounded-md border border-border bg-foreground shadow-sm" />
                    <Input defaultValue="#1C1917" className="font-mono" />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-medium text-foreground">Background</label>
                  <div className="flex gap-2 items-center">
                    <div className="h-9 w-9 rounded-md border border-border bg-background shadow-sm" />
                    <Input defaultValue="#FCFAF7" className="font-mono" />
                  </div>
                </div>
              </div>
            </div>

            <Separator />

            {/* Layout Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                  <Layout className="h-3 w-3" /> Layout
                </h3>
              </div>
              
              <div className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <label className="text-xs font-medium text-foreground">Padding</label>
                    <span className="text-xs text-muted-foreground">24px</span>
                  </div>
                  <Slider defaultValue={[24]} max={100} step={4} />
                </div>
                
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-foreground">Auto Margin</label>
                  <Switch />
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="assistant" className="p-5 space-y-6 mt-0">
            {/* AI Suggestions Panel */}
            <Card className="bg-primary/5 border-primary/10 shadow-none">
              <CardContent className="p-4">
                <div className="flex items-start gap-3">
                  <Lightbulb className="h-5 w-5 text-amber-500 mt-0.5 shrink-0" />
                  <div className="space-y-3">
                    <p className="text-sm text-foreground leading-relaxed">
                      Consider increasing the contrast of your primary buttons to improve accessibility.
                    </p>
                    <Button size="sm" className="w-full bg-primary text-primary-foreground hover:bg-primary-hover">
                      Apply Fix
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="space-y-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                Active Elements
              </h3>
              <div className="p-3 border border-border rounded-lg bg-background flex items-center gap-3 shadow-sm">
                <MousePointer2 className="h-4 w-4 text-primary" />
                <div>
                  <p className="text-sm font-medium">Hero Section</p>
                  <p className="text-xs text-muted-foreground">Currently selected</p>
                </div>
              </div>
            </div>
          </TabsContent>
        </ScrollArea>
      </Tabs>
    </aside>
  );
}
