import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface FormField {
  id: string;
  type: 'text' | 'email' | 'textarea' | 'checkbox' | 'select';
  label: string;
  placeholder?: string;
  required: boolean;
  options?: string[];
}

interface FormPreviewProps {
  fields: FormField[];
  onSubmit?: (data: any) => void;
}

export function FormPreview({ fields, onSubmit }: FormPreviewProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Collect data and call onSubmit
    if (onSubmit) onSubmit({});
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-md mx-auto p-6 border rounded-lg bg-card shadow-sm">
      {fields.map((field) => (
        <div key={field.id} className="space-y-2">
          {field.type !== 'checkbox' && (
            <Label>
              {field.label}
              {field.required && <span className="text-destructive ml-1">*</span>}
            </Label>
          )}

          {field.type === 'text' && (
            <Input placeholder={field.placeholder} required={field.required} />
          )}

          {field.type === 'email' && (
            <Input type="email" placeholder={field.placeholder} required={field.required} />
          )}

          {field.type === 'textarea' && (
            <Textarea placeholder={field.placeholder} required={field.required} />
          )}

          {field.type === 'select' && (
            <Select>
              <SelectTrigger>
                <SelectValue placeholder={field.placeholder || "Select an option"} />
              </SelectTrigger>
              <SelectContent>
                {field.options?.map((opt) => (
                  <SelectItem key={opt} value={opt}>{opt}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}

          {field.type === 'checkbox' && (
            <div className="flex items-center space-x-2">
              <Checkbox id={field.id} required={field.required} />
              <Label htmlFor={field.id} className="font-normal">
                {field.label}
                {field.required && <span className="text-destructive ml-1">*</span>}
              </Label>
            </div>
          )}
        </div>
      ))}

      <Button type="submit" className="w-full">Submit</Button>
    </form>
  );
}
