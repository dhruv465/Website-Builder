import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';
import { Loader2, Sparkles } from 'lucide-react';

interface MetaTags {
  title: string;
  description: string;
  keywords: string[];
  og_title?: string;
  og_description?: string;
  twitter_title?: string;
  twitter_description?: string;
}

export function MetaTagEditor({ siteName, content }: { siteName: string; content: string }) {
  const [metaTags, setMetaTags] = useState<MetaTags>({
    title: '',
    description: '',
    keywords: [],
  });
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const response = await apiClient.post('/api/seo/meta-tags', {
        site_name: siteName,
        content: content,
      });
      setMetaTags(response.data);
      toast.success("Meta tags generated successfully!");
    } catch (error) {
      console.error('Error generating meta tags:', error);
      toast.error("Failed to generate meta tags.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">SEO Meta Tags</h2>
        <Button onClick={handleGenerate} disabled={isGenerating}>
          {isGenerating ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
          Generate with AI
        </Button>
      </div>

      <Tabs defaultValue="basic" className="w-full">
        <TabsList>
          <TabsTrigger value="basic">Basic</TabsTrigger>
          <TabsTrigger value="social">Social Media</TabsTrigger>
          <TabsTrigger value="preview">Preview</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-4 mt-4">
          <div className="space-y-2">
            <Label>Page Title</Label>
            <Input 
              value={metaTags.title} 
              onChange={(e) => setMetaTags({ ...metaTags, title: e.target.value })}
              maxLength={60}
            />
            <p className="text-xs text-muted-foreground">{metaTags.title.length}/60 characters</p>
          </div>

          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea 
              value={metaTags.description} 
              onChange={(e) => setMetaTags({ ...metaTags, description: e.target.value })}
              maxLength={160}
            />
            <p className="text-xs text-muted-foreground">{metaTags.description.length}/160 characters</p>
          </div>

          <div className="space-y-2">
            <Label>Keywords (comma separated)</Label>
            <Input 
              value={metaTags.keywords.join(', ')} 
              onChange={(e) => setMetaTags({ ...metaTags, keywords: e.target.value.split(',').map(k => k.trim()) })}
            />
          </div>
        </TabsContent>

        <TabsContent value="social" className="space-y-4 mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Open Graph (Facebook/LinkedIn)</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>OG Title</Label>
                  <Input 
                    value={metaTags.og_title || metaTags.title} 
                    onChange={(e) => setMetaTags({ ...metaTags, og_title: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>OG Description</Label>
                  <Textarea 
                    value={metaTags.og_description || metaTags.description} 
                    onChange={(e) => setMetaTags({ ...metaTags, og_description: e.target.value })}
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Twitter Card</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Twitter Title</Label>
                  <Input 
                    value={metaTags.twitter_title || metaTags.title} 
                    onChange={(e) => setMetaTags({ ...metaTags, twitter_title: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Twitter Description</Label>
                  <Textarea 
                    value={metaTags.twitter_description || metaTags.description} 
                    onChange={(e) => setMetaTags({ ...metaTags, twitter_description: e.target.value })}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="preview" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Google Search Result Preview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-sans max-w-[600px]">
                <div className="text-sm text-[#202124] mb-1 flex items-center gap-2">
                  <div className="w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center text-xs">Fav</div>
                  <div className="flex flex-col">
                    <span className="text-[#202124]">{siteName}</span>
                    <span className="text-[#5f6368] text-xs">https://www.example.com</span>
                  </div>
                </div>
                <div className="text-xl text-[#1a0dab] hover:underline cursor-pointer mb-1 truncate">
                  {metaTags.title || "Page Title"}
                </div>
                <div className="text-sm text-[#4d5156] line-clamp-2">
                  {metaTags.description || "Page description will appear here..."}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
