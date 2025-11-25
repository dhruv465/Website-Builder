import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Download, Github, Loader2 } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface ExportPanelProps {
  htmlCode: string;
  cssCode: string;
  jsCode: string;
}

export function ExportPanel({ htmlCode, cssCode, jsCode }: ExportPanelProps) {
  const [isZipping, setIsZipping] = useState(false);
  const [isPushing, setIsPushing] = useState(false);
  const [repoUrl, setRepoUrl] = useState('');
  const [githubToken, setGithubToken] = useState('');

  const handleDownloadZip = async () => {
    setIsZipping(true);
    try {
      const response = await apiClient.post('/api/export/zip', {
        html_code: htmlCode,
        css_code: cssCode,
        js_code: jsCode,
      }, {
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'website-export.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("Website downloaded successfully!");
    } catch (error) {
      console.error('Error downloading ZIP:', error);
      toast.error("Failed to download ZIP.");
    } finally {
      setIsZipping(false);
    }
  };

  const handleGithubExport = async () => {
    if (!repoUrl || !githubToken) {
      toast.error("Please provide Repository URL and Token");
      return;
    }

    setIsPushing(true);
    try {
      await apiClient.post('/api/export/github', {
        repo_url: repoUrl,
        token: githubToken,
        html_code: htmlCode,
        css_code: cssCode,
        js_code: jsCode,
      });
      toast.success("Successfully exported to GitHub!");
    } catch (error) {
      console.error('Error exporting to GitHub:', error);
      toast.error("Failed to export to GitHub.");
    } finally {
      setIsPushing(false);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="h-5 w-5" />
            Download ZIP
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Download your entire website including HTML, CSS, and JavaScript files in a ZIP archive.
          </p>
          <Button onClick={handleDownloadZip} disabled={isZipping} className="w-full">
            {isZipping ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Download className="mr-2 h-4 w-4" />}
            Download Source Code
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Github className="h-5 w-5" />
            Export to GitHub
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Repository URL</Label>
            <Input 
              placeholder="https://github.com/username/repo.git" 
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label>Personal Access Token</Label>
            <Input 
              type="password" 
              placeholder="ghp_..." 
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
            />
          </div>
          <Button onClick={handleGithubExport} disabled={isPushing} variant="secondary" className="w-full">
            {isPushing ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Github className="mr-2 h-4 w-4" />}
            Push to Repository
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
