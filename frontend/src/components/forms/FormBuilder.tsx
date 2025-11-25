import { useState } from 'react';
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from '@dnd-kit/core';
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { GripVertical, Trash2, Plus } from 'lucide-react';

interface FormField {
  id: string;
  type: 'text' | 'email' | 'textarea' | 'checkbox' | 'select';
  label: string;
  placeholder?: string;
  required: boolean;
  options?: string[];
}

interface SortableFieldProps {
  field: FormField;
  onRemove: (id: string) => void;
  onUpdate: (id: string, updates: Partial<FormField>) => void;
}

function SortableField({ field, onRemove, onUpdate }: SortableFieldProps) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: field.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} className="flex items-start gap-4 p-4 bg-card border rounded-lg mb-2">
      <div {...attributes} {...listeners} className="mt-2 cursor-move text-muted-foreground hover:text-foreground">
        <GripVertical className="h-5 w-5" />
      </div>
      
      <div className="flex-1 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Label</Label>
            <Input 
              value={field.label} 
              onChange={(e) => onUpdate(field.id, { label: e.target.value })} 
            />
          </div>
          <div className="space-y-2">
            <Label>Type</Label>
            <select 
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              value={field.type}
              onChange={(e) => onUpdate(field.id, { type: e.target.value as any })}
            >
              <option value="text">Text Input</option>
              <option value="email">Email</option>
              <option value="textarea">Text Area</option>
              <option value="checkbox">Checkbox</option>
              <option value="select">Dropdown</option>
            </select>
          </div>
        </div>

        {field.type !== 'checkbox' && (
          <div className="space-y-2">
            <Label>Placeholder</Label>
            <Input 
              value={field.placeholder || ''} 
              onChange={(e) => onUpdate(field.id, { placeholder: e.target.value })} 
            />
          </div>
        )}

        <div className="flex items-center space-x-2">
          <Switch 
            checked={field.required}
            onCheckedChange={(checked) => onUpdate(field.id, { required: checked })}
          />
          <Label>Required</Label>
        </div>
      </div>

      <Button variant="ghost" size="icon" onClick={() => onRemove(field.id)} className="text-destructive hover:text-destructive/90">
        <Trash2 className="h-5 w-5" />
      </Button>
    </div>
  );
}

export function FormBuilder() {
  const [fields, setFields] = useState<FormField[]>([
    { id: '1', type: 'text', label: 'Name', placeholder: 'Your name', required: true },
    { id: '2', type: 'email', label: 'Email', placeholder: 'your@email.com', required: true },
    { id: '3', type: 'textarea', label: 'Message', placeholder: 'How can we help?', required: true },
  ]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setFields((items) => {
        const oldIndex = items.findIndex((i) => i.id === active.id);
        const newIndex = items.findIndex((i) => i.id === over.id);
        return arrayMove(items, oldIndex, newIndex);
      });
    }
  };

  const addField = () => {
    const newField: FormField = {
      id: Math.random().toString(36).substr(2, 9),
      type: 'text',
      label: 'New Field',
      required: false,
    };
    setFields([...fields, newField]);
  };

  const removeField = (id: string) => {
    setFields(fields.filter((f) => f.id !== id));
  };

  const updateField = (id: string, updates: Partial<FormField>) => {
    setFields(fields.map((f) => (f.id === id ? { ...f, ...updates } : f)));
  };

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Form Builder</h2>
        <Button onClick={addField}>
          <Plus className="h-4 w-4 mr-2" />
          Add Field
        </Button>
      </div>

      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={fields.map(f => f.id)} strategy={verticalListSortingStrategy}>
          <div className="space-y-4">
            {fields.map((field) => (
              <SortableField 
                key={field.id} 
                field={field} 
                onRemove={removeField} 
                onUpdate={updateField} 
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>

      {fields.length === 0 && (
        <div className="text-center py-12 border-2 border-dashed rounded-lg text-muted-foreground">
          No fields yet. Click "Add Field" to start building your form.
        </div>
      )}
    </div>
  );
}
