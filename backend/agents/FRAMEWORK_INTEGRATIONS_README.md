# Framework-Specific Workflow Integrations

## Overview

This document describes the framework-specific workflow integrations added to the Workflow Integration Agent. These integrations provide tailored code generation for payment processing and contact forms across different frontend frameworks.

## Implemented Features

### 1. Framework-Specific Payment Integration (Stripe)

The Workflow Integration Agent now supports generating Stripe payment integration code for:

#### React
- **Component**: `StripeCheckout.tsx`
- **Dependencies**: `@stripe/stripe-js`, `@stripe/react-stripe-js`
- **Features**:
  - Functional component with hooks (useState)
  - CardElement from Stripe React library
  - Form validation and error handling
  - TypeScript types for payment data
  - Environment variable configuration (VITE_STRIPE_PUBLISHABLE_KEY)

#### Vue
- **Component**: `StripeCheckout.vue`
- **Dependencies**: `@stripe/stripe-js`
- **Features**:
  - Composition API with ref/reactive
  - Stripe Elements integration
  - Form validation with event handling
  - TypeScript support
  - Environment variable configuration (VITE_STRIPE_PUBLISHABLE_KEY)

#### Next.js
- **Component**: `app/components/StripeCheckout.tsx` (client component)
- **API Route**: `app/api/payment/create-intent/route.ts`
- **Webhook**: `app/api/payment/webhook/route.ts`
- **Dependencies**: `@stripe/stripe-js`, `@stripe/react-stripe-js`, `stripe`
- **Features**:
  - Client component with 'use client' directive
  - Server-side payment processing via API routes
  - Webhook handler for payment events
  - Environment variable configuration (NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET)

#### Svelte
- **Component**: `StripeCheckout.svelte`
- **Store**: `stores/payment.ts`
- **Dependencies**: `@stripe/stripe-js`
- **Features**:
  - Reactive Svelte component
  - Writable stores for payment state
  - onMount lifecycle for Stripe initialization
  - TypeScript support
  - Environment variable configuration (VITE_STRIPE_PUBLISHABLE_KEY)

### 2. Framework-Specific Contact Forms

The agent now generates contact forms with framework-appropriate validation:

#### React
- **Library**: react-hook-form
- **Features**:
  - Form validation with useForm hook
  - Error handling and display
  - TypeScript types
  - Async form submission

#### Vue
- **Library**: VeeValidate
- **Features**:
  - Composition API validation
  - Reactive error handling
  - Form state management

#### Next.js
- **Features**:
  - Server actions for form submission
  - react-hook-form for client-side validation
  - API route for backend processing

#### Svelte
- **Libraries**: svelte-forms-lib, yup
- **Features**:
  - Reactive form validation
  - Store-based state management
  - Schema validation with yup

## Usage

### Input Model

The `WorkflowIntegrationInput` model now includes a `framework` field:

```python
class WorkflowIntegrationInput(AgentInput):
    integration_type: IntegrationType
    provider: IntegrationProvider
    config: Dict[str, Any]
    existing_html: Optional[str]
    site_requirements: Optional[Dict[str, Any]]
    framework: Framework = Framework.VANILLA  # New field
```

### Example Usage

```python
from agents.workflow_integration_agent import WorkflowIntegrationAgent, WorkflowIntegrationInput
from agents.framework_configs import Framework

# Create input for React Stripe integration
input_data = WorkflowIntegrationInput(
    integration_type=IntegrationType.PAYMENT,
    provider=IntegrationProvider.STRIPE,
    framework=Framework.REACT,
    config={
        "product_name": "Premium Plan",
        "price": "29.99",
        "currency": "usd",
        "button_text": "Subscribe Now"
    }
)

# Execute agent
agent = WorkflowIntegrationAgent()
result = await agent.execute(input_data, context)

# Access generated code
integration = result.integration
print(integration.code.html_snippet)  # React component code
print(integration.code.dependencies)  # ['@stripe/stripe-js', '@stripe/react-stripe-js']
print(integration.setup_instructions.steps)  # Setup instructions
```

## Routing Logic

The agent automatically routes to framework-specific implementations:

1. **Payment Integration**: Routes based on `framework` field
   - React → `_generate_react_stripe_integration()`
   - Vue → `_generate_vue_stripe_integration()`
   - Next.js → `_generate_nextjs_stripe_integration()`
   - Svelte → `_generate_svelte_stripe_integration()`
   - Vanilla → `_generate_stripe_integration()` (fallback)

2. **Contact Forms**: Routes for CUSTOM_SMTP provider
   - React → `_generate_react_contact_form()`
   - Vue → `_generate_vue_contact_form()`
   - Next.js → `_generate_nextjs_contact_form()`
   - Svelte → `_generate_svelte_contact_form()`
   - Vanilla → `_generate_custom_smtp_integration()` (fallback)

## Security Considerations

All framework-specific integrations include:

1. **Environment Variable Usage**: API keys are never hardcoded
2. **Input Validation**: Form inputs are validated on both client and server
3. **Error Handling**: Proper error messages without exposing sensitive data
4. **HTTPS Enforcement**: All external API calls use HTTPS
5. **Security Validation**: Automated security checks via `_validate_security()`

## Setup Instructions

Each integration includes detailed setup instructions covering:

1. Dependency installation
2. API key configuration
3. Environment variable setup
4. Backend endpoint creation
5. Testing procedures
6. Production deployment considerations

## Environment Variables

### React/Vue/Svelte (Vite-based)
- `VITE_STRIPE_PUBLISHABLE_KEY`: Stripe publishable key (frontend)
- Backend variables: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`

### Next.js
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`: Stripe publishable key (frontend)
- `STRIPE_SECRET_KEY`: Stripe secret key (API routes)
- `STRIPE_WEBHOOK_SECRET`: Webhook verification secret
- `NEXT_PUBLIC_BASE_URL`: Base URL for return URLs

### SMTP Configuration (All Frameworks)
- `SMTP_HOST`: SMTP server host
- `SMTP_PORT`: SMTP server port
- `SMTP_USERNAME`: SMTP username
- `SMTP_PASSWORD`: SMTP password
- `CONTACT_EMAIL`: Email to receive contact form submissions

## Testing

### Test Mode
All payment integrations support Stripe test mode:
- Use test keys (pk_test_*, sk_test_*)
- Test cards: 4242 4242 4242 4242 (success), 4000 0000 0000 9995 (decline)

### Contact Forms
- Test with various inputs to verify validation
- Test error handling with invalid data
- Verify email delivery in test environment

## Future Enhancements

Potential improvements for future iterations:

1. **Additional Payment Providers**: PayPal, Square, etc.
2. **More Validation Libraries**: Formik for React, Vuelidate for Vue
3. **Advanced Features**: Multi-step forms, file uploads, payment plans
4. **Internationalization**: Multi-language support for forms
5. **Accessibility**: Enhanced ARIA labels and keyboard navigation

## Requirements Satisfied

This implementation satisfies the following requirements:

- **Requirement 8.1**: Payment integration support with framework-specific implementations
- **Requirement 8.3**: Contact form integration with framework-appropriate validation
- **Requirement 8.4**: Security validation for all integrations
- **Requirement 7.5**: Secure integration code following best practices

## Related Files

- `backend/agents/workflow_integration_agent.py`: Main implementation
- `backend/agents/framework_configs.py`: Framework configuration definitions
- `backend/agents/base_agent.py`: Base agent interface
- `.kiro/specs/smart-website-builder/tasks.md`: Task tracking
- `.kiro/specs/smart-website-builder/requirements.md`: Requirements documentation
