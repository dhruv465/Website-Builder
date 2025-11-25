import React from 'react';
import { List } from 'react-window';

interface VirtualListProps<T> {
  items: T[];
  height: number;
  itemHeight: number;
  width?: string | number;
  renderItem: (item: T, index: number) => React.ReactNode;
  className?: string;
  overscanCount?: number;
}

/**
 * Virtual scrolling list component using react-window
 * Renders only visible items for optimal performance with large lists
 * 
 * @param items - Array of items to render
 * @param height - Height of the list container
 * @param itemHeight - Height of each item (can be number or function)
 * @param width - Width of the list (default: 100%)
 * @param renderItem - Function to render each item
 * @param className - Additional CSS classes
 * @param overscanCount - Number of items to render outside visible area
 */
export function VirtualList<T>({
  items,
  height,
  itemHeight,
  renderItem,
  className,
  overscanCount = 3,
}: VirtualListProps<T>) {
  return (
    <List
      className={className}
      defaultHeight={height}
      rowCount={items.length}
      rowHeight={itemHeight}
      overscanCount={overscanCount}
      rowProps={{}}
      rowComponent={({ index, style }) => {
        const item = items[index];
        // Always return a valid React element
        return <div style={style}>{item ? renderItem(item, index) : null}</div>;
      }}
    >
      {null}
    </List>
  );
}
