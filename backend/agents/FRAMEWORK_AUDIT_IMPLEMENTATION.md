# Framework-Specific Audit Implementation

## Overview

This document describes the framework-specific audit capabilities added to the Audit Agent. The implementation allows the system to perform specialized code quality checks based on the frontend framework used (React, Vue, Next.js, or Svelte).

## Implementation Details

### 1. Data Models

#### FrameworkAuditScore
A new Pydantic model that extends the standard audit scoring with framework information:
- `score`: 0-100 score for framework-specific best practices
- `summary`: Human-readable summary of findings
- `suggestions`: List of improvement suggestions
- `issues`: Detailed list of framework-specific issues
- `confidence`: Confidence level in the assessment (0.0-1.0)
- `framework`: The framework being audited (FrameworkType enum)

#### Updated Models
- **AuditInput**: Added optional `framework` field to specify the framework type
- **AuditResult**: Added optional `framework_specific` field containing FrameworkAuditScore

### 2. Framework-Specific Audit Methods

#### React Audit (`_audit_react`)
Checks for:
- **Key props in lists**: Detects missing `key` props in `.map()` calls
- **Hooks rules**: Identifies hooks called conditionally (violates Rules of Hooks)
- **State management**: Flags complex state objects that might benefit from useReducer
- **Performance**: Detects inline arrow functions in JSX that cause unnecessary re-renders
- **Error boundaries**: Checks for error handling components
- **useEffect dependencies**: Validates dependency arrays in useEffect hooks
- **Memoization**: Suggests useMemo for expensive computations

**Scoring**: Starts at 100, deducts points based on severity:
- Critical issues: -20 to -25 points
- Warnings: -10 to -15 points
- Info: -3 to -5 points

#### Vue Audit (`_audit_vue`)
Checks for:
- **v-for keys**: Detects missing `:key` bindings in v-for directives
- **Watcher cleanup**: Identifies watchers without cleanup (memory leak risk)
- **Reactivity patterns**: Validates proper use of reactive() vs ref()
- **Component communication**: Checks for declared emits
- **v-if with v-for**: Flags anti-pattern of using both on same element
- **Props validation**: Ensures props have type validation
- **API consistency**: Detects mixing of Composition API and Options API

**Scoring**: Similar to React, starts at 100 with deductions for issues

#### Next.js Audit (`_audit_nextjs`)
Checks for:
- **Metadata configuration**: Validates metadata exports for SEO
- **Image optimization**: Detects `<img>` tags that should use `next/image`
- **'use client' directive**: Ensures it's only used when needed
- **Data fetching**: Checks for cache configuration in fetch() calls
- **API route security**: Validates authentication in API routes
- **Loading states**: Checks for Suspense boundaries with async components
- **Error handling**: Validates error.js files or ErrorBoundary usage
- **Code splitting**: Suggests dynamic imports for large components

**Scoring**: Emphasizes security (API routes) and performance (images, metadata)

#### Svelte Audit (`_audit_svelte`)
Checks for:
- **Store subscriptions**: Prefers auto-subscription ($) over manual subscribe()
- **Reactive statements**: Flags overly complex reactive declarations
- **Event modifiers**: Suggests using event modifiers instead of manual preventDefault
- **Lifecycle cleanup**: Ensures onMount returns cleanup function when needed
- **Unnecessary reactivity**: Identifies simple reactive assignments that may not need reactivity
- **Component props**: Checks for default values on props
- **Store exports**: Validates that stores are properly exported
- **Each block keys**: Ensures {#each} blocks have keys
- **Error handling**: Checks for {:catch} blocks in {#await}

**Scoring**: Focuses on reactivity patterns and proper cleanup

### 3. Integration with Main Audit Flow

The framework-specific audit is integrated into the main `execute()` method:

1. Standard audits run first (SEO, Accessibility, Performance)
2. If a framework is specified (and not vanilla HTML), framework-specific audit runs
3. Overall score calculation includes framework score with 15% weight:
   - Without framework: SEO 30%, A11y 40%, Perf 30%
   - With framework: SEO 25%, A11y 35%, Perf 25%, Framework 15%

### 4. AI-Powered Analysis

Each framework audit uses Gemini AI for deeper semantic analysis:
- Analyzes code structure and patterns
- Identifies framework-specific anti-patterns
- Provides 2-3 actionable suggestions
- Uses low temperature (0.3) for consistency

### 5. Test Coverage

Comprehensive tests added to `test_audit_agent.py`:
- `test_audit_react_code`: Validates React-specific checks
- `test_audit_vue_code`: Validates Vue-specific checks
- `test_audit_nextjs_code`: Validates Next.js-specific checks
- `test_audit_svelte_code`: Validates Svelte-specific checks
- `test_audit_vanilla_html_no_framework_checks`: Ensures vanilla HTML skips framework checks
- `test_calculate_overall_score_with_framework`: Validates score calculation with framework

## Usage Example

```python
from agents.audit_agent import AuditAgent, AuditInput
from agents.base_agent import AgentContext
from models.framework import FrameworkType

# Create agent and context
agent = AuditAgent()
context = AgentContext(
    session_id="session-123",
    workflow_id="workflow-456"
)

# Audit React code
input_data = AuditInput(
    html_code=react_component_code,
    framework=FrameworkType.REACT
)

result = await agent.execute(input_data, context)

# Access framework-specific results
if result.audit_result.framework_specific:
    print(f"Framework: {result.audit_result.framework_specific.framework.value}")
    print(f"Score: {result.audit_result.framework_specific.score}/100")
    print(f"Issues: {len(result.audit_result.framework_specific.issues)}")
    
    for issue in result.audit_result.framework_specific.issues:
        print(f"  {issue.severity}: {issue.description}")
        print(f"  Fix: {issue.fix_suggestion}")
```

## Benefits

1. **Framework-Aware Quality Checks**: Goes beyond generic HTML/CSS/JS validation
2. **Best Practices Enforcement**: Catches framework-specific anti-patterns
3. **Performance Optimization**: Identifies framework-specific performance issues
4. **Developer Guidance**: Provides actionable, framework-specific suggestions
5. **Comprehensive Coverage**: Supports all major modern frameworks
6. **Extensible Design**: Easy to add new framework checks

## Future Enhancements

Potential improvements for future iterations:
1. Add Angular-specific audit checks
2. Implement framework version-specific checks (e.g., React 18 vs 19)
3. Add more sophisticated pattern detection using AST parsing
4. Integrate with framework-specific linters (ESLint plugins)
5. Add performance profiling for framework-specific patterns
6. Support custom framework-specific rules via configuration

## Requirements Satisfied

This implementation satisfies the following requirements from the spec:
- **Requirement 4.4**: Framework-specific best practices validation
- **Requirement 10.2**: Agent self-evaluation with framework-specific checks

## Related Files

- `backend/agents/audit_agent.py`: Main implementation
- `backend/models/framework.py`: Framework type definitions
- `backend/tests/test_audit_agent.py`: Test coverage
- `backend/verify_framework_audit_simple.py`: Static verification script
