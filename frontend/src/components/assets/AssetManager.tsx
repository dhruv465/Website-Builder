import { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { 
  Upload, 
  Image as ImageIcon, 
  Type, 
  Search, 
  Download,
  Trash2,
  Check,
  X,
} from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { cn } from '@/lib/utils';
import { useDropzone } from 'react-dropzone';

interface Asset {
  id: string;
  filename: string;
  original_filename: string;
  url: string;
  size: number;
  width?: number;
  height?: number;
  format: string;
  optimized: boolean;
}

interface UnsplashPhoto {
  id: string;
  description?: string;
  urls: {
    raw: string;
    full: string;
    regular: string;
    small: string;
    thumb: string;
  };
  user: {
    name: string;
    username: string;
  };
  width: number;
  height: number;
}

interface GoogleFont {
  family: string;
  variants: string[];
  subsets: string[];
  category: string;
}

interface AssetManagerProps {
  onSelectAsset?: (asset: Asset | UnsplashPhoto | GoogleFont) => void;
  onClose?: () => void;
  type?: 'image' | 'font' | 'all';
}

export function AssetManager({ onSelectAsset, onClose, type = 'all' }: AssetManagerProps) {
  const [activeTab, setActiveTab] = useState<'upload' | 'unsplash' | 'fonts'>('upload');
  const [uploadedAssets, setUploadedAssets] = useState<Asset[]>([]);
  const [unsplashPhotos, setUnsplashPhotos] = useState<UnsplashPhoto[]>([]);
  const [googleFonts, setGoogleFonts] = useState<GoogleFont[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<any>(null);

  // Load uploaded assets
  const loadAssets = async () => {
    try {
      const response = await apiClient.get('/api/assets');
      setUploadedAssets(response.data.assets);
    } catch (error) {
      console.error('Failed to load assets:', error);
    }
  };

  // Search Unsplash
  const searchUnsplash = async (query: string) => {
    if (!query.trim()) return;
    
    try {
      const response = await apiClient.get('/api/assets/unsplash/search', {
        params: { query, per_page: 20 },
      });
      setUnsplashPhotos(response.data.results);
    } catch (error) {
      console.error('Failed to search Unsplash:', error);
    }
  };

  // Load Google Fonts
  const loadGoogleFonts = async (search?: string) => {
    try {
      const params: any = {};
      if (search) params.search = search;
      
      const response = await apiClient.get('/api/assets/fonts', { params });
      setGoogleFonts(response.data.fonts);
    } catch (error) {
      console.error('Failed to load fonts:', error);
    }
  };

  // File upload with dropzone
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true);
    
    for (const file of acceptedFiles) {
      try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await apiClient.post('/api/assets/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          params: {
            optimize: true,
          },
        });
        
        setUploadedAssets((prev) => [response.data, ...prev]);
      } catch (error) {
        console.error('Failed to upload file:', error);
      }
    }
    
    setIsUploading(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'],
    },
    multiple: true,
  });

  // Delete asset
  const deleteAsset = async (filename: string) => {
    try {
      await apiClient.delete(`/api/assets/${filename}`);
      setUploadedAssets((prev) => prev.filter((a) => a.filename !== filename));
    } catch (error) {
      console.error('Failed to delete asset:', error);
    }
  };

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  // Load initial data
  useState(() => {
    loadAssets();
    loadGoogleFonts();
  });

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-border">
        <div>
          <h2 className="text-2xl font-bold">Asset Manager</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Upload images, browse stock photos, or select fonts
          </p>
        </div>
        {onClose && (
          <Button variant="ghost" size="icon" onClick={onClose}>
            <X className="h-5 w-5" />
          </Button>
        )}
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)} className="flex-1 flex flex-col">
        <div className="border-b border-border px-6">
          <TabsList>
            <TabsTrigger value="upload">
              <Upload className="h-4 w-4 mr-2" />
              Upload
            </TabsTrigger>
            <TabsTrigger value="unsplash">
              <ImageIcon className="h-4 w-4 mr-2" />
              Stock Photos
            </TabsTrigger>
            <TabsTrigger value="fonts">
              <Type className="h-4 w-4 mr-2" />
              Fonts
            </TabsTrigger>
          </TabsList>
        </div>

        {/* Upload Tab */}
        <TabsContent value="upload" className="flex-1 flex flex-col m-0">
          <div className="p-6 space-y-4">
            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={cn(
                'border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors',
                isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
              )}
            >
              <input {...getInputProps()} />
              <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg font-medium mb-2">
                {isDragActive ? 'Drop files here' : 'Drag & drop images here'}
              </p>
              <p className="text-sm text-muted-foreground mb-4">
                or click to browse (PNG, JPG, GIF, WebP, SVG)
              </p>
              {isUploading && (
                <Badge variant="secondary">Uploading...</Badge>
              )}
            </div>

            {/* Uploaded Assets Grid */}
            <ScrollArea className="h-[400px]">
              <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {uploadedAssets.map((asset) => (
                  <Card
                    key={asset.id}
                    className="group cursor-pointer hover:shadow-lg transition-all"
                    onClick={() => setSelectedAsset(asset)}
                  >
                    <CardContent className="p-2">
                      <div className="aspect-square bg-muted rounded-md overflow-hidden mb-2">
                        <img
                          src={asset.url}
                          alt={asset.original_filename}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        />
                      </div>
                      <p className="text-xs truncate">{asset.original_filename}</p>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-xs text-muted-foreground">
                          {formatFileSize(asset.size)}
                        </span>
                        {asset.optimized && (
                          <Badge variant="secondary" className="text-xs">WebP</Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </div>
        </TabsContent>

        {/* Unsplash Tab */}
        <TabsContent value="unsplash" className="flex-1 flex flex-col m-0">
          <div className="p-6 space-y-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search for photos..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    searchUnsplash(searchQuery);
                  }
                }}
                className="pl-10"
              />
            </div>

            {/* Photos Grid */}
            <ScrollArea className="h-[500px]">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {unsplashPhotos.map((photo) => (
                  <Card
                    key={photo.id}
                    className="group cursor-pointer hover:shadow-lg transition-all"
                    onClick={() => setSelectedAsset(photo)}
                  >
                    <CardContent className="p-2">
                      <div className="aspect-square bg-muted rounded-md overflow-hidden mb-2">
                        <img
                          src={photo.urls.small}
                          alt={photo.description || 'Unsplash photo'}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                        />
                      </div>
                      <p className="text-xs text-muted-foreground">
                        by {photo.user.name}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </div>
        </TabsContent>

        {/* Fonts Tab */}
        <TabsContent value="fonts" className="flex-1 flex flex-col m-0">
          <div className="p-6 space-y-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search fonts..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  loadGoogleFonts(e.target.value);
                }}
                className="pl-10"
              />
            </div>

            {/* Fonts List */}
            <ScrollArea className="h-[500px]">
              <div className="space-y-2">
                {googleFonts.map((font) => (
                  <Card
                    key={font.family}
                    className="cursor-pointer hover:shadow-md transition-all"
                    onClick={() => setSelectedAsset(font)}
                  >
                    <CardHeader className="p-4">
                      <CardTitle className="text-lg" style={{ fontFamily: font.family }}>
                        {font.family}
                      </CardTitle>
                      <CardDescription>
                        <Badge variant="outline" className="text-xs mr-2">
                          {font.category}
                        </Badge>
                        {font.variants.length} variants
                      </CardDescription>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            </ScrollArea>
          </div>
        </TabsContent>
      </Tabs>

      {/* Asset Preview Dialog */}
      {selectedAsset && (
        <Dialog open={!!selectedAsset} onOpenChange={() => setSelectedAsset(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {selectedAsset.original_filename || selectedAsset.description || selectedAsset.family}
              </DialogTitle>
              <DialogDescription>
                {selectedAsset.width && selectedAsset.height && (
                  <span>{selectedAsset.width} × {selectedAsset.height}</span>
                )}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4">
              {selectedAsset.url && (
                <img
                  src={selectedAsset.url || selectedAsset.urls?.regular}
                  alt="Preview"
                  className="w-full rounded-lg"
                />
              )}

              <div className="flex gap-2 justify-end">
                {selectedAsset.filename && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => deleteAsset(selectedAsset.filename)}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </Button>
                )}
                <Button
                  onClick={() => {
                    onSelectAsset?.(selectedAsset);
                    setSelectedAsset(null);
                    onClose?.();
                  }}
                >
                  <Check className="h-4 w-4 mr-2" />
                  Use Asset
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
