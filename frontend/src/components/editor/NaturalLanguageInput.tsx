import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Sparkles, Loader2, Send } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

interface NaturalLanguageInputProps {
  onApplyEdit: (html: string, css: string) => void;
  htmlCode: string;
  cssCode: string;
  selectedElement?: string;
}

export function NaturalLanguageInput({ onApplyEdit, htmlCode, cssCode, selectedElement }: NaturalLanguageInputProps) {
  const [prompt, setPrompt] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsProcessing(true);
    try {
      // 1. Parse Command
      const parseResponse = await apiClient.post('/api/edit/parse', {
        prompt,
        context: {
          html_code: htmlCode,
          css_code: cssCode,
          selected_element: selectedElement
        }
      });

      const command = parseResponse.data;

      // 2. Apply Edit
      const applyResponse = await apiClient.post('/api/edit/apply', {
        command,
        context: {
          html_code: htmlCode,
          css_code: cssCode,
          selected_element: selectedElement
        }
      });

      const result = applyResponse.data;

      if (result.success) {
        onApplyEdit(result.html_code, result.css_code);
        toast.success(result.message);
        setPrompt('');
      } else {
        toast.error(result.message);
      }

    } catch (error) {
      console.error('Error applying edit:', error);
      toast.error("Failed to process your request.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative flex items-center">
        <Sparkles className="absolute left-3 h-4 w-4 text-purple-500" />
        <Input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe your change (e.g., 'Make the header blue')..."
          className="pl-9 pr-12 py-6 bg-background/50 backdrop-blur-sm border-purple-200 focus-visible:ring-purple-500"
          disabled={isProcessing}
        />
        <Button
          type="submit"
          size="sm"
          className="absolute right-1.5 h-8 w-8 p-0 bg-purple-600 hover:bg-purple-700"
          disabled={!prompt.trim() || isProcessing}
        >
          {isProcessing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>
    </form>
  );
}
