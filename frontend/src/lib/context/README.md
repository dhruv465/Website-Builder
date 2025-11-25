# Session Context

The SessionContext provides session management functionality for the website builder application.

## Features

- **Automatic Session Creation**: Creates a new session on first visit
- **Session Persistence**: Stores session ID in localStorage for persistence across browser sessions
- **Session Restoration**: Automatically restores session on app load
- **Preferences Management**: Update and persist user preferences
- **Export/Import**: Export session data for backup and import on another device
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Usage

### 1. Wrap your app with SessionProvider

```tsx
import { SessionProvider } from './lib/context';

function App() {
  return (
    <SessionProvider>
      {/* Your app components */}
    </SessionProvider>
  );
}
```

### 2. Use the useSession hook in components

```tsx
import { useSession } from './lib/context';

function MyComponent() {
  const {
    session,
    isLoading,
    error,
    createNewSession,
    loadSession,
    updateSessionData,
    updatePreferences,
    exportSession,
    importSession,
    clearSession,
  } = useSession();

  if (isLoading) {
    return <div>Loading session...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div>
      <h1>Session ID: {session?.id}</h1>
      {/* Your component content */}
    </div>
  );
}
```

## API Reference

### SessionContextValue

#### Properties

- `session: Session | null` - Current session object or null if no session
- `isLoading: boolean` - Loading state for async operations
- `error: Error | null` - Error object if an error occurred

#### Methods

- `createNewSession(): Promise<void>` - Create a new session
- `loadSession(sessionId: string): Promise<void>` - Load an existing session by ID
- `updateSessionData(data: Partial<Session>): Promise<void>` - Update session data
- `updatePreferences(preferences: UserPreferences): Promise<void>` - Update session preferences
- `exportSession(): string` - Export session data as JSON string
- `importSession(data: string): Promise<void>` - Import session data from JSON string
- `clearSession(): void` - Clear current session and remove from localStorage

## Examples

### Update User Preferences

```tsx
const { updatePreferences } = useSession();

const handleUpdatePreferences = async () => {
  try {
    await updatePreferences({
      default_color_scheme: 'dark',
      design_style: 'minimal',
      framework_preference: 'react',
    });
  } catch (error) {
    console.error('Failed to update preferences:', error);
  }
};
```

### Export Session

```tsx
const { exportSession } = useSession();

const handleExport = () => {
  try {
    const data = exportSession();
    // Download as file or copy to clipboard
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'session-backup.json';
    a.click();
  } catch (error) {
    console.error('Failed to export session:', error);
  }
};
```

### Import Session

```tsx
const { importSession } = useSession();

const handleImport = async (file: File) => {
  try {
    const text = await file.text();
    await importSession(text);
  } catch (error) {
    console.error('Failed to import session:', error);
  }
};
```

## Requirements Fulfilled

This implementation fulfills the following requirements:

- **7.1**: Creates new session via Backend API on first visit
- **7.2**: Stores session ID in browser localStorage
- **7.3**: Restores session on app load
- **7.4**: Updates preferences via Backend API
- **7.5**: Provides export/import functionality
