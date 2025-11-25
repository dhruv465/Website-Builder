# Dynamic Package Research System

## Overview

The Smart Website Builder now features a **dynamic package research system** that can learn about ANY npm package the user mentions, not just pre-configured ones. This eliminates the hardcoded limitation and makes the system truly flexible.

## The Problem We Solved

### ❌ Before (Hardcoded Approach)

```python
# Only 8 pre-configured libraries
supported_libraries = ["shadcn", "antd", "mui", "chakra", "mantine", "vuetify", "primevue", "daisyui"]

# User asks for something else
User: "Use Framer Motion for animations"
Agent: "Sorry, I don't know that library" ❌
```

### ✅ After (Dynamic Research)

```python
# ANY package can be researched
User: "Use Framer Motion for animations"
Agent: *researches Framer Motion using LLM*
Agent: *learns installation, usage, best practices*
Agent: *generates code with Framer Motion* ✅
```

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER REQUEST                              │
│  "Create a portfolio in React with Framer Motion"           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              CODE GENERATION AGENT                           │
│                                                              │
│  1. Checks if "framer-motion" is in registry                │
│     → Not found                                              │
│                                                              │
│  2. Calls Package Research Agent                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           PACKAGE RESEARCH AGENT                             │
│                                                              │
│  1. Builds research prompt:                                 │
│     "Research npm package 'framer-motion' for React"        │
│                                                              │
│  2. Calls Gemini LLM with structured prompt                 │
│                                                              │
│  3. LLM researches and returns:                             │
│     ✓ Package name: framer-motion                           │
│     ✓ Version: 10.16.0                                      │
│     ✓ Installation: npm install framer-motion              │
│     ✓ Import examples:                                      │
│       - import { motion } from 'framer-motion'              │
│       - import { AnimatePresence } from 'framer-motion'     │
│     ✓ Usage examples:                                       │
│       - <motion.div animate={{ x: 100 }} />                 │
│       - <motion.button whileHover={{ scale: 1.1 }} />       │
│     ✓ Best practices:                                       │
│       - Use motion components for animations                │
│       - Optimize with layoutId for shared layouts           │
│     ✓ Configuration: Not required                           │
│                                                              │
│  4. Returns structured PackageInfo                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              CODE GENERATION AGENT                           │
│                                                              │
│  1. Receives package info                                   │
│  2. Adds to package.json:                                   │
│     "framer-motion": "10.16.0"                              │
│  3. Enhances prompt with usage examples                     │
│  4. Generates code using Framer Motion                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  GENERATED CODE                              │
│                                                              │
│  package.json:                                              │
│  {                                                           │
│    "dependencies": {                                         │
│      "react": "^18.2.0",                                     │
│      "framer-motion": "10.16.0"  ← Dynamically added        │
│    }                                                         │
│  }                                                           │
│                                                              │
│  src/App.jsx:                                               │
│  import { motion } from 'framer-motion'                     │
│                                                              │
│  function App() {                                            │
│    return (                                                  │
│      <motion.div                                            │
│        initial={{ opacity: 0 }}                             │
│        animate={{ opacity: 1 }}                             │
│        transition={{ duration: 0.5 }}                       │
│      >                                                       │
│        <h1>Welcome</h1>                                      │
│      </motion.div>                                           │
│    )                                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
```

## Real-World Examples

### Example 1: Framer Motion (Animation Library)

**User Request:**
```
"Create a portfolio in React with Framer Motion for smooth animations"
```

**What Happens:**

1. **Research Phase:**
```python
# Package Research Agent researches "framer-motion"
PackageInfo(
    package_name="framer-motion",
    version="10.16.0",
    description="Production-ready motion library for React",
    installation_command="npm install framer-motion",
    import_examples=[
        "import { motion } from 'framer-motion'",
        "import { AnimatePresence } from 'framer-motion'",
        "import { useAnimation } from 'framer-motion'"
    ],
    usage_examples=[
        "<motion.div animate={{ x: 100 }} />",
        "<motion.button whileHover={{ scale: 1.1 }} />",
        "<AnimatePresence><motion.div exit={{ opacity: 0 }} /></AnimatePresence>"
    ],
    best_practices=[
        "Use motion components for all animated elements",
        "Leverage variants for complex animations",
        "Use layoutId for shared element transitions"
    ]
)
```

2. **Generated Code:**
```jsx
// package.json
{
  "dependencies": {
    "react": "^18.2.0",
    "framer-motion": "10.16.0"
  }
}

// src/App.jsx
import { motion, AnimatePresence } from 'framer-motion'

function App() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="min-h-screen"
    >
      <motion.h1
        initial={{ scale: 0.8 }}
        animate={{ scale: 1 }}
        transition={{ type: "spring", stiffness: 100 }}
      >
        My Portfolio
      </motion.h1>
      
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        Contact Me
      </motion.button>
    </motion.div>
  )
}
```

### Example 2: React Spring (Alternative Animation)

**User Request:**
```
"Build a landing page with React Spring animations"
```

**Research Result:**
```python
PackageInfo(
    package_name="@react-spring/web",
    version="9.7.3",
    installation_command="npm install @react-spring/web",
    import_examples=[
        "import { useSpring, animated } from '@react-spring/web'",
        "import { useTrail } from '@react-spring/web'"
    ],
    usage_examples=[
        "const springs = useSpring({ from: { opacity: 0 }, to: { opacity: 1 } })",
        "<animated.div style={springs}>Content</animated.div>"
    ]
)
```

### Example 3: Headless UI (Unstyled Components)

**User Request:**
```
"Create a dashboard with Headless UI components"
```

**Research Result:**
```python
PackageInfo(
    package_name="@headlessui/react",
    version="1.7.17",
    installation_command="npm install @headlessui/react",
    peer_dependencies=["react", "react-dom"],
    import_examples=[
        "import { Dialog, Transition } from '@headlessui/react'",
        "import { Menu } from '@headlessui/react'",
        "import { Listbox } from '@headlessui/react'"
    ],
    usage_examples=[
        "<Dialog open={isOpen} onClose={closeModal}>...</Dialog>",
        "<Menu><Menu.Button>Options</Menu.Button><Menu.Items>...</Menu.Items></Menu>"
    ],
    configuration_required=False
)
```

### Example 4: React Query (Data Fetching)

**User Request:**
```
"Build a blog with React Query for data fetching"
```

**Research Result:**
```python
PackageInfo(
    package_name="@tanstack/react-query",
    version="5.14.0",
    installation_command="npm install @tanstack/react-query",
    import_examples=[
        "import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'"
    ],
    usage_examples=[
        "const { data, isLoading } = useQuery({ queryKey: ['posts'], queryFn: fetchPosts })"
    ],
    configuration_required=True,
    configuration_steps=[
        "Wrap app with QueryClientProvider",
        "Create QueryClient instance"
    ]
)
```

### Example 5: Unknown/Invalid Package

**User Request:**
```
"Use xyz-fake-library-123 for styling"
```

**Research Result:**
```python
PackageInfo(
    package_name="xyz-fake-library-123",
    description="Package 'xyz-fake-library-123' not found in npm registry",
    compatible_with_framework=False,
    warnings=["Package may not exist or is not well-documented"]
)

# Agent falls back to Tailwind CSS
```

## Benefits

### 1. **Unlimited Flexibility**
- Works with ANY npm package
- Not limited to pre-configured libraries
- Adapts to new packages automatically

### 2. **Always Up-to-Date**
- LLM has knowledge of latest packages
- No need to manually update registry
- Learns about new libraries as they're released

### 3. **Intelligent Integration**
- Understands package requirements
- Knows peer dependencies
- Follows best practices
- Avoids common pitfalls

### 4. **Graceful Fallbacks**
- If package doesn't exist, falls back to Tailwind
- Warns user about compatibility issues
- Suggests alternatives

### 5. **Zero Configuration**
- User just mentions the package name
- System handles everything automatically
- No manual setup required

## API Usage

### Python API

```python
from agents.code_generation_agent import CodeGenerationAgent, CodeGenerationInput

agent = CodeGenerationAgent()

# User can specify ANY package
input_data = CodeGenerationInput(
    requirements={
        "site_type": "portfolio",
        "pages": ["home", "about"],
    },
    framework="react",
    ui_library="framer-motion"  # ← Can be ANY package!
)

output = await agent.execute(input_data, context)

# System automatically:
# 1. Researches "framer-motion"
# 2. Learns how to use it
# 3. Adds to package.json
# 4. Generates code with it
```

### Natural Language

Users can just mention packages naturally:

```
✅ "Create a site with Framer Motion"
✅ "Use React Spring for animations"
✅ "Build with Headless UI components"
✅ "Add React Query for data fetching"
✅ "Use Zustand for state management"
✅ "Include React Hook Form for forms"
```

## Comparison: Hardcoded vs Dynamic

| Feature | Hardcoded | Dynamic Research |
|---------|-----------|------------------|
| Supported packages | 8 libraries | ∞ (unlimited) |
| New packages | Manual update needed | Automatic |
| Custom packages | Not possible | Fully supported |
| Maintenance | High (constant updates) | Low (self-learning) |
| Flexibility | Limited | Unlimited |
| User experience | Restrictive | Empowering |

## Technical Implementation

### Package Research Agent

```python
class PackageResearchAgent:
    async def execute(self, input_data, context):
        # 1. Build research prompt
        prompt = self._build_research_prompt(
            package_name="framer-motion",
            framework="react"
        )
        
        # 2. Call LLM
        response = await gemini.generate_text(prompt)
        
        # 3. Parse structured response
        package_info = self._parse_research_response(response)
        
        # 4. Return package information
        return PackageResearchOutput(
            package_info=package_info,
            can_be_used=True
        )
```

### Integration with Code Generation

```python
class CodeGenerationAgent:
    async def _generate_react_code(self, requirements, context, ui_library):
        # 1. Research package dynamically
        ui_lib_info = await self._research_and_get_ui_library_info(
            ui_library="framer-motion",
            framework="react",
            context=context
        )
        
        # 2. Add packages to package.json
        npm_packages = ui_lib_info["npm_packages"]
        # {"framer-motion": "10.16.0"}
        
        # 3. Enhance prompt with usage examples
        prompt_addition = ui_lib_info["prompt_addition"]
        
        # 4. Generate code
        code = await self.gemini.generate_text(enhanced_prompt)
```

## Future Enhancements

1. **Package Caching**: Cache researched packages to avoid repeated LLM calls
2. **Version Management**: Automatically select compatible versions
3. **Conflict Detection**: Detect package conflicts before generation
4. **Bundle Size Optimization**: Warn about large packages
5. **Security Scanning**: Check for known vulnerabilities
6. **Alternative Suggestions**: Suggest lighter alternatives

## Conclusion

The dynamic package research system transforms the Smart Website Builder from a **limited, hardcoded tool** into a **flexible, intelligent system** that can work with ANY npm package. Users are no longer restricted to pre-configured libraries—they can use whatever tools they prefer, and the system will learn and adapt automatically.

This is a **game-changer** for user experience and system capabilities! 🚀
