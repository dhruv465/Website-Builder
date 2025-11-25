# UI Library Integration Examples

## Overview

The Smart Website Builder now supports multiple UI libraries across different frameworks. Users can specify which UI library they want to use, and the system will automatically:

1. Include the necessary npm packages in package.json
2. Generate code using that library's components
3. Add required setup/configuration files
4. Provide proper imports and usage examples

## Supported UI Libraries

### React/Next.js
- **Shadcn UI** - Beautifully designed components with Radix UI
- **Ant Design (antd)** - Enterprise-class UI design
- **Material UI (mui)** - Google's Material Design
- **Chakra UI** - Simple, modular components
- **Mantine** - Fully featured component library
- **DaisyUI** - Tailwind CSS components

### Vue
- **Ant Design Vue (antd)** - Ant Design for Vue
- **Vuetify** - Material Design for Vue
- **PrimeVue** - Rich UI components
- **DaisyUI** - Tailwind CSS components

### Svelte
- **DaisyUI** - Tailwind CSS components

## Usage Examples

### Example 1: React with Shadcn UI

**User Request:**
```
"Create a portfolio website in React using Shadcn UI"
```

**What Gets Generated:**

**package.json:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@radix-ui/react-slot": "^1.0.2",
    "@radix-ui/react-dialog": "^1.0.5",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.2.0",
    "lucide-react": "^0.294.0"
  }
}
```

**lib/utils.ts:**
```typescript
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**src/App.jsx:**
```jsx
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardContent } from '@/components/ui/card'

function App() {
  return (
    <div className="min-h-screen p-8">
      <Card>
        <CardHeader>
          <h1 className="text-3xl font-bold">Welcome</h1>
        </CardHeader>
        <CardContent>
          <p>This is a portfolio built with Shadcn UI</p>
          <Button variant="default">Get Started</Button>
        </CardContent>
      </Card>
    </div>
  )
}
```

### Example 2: React with Material UI

**User Request:**
```
"Create a dashboard in React with Material UI"
```

**What Gets Generated:**

**package.json:**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@mui/material": "^5.15.0",
    "@mui/icons-material": "^5.15.0",
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0"
  }
}
```

**src/App.jsx:**
```jsx
import Button from '@mui/material/Button'
import { Card, CardContent } from '@mui/material'
import { AppBar, Toolbar, Typography } from '@mui/material'

function App() {
  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">Dashboard</Typography>
        </Toolbar>
      </AppBar>
      <div style={{ padding: 20 }}>
        <Card>
          <CardContent>
            <Typography variant="h5">Welcome</Typography>
            <Button variant="contained" color="primary">
              Get Started
            </Button>
          </CardContent>
        </Card>
      </div>
    </>
  )
}
```

### Example 3: Vue with Vuetify

**User Request:**
```
"Create a blog in Vue using Vuetify"
```

**What Gets Generated:**

**package.json:**
```json
{
  "dependencies": {
    "vue": "^3.3.11",
    "vuetify": "^3.4.0",
    "@mdi/font": "^7.3.0"
  }
}
```

**src/App.vue:**
```vue
<template>
  <v-app>
    <v-app-bar color="primary">
      <v-toolbar-title>My Blog</v-toolbar-title>
    </v-app-bar>
    
    <v-main>
      <v-container>
        <v-card>
          <v-card-title>Welcome</v-card-title>
          <v-card-text>
            This is a blog built with Vuetify
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary">Read More</v-btn>
          </v-card-actions>
        </v-card>
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
// Component logic
</script>
```

### Example 4: Next.js with Ant Design

**User Request:**
```
"Create an e-commerce site in Next.js with Ant Design"
```

**What Gets Generated:**

**package.json:**
```json
{
  "dependencies": {
    "next": "^14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "antd": "^5.12.0"
  }
}
```

**app/page.js:**
```jsx
import { Button, Card } from 'antd'
import { ShoppingCartOutlined } from '@ant-design/icons'

export default function Home() {
  return (
    <main className="p-8">
      <Card title="Featured Products">
        <p>Browse our amazing products</p>
        <Button type="primary" icon={<ShoppingCartOutlined />}>
          Shop Now
        </Button>
      </Card>
    </main>
  )
}
```

## How It Works

### 1. User Specifies UI Library

The user can specify the UI library in their request:

```python
input_data = CodeGenerationInput(
    requirements={
        "site_type": "portfolio",
        "framework": "react",
        "ui_library": "shadcn"  # ← User specifies UI library
    }
)
```

Or through natural language:
- "Create a portfolio in React using Shadcn UI"
- "Build a dashboard with Material UI"
- "Make a blog in Vue with Vuetify"

### 2. System Validates Compatibility

The system checks if the UI library is compatible with the chosen framework:

```python
library = ui_library_registry.get_library("shadcn")
if "react" in library.supported_frameworks:
    # Proceed with generation
```

### 3. Dependencies Are Added

The system automatically adds the UI library's npm packages to package.json:

```python
ui_lib_packages = ui_library_registry.get_npm_packages("shadcn")
package_json["dependencies"].update(ui_lib_packages)
```

### 4. Setup Files Are Included

If the UI library requires setup files (like Shadcn's utils.ts), they're automatically included:

```python
if ui_lib.setup_files:
    files.update(ui_lib.setup_files)
```

### 5. LLM Generates Appropriate Code

The prompt is enhanced with UI library-specific instructions:

```
**UI Library: Shadcn UI**
Beautifully designed components built with Radix UI and Tailwind CSS

**Import Examples:**
- button: import { Button } from '@/components/ui/button'
- dialog: import { Dialog, DialogContent } from '@/components/ui/dialog'

**Usage Examples:**
- button: <Button variant='default'>Click me</Button>

**IMPORTANT:** Use Shadcn UI components throughout the application.
```

### 6. Deployment Works Automatically

The Deployment Agent:
1. Writes all files (including UI library setup)
2. Runs `npm install` (installs UI library packages)
3. Runs `npm run build` (builds with UI library)
4. Deploys to hosting

## API Usage

### Python API

```python
from agents.code_generation_agent import CodeGenerationAgent, CodeGenerationInput
from agents.base_agent import AgentContext

agent = CodeGenerationAgent()

# Example 1: React with Shadcn UI
input_data = CodeGenerationInput(
    requirements={
        "site_type": "portfolio",
        "pages": ["home", "about", "projects"],
        "key_features": ["dark mode", "animations"],
        "design_style": "Bold Minimalism"
    },
    framework="react",
    ui_library="shadcn"  # ← Specify UI library
)

context = AgentContext(
    session_id="session_123",
    workflow_id="workflow_456"
)

output = await agent.execute(input_data, context)

# Access generated files
files = output.generated_code.additional_files
# files contains: package.json with Shadcn packages, lib/utils.ts, components/ui/button.tsx, etc.
```

### REST API

```bash
POST /api/generate-site
{
  "site_type": "portfolio",
  "framework": "react",
  "ui_library": "shadcn",
  "pages": ["home", "about", "projects"],
  "design_style": "Bold Minimalism"
}
```

## Supported Combinations

| Framework | Shadcn | Ant Design | Material UI | Chakra UI | Mantine | Vuetify | PrimeVue | DaisyUI |
|-----------|--------|------------|-------------|-----------|---------|---------|----------|---------|
| React     | ✅     | ✅         | ✅          | ✅        | ✅      | ❌      | ❌       | ✅      |
| Next.js   | ✅     | ✅         | ✅          | ✅        | ✅      | ❌      | ❌       | ✅      |
| Vue       | ❌     | ✅         | ❌          | ❌        | ❌      | ✅      | ✅       | ✅      |
| Svelte    | ❌     | ❌         | ❌          | ❌        | ❌      | ❌      | ❌       | ✅      |

## Benefits

1. **No Manual Setup**: Users don't need to install or configure UI libraries
2. **Best Practices**: Generated code follows each library's best practices
3. **Consistent Styling**: All components use the same UI library
4. **Type Safety**: TypeScript support where applicable
5. **Accessibility**: UI libraries come with built-in accessibility features
6. **Professional Look**: High-quality, production-ready components

## Future Enhancements

1. **Custom Themes**: Allow users to customize UI library themes
2. **Component Variants**: Support different component variants and styles
3. **More Libraries**: Add support for more UI libraries (Radix UI, Headless UI, etc.)
4. **Hybrid Approach**: Mix UI library components with custom Tailwind styling
5. **Component Playground**: Preview UI library components before generation

## Conclusion

The UI library integration makes the Smart Website Builder even more powerful by allowing users to leverage professional, battle-tested component libraries without any manual setup or configuration. The system handles everything automatically from dependency installation to code generation to deployment.
