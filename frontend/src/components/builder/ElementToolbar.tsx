import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import {
  Type,
  Palette,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Trash2,
  X,
  Edit3,
  Check,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { StyleEdit } from './WYSIWYGEditor';

export interface ElementToolbarProps {
  element: HTMLElement;
  rect: DOMRect;
  isEditing: boolean;
  onTextEdit: (content: string) => void;
  onStyleEdit: (styles: StyleEdit) => void;
  onDelete: () => void;
  onClose: () => void;
  onEditModeChange: (isEditing: boolean) => void;
  className?: string;
}

export const ElementToolbar: React.FC<ElementToolbarProps> = ({
  element,
  rect,
  isEditing,
  onTextEdit,
  onStyleEdit,
  onDelete,
  onClose,
  onEditModeChange,
  className,
}) => {
  const [editContent, setEditContent] = useState('');
  const [color, setColor] = useState('#000000');
  const [fontSize, setFontSize] = useState('16');
  const [textAlign, setTextAlign] = useState<'left' | 'center' | 'right'>('left');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Initialize values from element
  useEffect(() => {
    const computedStyles = window.getComputedStyle(element);
    setEditContent(element.textContent || '');
    
    const colorValue = computedStyles.getPropertyValue('color');
    setColor(rgbToHex(colorValue || '#000000'));
    
    const fontSizeValue = computedStyles.getPropertyValue('font-size');
    setFontSize(fontSizeValue ? parseInt(fontSizeValue).toString() : '16');
    
    const textAlignValue = computedStyles.getPropertyValue('text-align') || 'left';
    setTextAlign(textAlignValue as 'left' | 'center' | 'right');
  }, [element]);

  // Focus textarea when entering edit mode
  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.select();
    }
  }, [isEditing]);

  // Convert RGB to Hex
  const rgbToHex = (rgb: string | undefined): string => {
    if (!rgb) return '#000000';
    const match = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
    if (!match || !match[1] || !match[2] || !match[3]) return '#000000';

    const r = parseInt(match[1]);
    const g = parseInt(match[2]);
    const b = parseInt(match[3]);

    return '#' + [r, g, b].map(x => {
      const hex = x.toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('');
  };

  // Handle text edit start
  const handleEditStart = () => {
    setEditContent(element.textContent || '');
    onEditModeChange(true);
  };

  // Handle text edit save
  const handleEditSave = () => {
    onTextEdit(editContent);
    onEditModeChange(false);
  };

  // Handle text edit cancel
  const handleEditCancel = () => {
    setEditContent(element.textContent || '');
    onEditModeChange(false);
  };

  // Handle color change
  const handleColorChange = (newColor: string) => {
    setColor(newColor);
    onStyleEdit({ color: newColor });
  };

  // Handle font size change
  const handleFontSizeChange = (newSize: string) => {
    setFontSize(newSize);
    onStyleEdit({ fontSize: `${newSize}px` });
  };

  // Handle text align change
  const handleTextAlignChange = (align: 'left' | 'center' | 'right') => {
    setTextAlign(align);
    onStyleEdit({ textAlign: align });
  };

  // Handle delete with confirmation
  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this element?')) {
      onDelete();
    }
  };

  // Calculate toolbar position (above element)
  const toolbarStyle: React.CSSProperties = {
    position: 'fixed',
    top: `${rect.top - 50}px`,
    left: `${rect.left}px`,
    zIndex: 1000,
  };

  return (
    <>
      {/* Highlight overlay */}
      <div
        className="fixed border-2 border-primary pointer-events-none"
        style={{
          top: `${rect.top}px`,
          left: `${rect.left}px`,
          width: `${rect.width}px`,
          height: `${rect.height}px`,
          zIndex: 999,
        }}
      />

      {/* Toolbar */}
      <div
        className={cn(
          'flex items-center gap-1 p-2 bg-background border rounded-lg shadow-lg',
          className
        )}
        style={toolbarStyle}
      >
        {!isEditing ? (
          <>
            {/* Edit Text Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleEditStart}
              title="Edit text"
            >
              <Edit3 className="h-4 w-4" />
            </Button>

            <Separator orientation="vertical" className="h-6" />

            {/* Color Picker */}
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="ghost" size="sm" title="Text color">
                  <Palette className="h-4 w-4" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-64">
                <div className="space-y-2">
                  <Label>Text Color</Label>
                  <div className="flex items-center gap-2">
                    <Input
                      type="color"
                      value={color}
                      onChange={(e) => handleColorChange(e.target.value)}
                      className="w-16 h-10"
                    />
                    <Input
                      type="text"
                      value={color}
                      onChange={(e) => handleColorChange(e.target.value)}
                      className="flex-1"
                    />
                  </div>
                </div>
              </PopoverContent>
            </Popover>

            {/* Font Size */}
            <Popover>
              <PopoverTrigger asChild>
                <Button variant="ghost" size="sm" title="Font size">
                  <Type className="h-4 w-4" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-48">
                <div className="space-y-2">
                  <Label>Font Size</Label>
                  <Select value={fontSize} onValueChange={handleFontSizeChange}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="12">12px</SelectItem>
                      <SelectItem value="14">14px</SelectItem>
                      <SelectItem value="16">16px</SelectItem>
                      <SelectItem value="18">18px</SelectItem>
                      <SelectItem value="20">20px</SelectItem>
                      <SelectItem value="24">24px</SelectItem>
                      <SelectItem value="32">32px</SelectItem>
                      <SelectItem value="48">48px</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </PopoverContent>
            </Popover>

            {/* Text Alignment */}
            <div className="flex items-center">
              <Button
                variant={textAlign === 'left' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => handleTextAlignChange('left')}
                title="Align left"
              >
                <AlignLeft className="h-4 w-4" />
              </Button>
              <Button
                variant={textAlign === 'center' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => handleTextAlignChange('center')}
                title="Align center"
              >
                <AlignCenter className="h-4 w-4" />
              </Button>
              <Button
                variant={textAlign === 'right' ? 'secondary' : 'ghost'}
                size="sm"
                onClick={() => handleTextAlignChange('right')}
                title="Align right"
              >
                <AlignRight className="h-4 w-4" />
              </Button>
            </div>

            <Separator orientation="vertical" className="h-6" />

            {/* Delete Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDelete}
              title="Delete element"
              className="text-destructive hover:text-destructive"
            >
              <Trash2 className="h-4 w-4" />
            </Button>

            {/* Close Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              title="Close"
            >
              <X className="h-4 w-4" />
            </Button>
          </>
        ) : (
          <>
            {/* Edit Mode */}
            <div className="flex items-center gap-2">
              <Textarea
                ref={textareaRef}
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="min-w-[300px] max-w-[500px]"
                rows={3}
              />
              <Button
                variant="default"
                size="sm"
                onClick={handleEditSave}
                title="Save"
              >
                <Check className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleEditCancel}
                title="Cancel"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </>
        )}
      </div>
    </>
  );
};
