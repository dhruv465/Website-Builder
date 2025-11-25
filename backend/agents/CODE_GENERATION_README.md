# Code Generation Agent Implementation

## Overview

The Code Generation Agent is responsible for generating complete, production-ready HTML/CSS/JS code from structured requirements. It supports both template-based and LLM-based generation, code modifications, and comprehensive validation.

## Components

### 1. Code Generation Agent (`code_generation_agent.py`)

**Key Features:**
- Generates new HTML code from requirements
- Modifies existing code based on requested changes
- Validates HTML syntax and structure
- Checks for SEO meta tags (title, description, viewport)
- Verifies Tailwind CSS CDN inclusion
- Validates responsive design patterns
- Calculates confidence scores
- Generates diffs for code modifications
- Validates that modifications don't break existing features

**Input Models:**
- `CodeGenerationInput`: Requirements, optional existing code, modifications, template preference

**Output Models:**
- `CodeGenerationOutput`: Generated code, metadata, validation results, confidence score, diff information

**Key Methods:**
- `execute()`: Main execution method that routes to generation or modification
- `_generate_code()`: Generate new code (template-based or LLM-based)
- `_modify_code()`: Modify existing code with requested changes
- `_generate_from_template()`: Generate code using templates with customizations
- `_validate_code()`: Comprehensive HTML validation
- `_generate_diff()`: Generate diff between old and new code
- `_validate_modifications()`: Ensure modifications don't break existing features

### 2. Template Library (`templates.py`)

**Key Features:**
- Pre-built templates for common website types
- Jinja2-based template customization
- Template selection based on site type
- Customization points for colors, content, and structure

**Available Templates:**
1. **Portfolio**: Professional portfolio with projects, skills, and contact sections
2. **Blog**: Clean blog layout with posts, categories, and sidebar
3. **Landing Page**: High-conversion landing page with hero, features, and testimonials
4. **Contact Form**: Simple contact page with form and business information

**Template Customization:**
- Color schemes (accent colors, backgrounds)
- Content (titles, descriptions, text)
- Structural elements (projects, posts, features)
- Design style (modern, dark mode, etc.)

### 3. API Endpoints (`api/code.py`)

**Endpoints:**

1. **POST /api/code/generate**
   - Generate new HTML code from requirements
   - Supports synchronous and asynchronous processing
   - Returns generated code with validation results
   - WebSocket updates for real-time progress

2. **POST /api/code/modify**
   - Modify existing HTML code
   - Provides diff of changes
   - Validates that modifications preserve existing features
   - Supports async processing via Celery

3. **GET /api/code/status/{task_id}**
   - Check status of async code generation tasks
   - Returns task status and results when complete

4. **GET /api/code/templates**
   - List all available templates
   - Returns template descriptions and customization points

### 4. Celery Tasks (`services/tasks.py`)

**Background Tasks:**

1. **generate_code_task**
   - Async code generation for long-running operations
   - Queued via Celery for scalability
   - Returns complete code generation results

2. **modify_code_task**
   - Async code modification
   - Handles large code modifications efficiently
   - Returns modified code with diff information

## Usage Examples

### Generate Code from Requirements

```python
from agents.code_generation_agent import CodeGenerationAgent, CodeGenerationInput
from agents.base_agent import AgentContext

# Create agent
agent = CodeGenerationAgent()

# Create input
input_data = CodeGenerationInput(
    requirements={
        "site_type": "portfolio",
        "key_features": ["projects gallery", "contact form"],
        "color_palette": "blue and white",
        "design_style": "modern"
    }
)

# Create context
context = AgentContext(
    session_id="session-123",
    workflow_id="workflow-456"
)

# Execute
result = await agent.execute_with_metrics(input_data, context)

if result.success:
    html_code = result.generated_code.html
    confidence = result.confidence
    print(f"Generated code with confidence: {confidence}")
```

### Modify Existing Code

```python
input_data = CodeGenerationInput(
    requirements=original_requirements,
    existing_code=current_html,
    modifications=[
        "Change the color scheme to green",
        "Add a testimonials section",
        "Make the navigation sticky"
    ]
)

result = await agent.execute_with_metrics(input_data, context)

if result.success:
    modified_code = result.generated_code.html
    diff = result.code_diff
    print(f"Modified {diff.added_lines} lines added, {diff.removed_lines} removed")
```

### Use API Endpoints

```bash
# Generate code
curl -X POST http://localhost:8000/api/code/generate \
  -H "Content-Type: application/json" \
  -d '{
    "requirements": {
      "site_type": "blog",
      "key_features": ["blog posts", "categories"]
    },
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'

# Modify code
curl -X POST http://localhost:8000/api/code/modify \
  -H "Content-Type: application/json" \
  -d '{
    "existing_code": "<html>...</html>",
    "modifications": ["Add dark mode toggle"],
    "requirements": {...},
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'

# List templates
curl http://localhost:8000/api/code/templates
```

## Validation

The agent performs comprehensive validation:

1. **HTML Structure**: Valid HTML5 with proper tags
2. **Meta Tags**: Title, description, viewport
3. **Tailwind CSS**: CDN inclusion verification
4. **Responsive Design**: Breakpoints and responsive patterns
5. **Modification Safety**: Ensures changes don't break existing features

## Confidence Scoring

Confidence scores are calculated based on:
- Valid HTML structure (33%)
- Meta tags presence (33%)
- Tailwind CSS inclusion (17%)
- Responsive design patterns (17%)

Scores are reduced for:
- Validation errors (50% reduction)
- Validation warnings (10% reduction)

## Template System

Templates use Jinja2 for customization:
- Variables for colors, text, and content
- Loops for dynamic sections (projects, posts, features)
- Conditionals for optional elements
- Default values for all customization points

## Error Handling

The agent handles various error scenarios:
- LLM generation failures → Retry with exponential backoff
- Template rendering errors → Fallback to LLM generation
- Validation errors → Detailed error messages
- Modification conflicts → Warnings about removed features

## Performance

- Template-based generation: < 1 second
- LLM-based generation: 5-10 seconds
- Code modification: 5-15 seconds (depending on size)
- Async processing: Scales with Celery workers

## Future Enhancements

1. Multi-page site generation
2. Component library integration
3. Framework support (React, Vue, etc.)
4. Advanced responsive patterns
5. Accessibility enhancements
6. Performance optimization suggestions
7. Code minification
8. Asset optimization
