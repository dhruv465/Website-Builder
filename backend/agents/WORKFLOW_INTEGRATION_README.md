# Workflow Integration Agent

The Workflow Integration Agent generates integration code for third-party services including payment processors, booking systems, and contact forms.

## Features

### Payment Integrations
- **Stripe**: Complete payment integration with Stripe Elements
  - Generates checkout form HTML
  - Includes client-side JavaScript for payment processing
  - Provides setup instructions for API keys and webhooks
  - Supports test mode configuration

### Booking Integrations
- **Calendly**: Embed Calendly scheduling widget
  - Inline widget or popup button options
  - Customizable appearance
  - Easy setup with Calendly URL
  
- **Custom Booking**: Custom booking form with time slot selection
  - Date and time picker
  - Contact information collection
  - Backend integration instructions
  - Email notification setup

### Contact Form Integrations
- **Formspree**: Simple contact form powered by Formspree
  - No backend required
  - Optional reCAPTCHA support
  - Email notifications included
  
- **EmailJS**: Contact form using EmailJS service
  - Client-side email sending
  - Template customization
  - Multiple email service support
  
- **Custom SMTP**: Contact form with custom backend
  - Full control over email sending
  - Custom validation and processing
  - reCAPTCHA support

## Security Features

The agent includes comprehensive security validation:
- Detects hardcoded API keys
- Checks for HTTPS usage
- Identifies XSS vulnerabilities
- Validates form input handling
- Uses Gemini AI for semantic security review
- Provides security recommendations

## Usage

### Basic Integration Generation

```python
from agents.workflow_integration_agent import (
    WorkflowIntegrationAgent,
    WorkflowIntegrationInput,
    IntegrationType,
    IntegrationProvider,
)
from agents.base_agent import AgentContext

# Create agent
agent = WorkflowIntegrationAgent()

# Create input for Stripe payment integration
input_data = WorkflowIntegrationInput(
    integration_type=IntegrationType.PAYMENT,
    provider=IntegrationProvider.STRIPE,
    config={
        "product_name": "Premium Plan",
        "price": "49.99",
        "currency": "usd",
        "button_text": "Subscribe Now"
    }
)

# Create context
context = AgentContext(
    session_id="session-123",
    workflow_id="workflow-456",
)

# Execute agent
result = await agent.execute(input_data, context)

# Access generated code
html_code = result.integration.code.html_snippet
javascript_code = result.integration.code.javascript_snippet
setup_steps = result.integration.setup_instructions.steps
security_validation = result.integration.security_validation
```

### Integration into Existing HTML

```python
# Provide existing HTML to integrate into
input_data = WorkflowIntegrationInput(
    integration_type=IntegrationType.CONTACT,
    provider=IntegrationProvider.FORMSPREE,
    config={"form_id": "abc123"},
    existing_html=existing_html_code
)

result = await agent.execute(input_data, context)

# Get HTML with integration applied
integrated_html = result.integrated_html
```

## API Endpoints

### POST /api/integrations/add
Generate and add an integration to a site.

**Request:**
```json
{
  "integration_type": "payment",
  "provider": "stripe",
  "config": {
    "product_name": "Premium Plan",
    "price": "49.99",
    "currency": "usd"
  },
  "session_id": "uuid",
  "existing_html": "<html>...</html>"
}
```

**Response:**
```json
{
  "success": true,
  "integration_type": "payment",
  "provider": "stripe",
  "code": {
    "html_snippet": "...",
    "javascript_snippet": "...",
    "dependencies": ["https://js.stripe.com/v3/"]
  },
  "setup_instructions": {
    "steps": ["1. Sign up...", "2. Get API keys..."],
    "test_mode_info": "...",
    "webhook_info": "..."
  },
  "security_validation": {
    "is_secure": true,
    "issues": [],
    "warnings": [],
    "recommendations": ["..."]
  },
  "confidence": 0.95
}
```

### GET /api/integrations/available
List all available integrations with their configuration options.

**Response:**
```json
{
  "integrations": [
    {
      "type": "payment",
      "provider": "stripe",
      "name": "Stripe Payment Integration",
      "description": "Accept credit card payments with Stripe Elements",
      "config_options": [...],
      "requirements": [...]
    }
  ],
  "count": 6
}
```

### POST /api/integrations/validate
Validate integration code for security issues.

**Request:**
```json
{
  "integration_type": "payment",
  "provider": "stripe",
  "code": {
    "html_snippet": "...",
    "javascript_snippet": "..."
  },
  "session_id": "uuid"
}
```

**Response:**
```json
{
  "success": true,
  "is_secure": true,
  "issues": [],
  "warnings": ["..."],
  "recommendations": ["..."]
}
```

## Configuration Options

### Stripe Payment
- `product_name`: Product or service name (default: "Product")
- `price`: Price amount (default: "99.99")
- `currency`: Currency code (default: "usd")
- `button_text`: Button text (default: "Buy Now")

### Calendly Booking
- `calendly_url`: Your Calendly scheduling URL (required)
- `button_text`: Button text (default: "Schedule a Meeting")
- `title`: Section title (default: "Book a Meeting")
- `description`: Section description

### Custom Booking
- `title`: Form title (default: "Book an Appointment")
- `time_slots`: Array of available time slots

### Formspree Contact
- `form_id`: Formspree form ID (required)
- `title`: Form title (default: "Contact Us")
- `include_phone`: Include phone field (default: true)
- `include_recaptcha`: Include reCAPTCHA (default: true)

### EmailJS Contact
- `service_id`: EmailJS service ID (required)
- `template_id`: EmailJS template ID (required)
- `public_key`: EmailJS public key (required)
- `title`: Form title (default: "Get in Touch")

### Custom SMTP Contact
- `title`: Form title (default: "Contact Form")
- `include_recaptcha`: Include reCAPTCHA (default: true)

## Database Storage

Integrations are stored in the `integrations` table with the following fields:
- `id`: Unique integration ID
- `site_id`: Associated site ID
- `integration_type`: Type (payment, booking, contact)
- `provider`: Provider name
- `html_snippet`, `javascript_snippet`, `css_snippet`: Code snippets
- `dependencies`: External dependencies (CDN links)
- `config`: Provider-specific configuration
- `setup_instructions`: Setup steps and information
- `is_secure`: Security validation result
- `security_issues`, `security_warnings`, `security_recommendations`: Security details
- `confidence_score`: Agent confidence score
- `is_active`: Whether integration is active
- `created_at`, `updated_at`: Timestamps

## Repository Operations

```python
from repositories.integration_repository import IntegrationRepository
from models.base import get_db

with get_db() as db:
    repo = IntegrationRepository(db)
    
    # Create integration
    integration = repo.create(
        site_id=site_id,
        integration_type="payment",
        provider="stripe",
        html_snippet=html_code,
        javascript_snippet=js_code,
        config=config_dict
    )
    
    # Get integrations for a site
    integrations = repo.get_by_site_id(site_id)
    
    # Get by type
    payment_integrations = repo.get_by_type(site_id, "payment")
    
    # Deactivate integration
    repo.deactivate(integration_id)
```

## Security Best Practices

1. **API Keys**: Never hardcode API keys in generated code. Always use placeholders like `YOUR_API_KEY` and provide instructions for proper key management.

2. **HTTPS**: All external resources and API calls should use HTTPS.

3. **Input Validation**: All form inputs should be validated and sanitized on the backend.

4. **CSRF Protection**: Implement CSRF tokens for form submissions.

5. **Rate Limiting**: Add rate limiting to prevent spam and abuse.

6. **reCAPTCHA**: Use reCAPTCHA for public forms to prevent bot submissions.

7. **Webhook Verification**: For payment integrations, always verify webhook signatures.

8. **Test Mode**: Use test mode keys during development and testing.

## Testing

Run the test suite:
```bash
pytest tests/test_workflow_integration_agent.py -v
```

Test coverage includes:
- Stripe payment integration generation
- Calendly booking integration generation
- Formspree contact form integration generation
- Integration into existing HTML
- Security validation
- Error handling
- Output validation

## Requirements

The agent requires the following requirements from the requirements document:
- **7.1**: Payment integration support (Stripe)
- **7.2**: Booking system integration (Calendly, custom)
- **7.3**: Contact form integration (Formspree, EmailJS, SMTP)
- **7.4**: Integration code generation and setup instructions
- **7.5**: Security validation for integrations

## Future Enhancements

Potential future additions:
- PayPal payment integration
- Square payment integration
- More booking providers (Acuity, SimplyBook.me)
- Newsletter signup integrations (Mailchimp, ConvertKit)
- Analytics integrations (Google Analytics, Plausible)
- Chat widget integrations (Intercom, Drift)
- Social media integrations
- E-commerce integrations (Shopify, WooCommerce)
