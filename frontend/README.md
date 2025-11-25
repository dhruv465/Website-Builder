# Website Builder Frontend

Modern, production-ready website builder frontend built with React, TypeScript, Vite, ShadCN UI, and Framer Motion.

## Tech Stack

- **Framework**: React 18
- **Build Tool**: Vite 5
- **Language**: TypeScript 5 (strict mode)
- **Routing**: React Router v6
- **UI Library**: ShadCN UI (Radix UI + Tailwind CSS)
- **Animation**: Framer Motion 11
- **State Management**: Zustand
- **Form Handling**: React Hook Form + Zod
- **HTTP Client**: Axios
- **Testing**: Vitest + React Testing Library + Playwright

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

### Testing

```bash
# Run unit tests
npm test

# Run tests in watch mode
npm run test:watch

# Run E2E tests
npm run test:e2e
```

### Linting and Formatting

```bash
# Run ESLint
npm run lint

# Format code with Prettier
npm run format
```

## Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # Application entry point
│   ├── App.tsx               # Root component
│   ├── index.css             # Global styles
│   ├── vite-env.d.ts         # Vite type definitions
│   ├── pages/                # Page components
│   ├── layouts/              # Layout components
│   ├── components/           # React components
│   │   ├── ui/               # ShadCN UI components
│   │   └── ...
│   ├── lib/                  # Utility libraries
│   │   ├── api/              # API client
│   │   ├── hooks/            # Custom hooks
│   │   ├── context/          # React Context
│   │   ├── store/            # Zustand stores
│   │   ├── utils/            # Utility functions
│   │   └── types/            # TypeScript types
│   └── test/                 # Test utilities
├── e2e/                      # E2E tests
├── public/                   # Static assets
├── index.html                # HTML entry point
├── vite.config.ts            # Vite configuration
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=true
VITE_ENV=development
```

## Features

- ✅ React 18 with TypeScript
- ✅ Vite for fast development and optimized builds
- ✅ Tailwind CSS with custom theme
- ✅ ShadCN UI components
- ✅ Framer Motion animations
- ✅ React Router v6 for routing
- ✅ Zustand for state management
- ✅ React Hook Form + Zod for forms
- ✅ Axios for API calls
- ✅ ESLint + Prettier for code quality
- ✅ Vitest + React Testing Library for unit tests
- ✅ Playwright for E2E tests
- ✅ Path aliases (@/* imports)
- ✅ API proxy configuration
- ✅ Dark mode support

## Component Documentation

### Builder Components

#### BuilderForm
Multi-tab input interface for website requirements.

```tsx
import { BuilderForm } from '@/components/builder';

<BuilderForm
  onSubmit={handleSubmit}
  initialData={{ requirements: 'Create a blog' }}
  isLoading={false}
/>
```

**Features:**
- Text, chat, and voice input modes
- Framework and design style selection
- Form validation with Zod
- Auto-save to localStorage

#### SitePreview
Live preview of generated website with editing capabilities.

```tsx
import { SitePreview } from '@/components/builder';

<SitePreview
  htmlCode={html}
  cssCode={css}
  jsCode={js}
  viewport="desktop"
  editable={true}
  onElementSelect={handleElementSelect}
/>
```

### Audit Components

#### AuditConsole
Comprehensive audit results display.

```tsx
import { AuditConsole } from '@/components/audit';

<AuditConsole
  auditResult={result}
  previousAudits={history}
  onRerun={handleRerun}
  onExport={handleExport}
/>
```

### Theme Components

#### ThemeSelector
Browse and apply design themes.

```tsx
import { ThemeSelector } from '@/components/theme';

<ThemeSelector
  themes={themes}
  selectedTheme={currentTheme}
  onThemeSelect={handleSelect}
  onThemeCustomize={handleCustomize}
/>
```

### Workflow Components

#### AgentActivityPanel
Real-time agent workflow progress.

```tsx
import { AgentActivityPanel } from '@/components/workflow';

<AgentActivityPanel
  workflowId={workflowId}
  onCancel={handleCancel}
/>
```

## API Integration

### Using the API Client

```typescript
import { api } from '@/lib/api';

// Create session
const session = await api.sessions.create();

// Start workflow
const workflow = await api.workflows.create({
  session_id: session.id,
  requirements: 'Create a portfolio',
  framework: 'react',
});

// Get site code
const code = await api.code.get(siteId);

// Run audit
const audit = await api.audit.run(siteId);

// Deploy
const deployment = await api.deploy.vercel(siteId, {
  project_name: 'my-site',
});
```

### WebSocket Integration

```typescript
import { useWebSocket } from '@/lib/hooks';

function WorkflowMonitor({ workflowId }) {
  const { status, logs, isConnected } = useWebSocket(workflowId);
  
  return (
    <div>
      <p>Status: {status}</p>
      <p>Connected: {isConnected ? 'Yes' : 'No'}</p>
      <ul>
        {logs.map(log => (
          <li key={log.timestamp}>{log.message}</li>
        ))}
      </ul>
    </div>
  );
}
```

## Custom Hooks

### useSession
Manage user session state.

```typescript
import { useSession } from '@/lib/hooks';

function MyComponent() {
  const { session, createSession, updatePreferences } = useSession();
  
  return <div>Session ID: {session?.id}</div>;
}
```

### useWorkflow
Monitor workflow execution.

```typescript
import { useWorkflow } from '@/lib/hooks';

function WorkflowStatus({ workflowId }) {
  const { status, progress, cancel } = useWorkflow(workflowId);
  
  return (
    <div>
      <p>Progress: {progress}%</p>
      <button onClick={cancel}>Cancel</button>
    </div>
  );
}
```

## Styling Guidelines

### Tailwind CSS

Use Tailwind utility classes for styling:

```tsx
// Good: Tailwind utilities
<div className="flex flex-col gap-4 p-6 bg-white dark:bg-gray-900 rounded-lg shadow-md">
  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Title</h2>
  <p className="text-gray-600 dark:text-gray-300">Description</p>
</div>

// Avoid: Inline styles
<div style={{ display: 'flex', padding: '24px' }}>
  <h2 style={{ fontSize: '24px' }}>Title</h2>
</div>
```

### Responsive Design

Use responsive modifiers:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {/* Content */}
</div>
```

### Dark Mode

Support dark mode with `dark:` prefix:

```tsx
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  {/* Content */}
</div>
```

## Testing

### Unit Tests

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { BuilderForm } from './BuilderForm';

describe('BuilderForm', () => {
  it('should submit form with valid data', async () => {
    const onSubmit = vi.fn();
    render(<BuilderForm onSubmit={onSubmit} />);
    
    const input = screen.getByLabelText(/requirements/i);
    fireEvent.change(input, { target: { value: 'Create a blog' } });
    
    const submitButton = screen.getByRole('button', { name: /submit/i });
    fireEvent.click(submitButton);
    
    expect(onSubmit).toHaveBeenCalledWith({
      requirements: 'Create a blog'
    });
  });
});
```

### E2E Tests

```typescript
import { test, expect } from '@playwright/test';

test('create website workflow', async ({ page }) => {
  await page.goto('/');
  
  await page.getByRole('button', { name: /create website/i }).click();
  await page.getByLabel(/requirements/i).fill('Create a portfolio');
  await page.getByRole('button', { name: /generate/i }).click();
  
  await expect(page.getByText(/generating/i)).toBeVisible();
  await expect(page.getByRole('heading', { name: /preview/i })).toBeVisible({ timeout: 30000 });
});
```

## Deployment

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Deploy to Netlify

```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod
```

## Troubleshooting

See [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) for common issues and solutions.

## Additional Documentation

- [API Integration Guide](../docs/API_INTEGRATION.md)
- [Accessibility Guide](../docs/ACCESSIBILITY_GUIDE.md)
- [Performance Guide](../docs/PERFORMANCE_GUIDE.md)
- [Deployment Guide](../docs/DEPLOYMENT_GUIDE.md)
- [Contributing Guidelines](../CONTRIBUTING.md)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed contribution guidelines.

## License

MIT
