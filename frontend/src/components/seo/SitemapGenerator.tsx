import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import { FileCode, Download, Copy, Check } from 'lucide-react';

export function SitemapGenerator({ siteUrl, pages }: { siteUrl: string; pages: string[] }) {
  const [sitemap, setSitemap] = useState<string>('');
  const [isCopied, setIsCopied] = useState(false);

  const handleGenerate = async () => {
    try {
      const response = await apiClient.post('/api/seo/sitemap', {
        base_url: siteUrl,
        pages: pages,
      });
      setSitemap(response.data);
      toast.success("Sitemap generated successfully!");
    } catch (error) {
      console.error('Error generating sitemap:', error);
      toast.error("Failed to generate sitemap.");
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(sitemap);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
    toast.success("Copied to clipboard");
  };

  const handleDownload = () => {
    const blob = new Blob([sitemap], { type: 'text/xml' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sitemap.xml';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileCode className="h-5 w-5" />
          Sitemap Generator
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Base URL</Label>
            <Input value={siteUrl} disabled />
          </div>
          <div className="space-y-2">
            <Label>Pages Included</Label>
            <Input value={`${pages.length} pages`} disabled />
          </div>
        </div>

        <Button onClick={handleGenerate} className="w-full">
          Generate Sitemap.xml
        </Button>

        {sitemap && (
          <div className="space-y-2 animate-in fade-in slide-in-from-top-2">
            <div className="relative">
              <pre className="p-4 bg-muted rounded-lg overflow-x-auto text-xs font-mono max-h-[300px]">
                {sitemap}
              </pre>
              <div className="absolute top-2 right-2 flex gap-2">
                <Button size="icon" variant="secondary" className="h-8 w-8" onClick={handleCopy}>
                  {isCopied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </Button>
                <Button size="icon" variant="secondary" className="h-8 w-8" onClick={handleDownload}>
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
