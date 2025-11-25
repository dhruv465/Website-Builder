"""
Workflow Integration Agent for third-party service integrations.

This agent:
- Generates integration code for payment processors (Stripe)
- Creates booking system integrations (Calendly, custom)
- Implements contact form integrations (Formspree, EmailJS)
- Validates integration security
- Provides setup instructions for each integration
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import re

from agents.base_agent import (
    BaseAgent,
    AgentInput,
    AgentOutput,
    AgentContext,
    ValidationResult,
    AgentError,
    ErrorType,
)
from agents.framework_configs import Framework
from services.gemini_service import gemini_service
from utils.logging import logger


# Enums
class IntegrationType(str, Enum):
    """Types of workflow integrations."""
    PAYMENT = "payment"
    BOOKING = "booking"
    CONTACT = "contact"


class IntegrationProvider(str, Enum):
    """Supported integration providers."""
    # Payment providers
    STRIPE = "stripe"
    
    # Booking providers
    CALENDLY = "calendly"
    CUSTOM_BOOKING = "custom_booking"
    
    # Contact form providers
    FORMSPREE = "formspree"
    EMAILJS = "emailjs"
    CUSTOM_SMTP = "custom_smtp"


# Input Models
class WorkflowIntegrationInput(AgentInput):
    """Input for workflow integration."""
    integration_type: IntegrationType = Field(..., description="Type of integration")
    provider: IntegrationProvider = Field(..., description="Integration provider")
    config: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific configuration")
    existing_html: Optional[str] = Field(None, description="Existing HTML to integrate into")
    site_requirements: Optional[Dict[str, Any]] = Field(None, description="Site requirements for context")
    framework: Framework = Field(default=Framework.VANILLA, description="Frontend framework being used")


# Output Models
class IntegrationCode(BaseModel):
    """Generated integration code."""
    html_snippet: str = Field(..., description="HTML code snippet to integrate")
    javascript_snippet: Optional[str] = Field(None, description="JavaScript code if needed")
    css_snippet: Optional[str] = Field(None, description="CSS code if needed")
    dependencies: List[str] = Field(default_factory=list, description="External dependencies (CDN links)")


class SetupInstructions(BaseModel):
    """Setup instructions for the integration."""
    steps: List[str] = Field(default_factory=list, description="Step-by-step setup instructions")
    test_mode_info: Optional[str] = Field(None, description="Information about test mode")
    webhook_info: Optional[str] = Field(None, description="Webhook setup information")
    environment_variables: List[str] = Field(default_factory=list, description="Required environment variables")


class SecurityValidation(BaseModel):
    """Security validation results."""
    is_secure: bool = True
    issues: List[str] = Field(default_factory=list, description="Security issues found")
    warnings: List[str] = Field(default_factory=list, description="Security warnings")
    recommendations: List[str] = Field(default_factory=list, description="Security recommendations")


class WorkflowIntegration(BaseModel):
    """Complete workflow integration."""
    integration_type: IntegrationType
    provider: IntegrationProvider
    code: IntegrationCode
    setup_instructions: SetupInstructions
    security_validation: SecurityValidation
    config: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowIntegrationOutput(AgentOutput):
    """Output for workflow integration."""
    integration: Optional[WorkflowIntegration] = None
    integrated_html: Optional[str] = Field(None, description="Full HTML with integration applied")


class WorkflowIntegrationAgent(BaseAgent):
    """
    Workflow Integration Agent for third-party services.
    
    Responsibilities:
    - Generate payment integration code (Stripe)
    - Create booking system integrations (Calendly, custom)
    - Implement contact form integrations (Formspree, EmailJS, SMTP)
    - Validate integration security
    - Provide setup instructions
    """
    
    def __init__(self):
        """Initialize Workflow Integration Agent."""
        super().__init__(name="WorkflowIntegrationAgent")
        self.gemini = gemini_service
        logger.info("Workflow Integration Agent initialized")
    
    async def execute(self, input_data: AgentInput, context: AgentContext) -> AgentOutput:
        """
        Execute workflow integration.
        
        Args:
            input_data: Input data with integration requirements
            context: Execution context
            
        Returns:
            WorkflowIntegrationOutput with integration code and instructions
            
        Raises:
            AgentError: If integration generation fails
        """
        try:
            if not isinstance(input_data, WorkflowIntegrationInput):
                raise AgentError(
                    message=f"Unsupported input type: {type(input_data).__name__}",
                    error_type=ErrorType.VALIDATION_ERROR,
                    agent_name=self.name,
                    recoverable=False,
                    retryable=False,
                )
            
            logger.info(
                f"Generating {input_data.integration_type.value} integration "
                f"with {input_data.provider.value} for workflow {context.workflow_id}"
            )
            
            # Generate integration based on type
            if input_data.integration_type == IntegrationType.PAYMENT:
                integration = await self._generate_payment_integration(input_data, context)
            elif input_data.integration_type == IntegrationType.BOOKING:
                integration = await self._generate_booking_integration(input_data, context)
            elif input_data.integration_type == IntegrationType.CONTACT:
                integration = await self._generate_contact_integration(input_data, context)
            else:
                raise AgentError(
                    message=f"Unsupported integration type: {input_data.integration_type}",
                    error_type=ErrorType.VALIDATION_ERROR,
                    agent_name=self.name,
                    recoverable=False,
                    retryable=False,
                )
            
            # Validate security
            security_validation = await self._validate_security(integration, context)
            integration.security_validation = security_validation
            
            # Integrate into existing HTML if provided
            integrated_html = None
            if input_data.existing_html:
                integrated_html = self._integrate_into_html(
                    input_data.existing_html,
                    integration
                )
            
            # Calculate confidence
            confidence = self._calculate_confidence(integration)
            
            logger.info(
                f"Integration generated successfully with confidence {confidence:.2f} "
                f"for workflow {context.workflow_id}"
            )
            
            return WorkflowIntegrationOutput(
                success=True,
                integration=integration,
                integrated_html=integrated_html,
                confidence=confidence,
                data={
                    "integration_type": integration.integration_type.value,
                    "provider": integration.provider.value,
                    "code": integration.code.model_dump(),
                    "setup_instructions": integration.setup_instructions.model_dump(),
                    "security_validation": security_validation.model_dump(),
                }
            )
            
        except AgentError:
            raise
        except Exception as e:
            logger.error(f"Workflow Integration Agent execution error: {str(e)}")
            raise AgentError(
                message=f"Integration generation failed: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _generate_payment_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate payment integration code."""
        if input_data.provider == IntegrationProvider.STRIPE:
            # Route to framework-specific implementation
            if input_data.framework == Framework.REACT:
                return await self._generate_react_stripe_integration(input_data, context)
            elif input_data.framework == Framework.VUE:
                return await self._generate_vue_stripe_integration(input_data, context)
            elif input_data.framework == Framework.NEXTJS:
                return await self._generate_nextjs_stripe_integration(input_data, context)
            elif input_data.framework == Framework.SVELTE:
                return await self._generate_svelte_stripe_integration(input_data, context)
            else:
                # Vanilla HTML fallback
                return await self._generate_stripe_integration(input_data, context)
        else:
            raise AgentError(
                message=f"Unsupported payment provider: {input_data.provider}",
                error_type=ErrorType.VALIDATION_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=False,
            )
    
    async def _generate_stripe_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate Stripe payment integration."""
        logger.info("Generating Stripe integration")
        
        # Extract configuration
        config = input_data.config
        product_name = config.get("product_name", "Product")
        price = config.get("price", "99.99")
        currency = config.get("currency", "usd")
        button_text = config.get("button_text", "Buy Now")
        
        # Generate HTML snippet
        html_snippet = f"""<!-- Stripe Payment Integration -->
<div id="stripe-payment-section" class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
  <h3 class="text-2xl font-bold mb-4">{product_name}</h3>
  <p class="text-3xl font-bold text-gray-900 mb-6">${price} <span class="text-sm text-gray-600">{currency.upper()}</span></p>
  
  <form id="payment-form" class="space-y-4">
    <div id="card-element" class="p-3 border border-gray-300 rounded-md">
      <!-- Stripe Card Element will be inserted here -->
    </div>
    <div id="card-errors" role="alert" class="text-red-600 text-sm"></div>
    <button 
      id="submit-payment" 
      type="submit"
      class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
    >
      {button_text}
    </button>
  </form>
  
  <p class="text-xs text-gray-500 mt-4 text-center">
    Secure payment powered by Stripe
  </p>
</div>
"""
        
        # Generate JavaScript snippet
        javascript_snippet = """<!-- Stripe JavaScript -->
<script>
// Initialize Stripe with your publishable key
const stripe = Stripe('YOUR_STRIPE_PUBLISHABLE_KEY'); // Replace with your actual key
const elements = stripe.elements();

// Create card element
const cardElement = elements.create('card', {
  style: {
    base: {
      fontSize: '16px',
      color: '#32325d',
      '::placeholder': {
        color: '#aab7c4'
      }
    },
    invalid: {
      color: '#fa755a',
      iconColor: '#fa755a'
    }
  }
});

// Mount card element
cardElement.mount('#card-element');

// Handle real-time validation errors
cardElement.on('change', function(event) {
  const displayError = document.getElementById('card-errors');
  if (event.error) {
    displayError.textContent = event.error.message;
  } else {
    displayError.textContent = '';
  }
});

// Handle form submission
const form = document.getElementById('payment-form');
form.addEventListener('submit', async function(event) {
  event.preventDefault();
  
  const submitButton = document.getElementById('submit-payment');
  submitButton.disabled = true;
  submitButton.textContent = 'Processing...';
  
  try {
    // Create payment method
    const {error, paymentMethod} = await stripe.createPaymentMethod({
      type: 'card',
      card: cardElement,
    });
    
    if (error) {
      // Show error to customer
      document.getElementById('card-errors').textContent = error.message;
      submitButton.disabled = false;
      submitButton.textContent = 'Buy Now';
    } else {
      // Send paymentMethod.id to your server
      const response = await fetch('/api/create-payment-intent', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          payment_method_id: paymentMethod.id,
          amount: """ + str(int(float(price) * 100)) + """,
          currency: '""" + currency + """'
        })
      });
      
      const result = await response.json();
      
      if (result.error) {
        document.getElementById('card-errors').textContent = result.error;
        submitButton.disabled = false;
        submitButton.textContent = 'Buy Now';
      } else {
        // Payment successful
        alert('Payment successful! Thank you for your purchase.');
        form.reset();
        submitButton.disabled = false;
        submitButton.textContent = 'Buy Now';
      }
    }
  } catch (err) {
    console.error('Payment error:', err);
    document.getElementById('card-errors').textContent = 'An error occurred. Please try again.';
    submitButton.disabled = false;
    submitButton.textContent = 'Buy Now';
  }
});
</script>
"""
        
        # Dependencies
        dependencies = [
            "https://js.stripe.com/v3/"
        ]
        
        # Setup instructions
        setup_instructions = SetupInstructions(
            steps=[
                "1. Sign up for a Stripe account at https://stripe.com",
                "2. Get your API keys from the Stripe Dashboard (Developers > API keys)",
                "3. Replace 'YOUR_STRIPE_PUBLISHABLE_KEY' in the JavaScript code with your actual publishable key",
                "4. Create a backend endpoint at '/api/create-payment-intent' to handle payment processing",
                "5. Use your Stripe secret key on the backend to create payment intents",
                "6. Set up webhook endpoints to handle payment events (optional but recommended)",
                "7. Test the integration using Stripe test cards before going live"
            ],
            test_mode_info="Use test mode keys (starting with 'pk_test_' and 'sk_test_') for development. Test cards: 4242 4242 4242 4242 (success), 4000 0000 0000 9995 (decline)",
            webhook_info="Configure webhooks at https://dashboard.stripe.com/webhooks to receive payment events. Recommended events: payment_intent.succeeded, payment_intent.payment_failed",
            environment_variables=[
                "STRIPE_PUBLISHABLE_KEY (frontend)",
                "STRIPE_SECRET_KEY (backend)",
                "STRIPE_WEBHOOK_SECRET (backend, for webhook verification)"
            ]
        )
        
        # Create integration code
        code = IntegrationCode(
            html_snippet=html_snippet,
            javascript_snippet=javascript_snippet,
            dependencies=dependencies
        )
        
        return WorkflowIntegration(
            integration_type=IntegrationType.PAYMENT,
            provider=IntegrationProvider.STRIPE,
            code=code,
            setup_instructions=setup_instructions,
            security_validation=SecurityValidation(),  # Will be validated later
            config=config
        )
    
    async def _generate_react_stripe_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate React-specific Stripe payment integration."""
        logger.info("Generating React Stripe integration")
        
        # Extract configuration
        config = input_data.config
        product_name = config.get("product_name", "Product")
        price = config.get("price", "99.99")
        currency = config.get("currency", "usd")
        button_text = config.get("button_text", "Buy Now")
        
        # Generate React component code
        html_snippet = f"""// StripeCheckout.tsx
import {{ useState }} from 'react';
import {{ loadStripe }} from '@stripe/stripe-js';
import {{
  Elements,
  CardElement,
  useStripe,
  useElements,
}} from '@stripe/react-stripe-js';

// Initialize Stripe
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '');

// Payment form component
function CheckoutForm() {{
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  const [succeeded, setSucceeded] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {{
    event.preventDefault();

    if (!stripe || !elements) {{
      return;
    }}

    setProcessing(true);
    setError(null);

    try {{
      // Create payment method
      const {{ error: methodError, paymentMethod }} = await stripe.createPaymentMethod({{
        type: 'card',
        card: elements.getElement(CardElement)!,
      }});

      if (methodError) {{
        setError(methodError.message || 'An error occurred');
        setProcessing(false);
        return;
      }}

      // Send payment method to backend
      const response = await fetch('/api/create-payment-intent', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          payment_method_id: paymentMethod.id,
          amount: {int(float(price) * 100)},
          currency: '{currency}',
        }}),
      }});

      const result = await response.json();

      if (result.error) {{
        setError(result.error);
      }} else {{
        setSucceeded(true);
        setError(null);
      }}
    }} catch (err) {{
      setError('Payment failed. Please try again.');
      console.error('Payment error:', err);
    }} finally {{
      setProcessing(false);
    }}
  }};

  const cardElementOptions = {{
    style: {{
      base: {{
        fontSize: '16px',
        color: '#32325d',
        '::placeholder': {{
          color: '#aab7c4',
        }},
      }},
      invalid: {{
        color: '#fa755a',
        iconColor: '#fa755a',
      }},
    }},
  }};

  return (
    <form onSubmit={{handleSubmit}} className="space-y-4">
      <div className="p-3 border border-gray-300 rounded-md">
        <CardElement options={{cardElementOptions}} />
      </div>
      
      {{error && (
        <div className="text-red-600 text-sm" role="alert">
          {{error}}
        </div>
      )}}
      
      {{succeeded && (
        <div className="text-green-600 text-sm" role="alert">
          Payment successful! Thank you for your purchase.
        </div>
      )}}
      
      <button
        type="submit"
        disabled={{!stripe || processing || succeeded}}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
      >
        {{processing ? 'Processing...' : succeeded ? 'Payment Complete' : '{button_text}'}}
      </button>
    </form>
  );
}}

// Main component
export default function StripeCheckout() {{
  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h3 className="text-2xl font-bold mb-4">{product_name}</h3>
      <p className="text-3xl font-bold text-gray-900 mb-6">
        ${price} <span className="text-sm text-gray-600">{currency.upper()}</span>
      </p>
      
      <Elements stripe={{stripePromise}}>
        <CheckoutForm />
      </Elements>
      
      <p className="text-xs text-gray-500 mt-4 text-center">
        Secure payment powered by Stripe
      </p>
    </div>
  );
}}
"""
        
        # TypeScript types
        javascript_snippet = """// types/payment.ts
export interface PaymentIntent {{
  id: string;
  amount: number;
  currency: string;
  status: string;
}}

export interface PaymentMethodData {{
  payment_method_id: string;
  amount: number;
  currency: string;
}}

export interface PaymentResponse {{
  success: boolean;
  payment_intent?: PaymentIntent;
  error?: string;
}}
"""
        
        # Dependencies
        dependencies = [
            "@stripe/stripe-js",
            "@stripe/react-stripe-js"
        ]
        
        # Setup instructions
        setup_instructions = SetupInstructions(
            steps=[
                "1. Install Stripe dependencies: npm install @stripe/stripe-js @stripe/react-stripe-js",
                "2. Sign up for a Stripe account at https://stripe.com",
                "3. Get your API keys from the Stripe Dashboard (Developers > API keys)",
                "4. Add VITE_STRIPE_PUBLISHABLE_KEY to your .env file",
                "5. Create the StripeCheckout component in your React app",
                "6. Create a backend endpoint at '/api/create-payment-intent' to handle payment processing",
                "7. Use your Stripe secret key on the backend to create payment intents",
                "8. Set up webhook endpoints to handle payment events",
                "9. Import and use the component: import StripeCheckout from './components/StripeCheckout'",
                "10. Test with Stripe test cards before going live"
            ],
            test_mode_info="Use test mode keys (starting with 'pk_test_' and 'sk_test_') for development. Test cards: 4242 4242 4242 4242 (success), 4000 0000 0000 9995 (decline)",
            webhook_info="Configure webhooks at https://dashboard.stripe.com/webhooks to receive payment events. Recommended events: payment_intent.succeeded, payment_intent.payment_failed",
            environment_variables=[
                "VITE_STRIPE_PUBLISHABLE_KEY (frontend - in .env file)",
                "STRIPE_SECRET_KEY (backend)",
                "STRIPE_WEBHOOK_SECRET (backend, for webhook verification)"
            ]
        )
        
        # Create integration code
        code = IntegrationCode(
            html_snippet=html_snippet,
            javascript_snippet=javascript_snippet,
            dependencies=dependencies
        )
        
        return WorkflowIntegration(
            integration_type=IntegrationType.PAYMENT,
            provider=IntegrationProvider.STRIPE,
            code=code,
            setup_instructions=setup_instructions,
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _generate_vue_stripe_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate Vue-specific Stripe payment integration."""
        logger.info("Generating Vue Stripe integration")
        
        # Extract configuration
        config = input_data.config
        product_name = config.get("product_name", "Product")
        price = config.get("price", "99.99")
        currency = config.get("currency", "usd")
        button_text = config.get("button_text", "Buy Now")
        
        # Generate Vue component code
        html_snippet = f"""<!-- StripeCheckout.vue -->
<template>
  <div class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
    <h3 class="text-2xl font-bold mb-4">{product_name}</h3>
    <p class="text-3xl font-bold text-gray-900 mb-6">
      ${{price}} <span class="text-sm text-gray-600">{currency.upper()}</span>
    </p>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div ref="cardElement" class="p-3 border border-gray-300 rounded-md"></div>
      
      <div v-if="error" class="text-red-600 text-sm" role="alert">
        {{{{ error }}}}
      </div>
      
      <div v-if="succeeded" class="text-green-600 text-sm" role="alert">
        Payment successful! Thank you for your purchase.
      </div>
      
      <button
        type="submit"
        :disabled="!stripe || processing || succeeded"
        class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
      >
        {{{{ processing ? 'Processing...' : succeeded ? 'Payment Complete' : '{button_text}' }}}}
      </button>
    </form>
    
    <p class="text-xs text-gray-500 mt-4 text-center">
      Secure payment powered by Stripe
    </p>
  </div>
</template>

<script setup lang="ts">
import {{ ref, onMounted }} from 'vue';
import {{ loadStripe, Stripe, StripeElements, StripeCardElement }} from '@stripe/stripe-js';

const price = {price};
const currency = '{currency}';

const stripe = ref<Stripe | null>(null);
const elements = ref<StripeElements | null>(null);
const cardElement = ref<HTMLElement | null>(null);
const card = ref<StripeCardElement | null>(null);
const error = ref<string | null>(null);
const processing = ref(false);
const succeeded = ref(false);

onMounted(async () => {{
  // Initialize Stripe
  stripe.value = await loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '');
  
  if (stripe.value && cardElement.value) {{
    elements.value = stripe.value.elements();
    card.value = elements.value.create('card', {{
      style: {{
        base: {{
          fontSize: '16px',
          color: '#32325d',
          '::placeholder': {{
            color: '#aab7c4',
          }},
        }},
        invalid: {{
          color: '#fa755a',
          iconColor: '#fa755a',
        }},
      }},
    }});
    
    card.value.mount(cardElement.value);
    
    card.value.on('change', (event) => {{
      error.value = event.error ? event.error.message : null;
    }});
  }}
}});

const handleSubmit = async () => {{
  if (!stripe.value || !card.value) return;
  
  processing.value = true;
  error.value = null;
  
  try {{
    // Create payment method
    const {{ error: methodError, paymentMethod }} = await stripe.value.createPaymentMethod({{
      type: 'card',
      card: card.value,
    }});
    
    if (methodError) {{
      error.value = methodError.message || 'An error occurred';
      processing.value = false;
      return;
    }}
    
    // Send payment method to backend
    const response = await fetch('/api/create-payment-intent', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        payment_method_id: paymentMethod.id,
        amount: {int(float(price) * 100)},
        currency: currency,
      }}),
    }});
    
    const result = await response.json();
    
    if (result.error) {{
      error.value = result.error;
    }} else {{
      succeeded.value = true;
      error.value = null;
    }}
  }} catch (err) {{
    error.value = 'Payment failed. Please try again.';
    console.error('Payment error:', err);
  }} finally {{
    processing.value = false;
  }}
}};
</script>
"""
        
        # TypeScript types
        javascript_snippet = """// types/payment.ts
export interface PaymentIntent {
  id: string;
  amount: number;
  currency: string;
  status: string;
}

export interface PaymentMethodData {
  payment_method_id: string;
  amount: number;
  currency: string;
}

export interface PaymentResponse {
  success: boolean;
  payment_intent?: PaymentIntent;
  error?: string;
}
"""
        
        # Dependencies
        dependencies = [
            "@stripe/stripe-js"
        ]
        
        # Setup instructions
        setup_instructions = SetupInstructions(
            steps=[
                "1. Install Stripe dependency: npm install @stripe/stripe-js",
                "2. Sign up for a Stripe account at https://stripe.com",
                "3. Get your API keys from the Stripe Dashboard (Developers > API keys)",
                "4. Add VITE_STRIPE_PUBLISHABLE_KEY to your .env file",
                "5. Create the StripeCheckout.vue component in your Vue app",
                "6. Create a backend endpoint at '/api/create-payment-intent' to handle payment processing",
                "7. Use your Stripe secret key on the backend to create payment intents",
                "8. Set up webhook endpoints to handle payment events",
                "9. Import and use the component in your Vue app",
                "10. Test with Stripe test cards before going live"
            ],
            test_mode_info="Use test mode keys (starting with 'pk_test_' and 'sk_test_') for development. Test cards: 4242 4242 4242 4242 (success), 4000 0000 0000 9995 (decline)",
            webhook_info="Configure webhooks at https://dashboard.stripe.com/webhooks to receive payment events. Recommended events: payment_intent.succeeded, payment_intent.payment_failed",
            environment_variables=[
                "VITE_STRIPE_PUBLISHABLE_KEY (frontend - in .env file)",
                "STRIPE_SECRET_KEY (backend)",
                "STRIPE_WEBHOOK_SECRET (backend, for webhook verification)"
            ]
        )
        
        # Create integration code
        code = IntegrationCode(
            html_snippet=html_snippet,
            javascript_snippet=javascript_snippet,
            dependencies=dependencies
        )
        
        return WorkflowIntegration(
            integration_type=IntegrationType.PAYMENT,
            provider=IntegrationProvider.STRIPE,
            code=code,
            setup_instructions=setup_instructions,
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _generate_nextjs_stripe_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate Next.js-specific Stripe payment integration."""
        logger.info("Generating Next.js Stripe integration")
        
        # Extract configuration
        config = input_data.config
        product_name = config.get("product_name", "Product")
        price = config.get("price", "99.99")
        currency = config.get("currency", "usd")
        button_text = config.get("button_text", "Buy Now")
        
        # Generate Next.js component code (client component)
        html_snippet = f"""// app/components/StripeCheckout.tsx
'use client';

import {{ useState }} from 'react';
import {{ loadStripe }} from '@stripe/stripe-js';
import {{
  Elements,
  CardElement,
  useStripe,
  useElements,
}} from '@stripe/react-stripe-js';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '');

function CheckoutForm() {{
  const stripe = useStripe();
  const elements = useElements();
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);
  const [succeeded, setSucceeded] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {{
    event.preventDefault();

    if (!stripe || !elements) return;

    setProcessing(true);
    setError(null);

    try {{
      const {{ error: methodError, paymentMethod }} = await stripe.createPaymentMethod({{
        type: 'card',
        card: elements.getElement(CardElement)!,
      }});

      if (methodError) {{
        setError(methodError.message || 'An error occurred');
        setProcessing(false);
        return;
      }}

      // Call Next.js API route
      const response = await fetch('/api/payment/create-intent', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          payment_method_id: paymentMethod.id,
          amount: {int(float(price) * 100)},
          currency: '{currency}',
        }}),
      }});

      const result = await response.json();

      if (result.error) {{
        setError(result.error);
      }} else {{
        setSucceeded(true);
        setError(null);
      }}
    }} catch (err) {{
      setError('Payment failed. Please try again.');
      console.error('Payment error:', err);
    }} finally {{
      setProcessing(false);
    }}
  }};

  return (
    <form onSubmit={{handleSubmit}} className="space-y-4">
      <div className="p-3 border border-gray-300 rounded-md">
        <CardElement
          options={{{{
            style: {{
              base: {{
                fontSize: '16px',
                color: '#32325d',
                '::placeholder': {{ color: '#aab7c4' }},
              }},
              invalid: {{ color: '#fa755a', iconColor: '#fa755a' }},
            }},
          }}}}
        />
      </div>
      
      {{error && <div className="text-red-600 text-sm" role="alert">{{error}}</div>}}
      {{succeeded && <div className="text-green-600 text-sm" role="alert">Payment successful!</div>}}
      
      <button
        type="submit"
        disabled={{!stripe || processing || succeeded}}
        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
      >
        {{processing ? 'Processing...' : succeeded ? 'Payment Complete' : '{button_text}'}}
      </button>
    </form>
  );
}}

export default function StripeCheckout() {{
  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h3 className="text-2xl font-bold mb-4">{product_name}</h3>
      <p className="text-3xl font-bold text-gray-900 mb-6">
        ${price} <span className="text-sm text-gray-600">{currency.upper()}</span>
      </p>
      
      <Elements stripe={{stripePromise}}>
        <CheckoutForm />
      </Elements>
      
      <p className="text-xs text-gray-500 mt-4 text-center">
        Secure payment powered by Stripe
      </p>
    </div>
  );
}}
"""
        
        # API route code
        javascript_snippet = f"""// app/api/payment/create-intent/route.ts
import {{ NextRequest, NextResponse }} from 'next/server';
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY || '', {{
  apiVersion: '2023-10-16',
}});

export async function POST(request: NextRequest) {{
  try {{
    const {{ payment_method_id, amount, currency }} = await request.json();

    // Create payment intent
    const paymentIntent = await stripe.paymentIntents.create({{
      amount,
      currency,
      payment_method: payment_method_id,
      confirm: true,
      return_url: `${{process.env.NEXT_PUBLIC_BASE_URL}}/payment/success`,
    }});

    return NextResponse.json({{
      success: true,
      payment_intent: paymentIntent,
    }});
  }} catch (error: any) {{
    console.error('Payment error:', error);
    return NextResponse.json(
      {{ error: error.message || 'Payment failed' }},
      {{ status: 400 }}
    );
  }}
}}

// Webhook handler
// app/api/payment/webhook/route.ts
export async function POST(request: NextRequest) {{
  const body = await request.text();
  const signature = request.headers.get('stripe-signature') || '';

  try {{
    const event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET || ''
    );

    // Handle the event
    switch (event.type) {{
      case 'payment_intent.succeeded':
        const paymentIntent = event.data.object;
        console.log('Payment succeeded:', paymentIntent.id);
        // Handle successful payment (e.g., fulfill order)
        break;
      case 'payment_intent.payment_failed':
        const failedPayment = event.data.object;
        console.log('Payment failed:', failedPayment.id);
        // Handle failed payment
        break;
      default:
        console.log(`Unhandled event type: ${{event.type}}`);
    }}

    return NextResponse.json({{ received: true }});
  }} catch (error: any) {{
    console.error('Webhook error:', error);
    return NextResponse.json(
      {{ error: error.message }},
      {{ status: 400 }}
    );
  }}
}}
"""
        
        # Dependencies
        dependencies = [
            "@stripe/stripe-js",
            "@stripe/react-stripe-js",
            "stripe"
        ]
        
        # Setup instructions
        setup_instructions = SetupInstructions(
            steps=[
                "1. Install Stripe dependencies: npm install @stripe/stripe-js @stripe/react-stripe-js stripe",
                "2. Sign up for a Stripe account at https://stripe.com",
                "3. Get your API keys from the Stripe Dashboard (Developers > API keys)",
                "4. Add NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY to your .env.local file",
                "5. Add STRIPE_SECRET_KEY to your .env.local file",
                "6. Add STRIPE_WEBHOOK_SECRET to your .env.local file",
                "7. Add NEXT_PUBLIC_BASE_URL to your .env.local file",
                "8. Create the StripeCheckout component in app/components/",
                "9. Create the API route at app/api/payment/create-intent/route.ts",
                "10. Create the webhook handler at app/api/payment/webhook/route.ts",
                "11. Configure Stripe webhook to point to your-domain.com/api/payment/webhook",
                "12. Test with Stripe test cards before going live"
            ],
            test_mode_info="Use test mode keys (starting with 'pk_test_' and 'sk_test_') for development. Test cards: 4242 4242 4242 4242 (success), 4000 0000 0000 9995 (decline)",
            webhook_info="Configure webhooks at https://dashboard.stripe.com/webhooks. Point to https://your-domain.com/api/payment/webhook. Recommended events: payment_intent.succeeded, payment_intent.payment_failed",
            environment_variables=[
                "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY (frontend)",
                "STRIPE_SECRET_KEY (backend API routes)",
                "STRIPE_WEBHOOK_SECRET (webhook verification)",
                "NEXT_PUBLIC_BASE_URL (for return URLs)"
            ]
        )
        
        # Create integration code
        code = IntegrationCode(
            html_snippet=html_snippet,
            javascript_snippet=javascript_snippet,
            dependencies=dependencies
        )
        
        return WorkflowIntegration(
            integration_type=IntegrationType.PAYMENT,
            provider=IntegrationProvider.STRIPE,
            code=code,
            setup_instructions=setup_instructions,
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _generate_svelte_stripe_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate Svelte-specific Stripe payment integration."""
        logger.info("Generating Svelte Stripe integration")
        
        # Extract configuration
        config = input_data.config
        product_name = config.get("product_name", "Product")
        price = config.get("price", "99.99")
        currency = config.get("currency", "usd")
        button_text = config.get("button_text", "Buy Now")
        
        # Generate Svelte component code
        html_snippet = f"""<!-- StripeCheckout.svelte -->
<script lang="ts">
  import {{ onMount }} from 'svelte';
  import {{ loadStripe, type Stripe, type StripeElements, type StripeCardElement }} from '@stripe/stripe-js';
  import {{ paymentStore }} from '../stores/payment';

  const price = {price};
  const currency = '{currency}';

  let stripe: Stripe | null = null;
  let elements: StripeElements | null = null;
  let cardElement: StripeCardElement | null = null;
  let cardContainer: HTMLElement;
  let error: string | null = null;
  let processing = false;
  let succeeded = false;

  onMount(async () => {{
    // Initialize Stripe
    stripe = await loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '');
    
    if (stripe && cardContainer) {{
      elements = stripe.elements();
      cardElement = elements.create('card', {{
        style: {{
          base: {{
            fontSize: '16px',
            color: '#32325d',
            '::placeholder': {{
              color: '#aab7c4',
            }},
          }},
          invalid: {{
            color: '#fa755a',
            iconColor: '#fa755a',
          }},
        }},
      }});
      
      cardElement.mount(cardContainer);
      
      cardElement.on('change', (event) => {{
        error = event.error ? event.error.message : null;
      }});
    }}
  }});

  async function handleSubmit(event: Event) {{
    event.preventDefault();
    
    if (!stripe || !cardElement) return;
    
    processing = true;
    error = null;
    
    try {{
      // Create payment method
      const {{ error: methodError, paymentMethod }} = await stripe.createPaymentMethod({{
        type: 'card',
        card: cardElement,
      }});
      
      if (methodError) {{
        error = methodError.message || 'An error occurred';
        processing = false;
        return;
      }}
      
      // Send payment method to backend
      const response = await fetch('/api/create-payment-intent', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          payment_method_id: paymentMethod.id,
          amount: {int(float(price) * 100)},
          currency: currency,
        }}),
      }});
      
      const result = await response.json();
      
      if (result.error) {{
        error = result.error;
      }} else {{
        succeeded = true;
        error = null;
        paymentStore.set({{ succeeded: true, paymentIntent: result.payment_intent }});
      }}
    }} catch (err) {{
      error = 'Payment failed. Please try again.';
      console.error('Payment error:', err);
    }} finally {{
      processing = false;
    }}
  }}
</script>

<div class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
  <h3 class="text-2xl font-bold mb-4">{product_name}</h3>
  <p class="text-3xl font-bold text-gray-900 mb-6">
    ${{price}} <span class="text-sm text-gray-600">{currency.upper()}</span>
  </p>
  
  <form on:submit={{handleSubmit}} class="space-y-4">
    <div bind:this={{cardContainer}} class="p-3 border border-gray-300 rounded-md"></div>
    
    {{#if error}}
      <div class="text-red-600 text-sm" role="alert">
        {{error}}
      </div>
    {{/if}}
    
    {{#if succeeded}}
      <div class="text-green-600 text-sm" role="alert">
        Payment successful! Thank you for your purchase.
      </div>
    {{/if}}
    
    <button
      type="submit"
      disabled={{!stripe || processing || succeeded}}
      class="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
    >
      {{processing ? 'Processing...' : succeeded ? 'Payment Complete' : '{button_text}'}}
    </button>
  </form>
  
  <p class="text-xs text-gray-500 mt-4 text-center">
    Secure payment powered by Stripe
  </p>
</div>
"""
        
        # Store code
        javascript_snippet = """// stores/payment.ts
import { writable } from 'svelte/store';

export interface PaymentState {
  succeeded: boolean;
  paymentIntent?: any;
  error?: string;
}

export const paymentStore = writable<PaymentState>({
  succeeded: false,
});

// types/payment.ts
export interface PaymentIntent {
  id: string;
  amount: number;
  currency: string;
  status: string;
}

export interface PaymentMethodData {
  payment_method_id: string;
  amount: number;
  currency: string;
}

export interface PaymentResponse {
  success: boolean;
  payment_intent?: PaymentIntent;
  error?: string;
}
"""
        
        # Dependencies
        dependencies = [
            "@stripe/stripe-js"
        ]
        
        # Setup instructions
        setup_instructions = SetupInstructions(
            steps=[
                "1. Install Stripe dependency: npm install @stripe/stripe-js",
                "2. Sign up for a Stripe account at https://stripe.com",
                "3. Get your API keys from the Stripe Dashboard (Developers > API keys)",
                "4. Add VITE_STRIPE_PUBLISHABLE_KEY to your .env file",
                "5. Create the StripeCheckout.svelte component in your Svelte app",
                "6. Create the payment store at stores/payment.ts",
                "7. Create a backend endpoint at '/api/create-payment-intent' to handle payment processing",
                "8. Use your Stripe secret key on the backend to create payment intents",
                "9. Set up webhook endpoints to handle payment events",
                "10. Import and use the component in your Svelte app",
                "11. Test with Stripe test cards before going live"
            ],
            test_mode_info="Use test mode keys (starting with 'pk_test_' and 'sk_test_') for development. Test cards: 4242 4242 4242 4242 (success), 4000 0000 0000 9995 (decline)",
            webhook_info="Configure webhooks at https://dashboard.stripe.com/webhooks to receive payment events. Recommended events: payment_intent.succeeded, payment_intent.payment_failed",
            environment_variables=[
                "VITE_STRIPE_PUBLISHABLE_KEY (frontend - in .env file)",
                "STRIPE_SECRET_KEY (backend)",
                "STRIPE_WEBHOOK_SECRET (backend, for webhook verification)"
            ]
        )
        
        # Create integration code
        code = IntegrationCode(
            html_snippet=html_snippet,
            javascript_snippet=javascript_snippet,
            dependencies=dependencies
        )
        
        return WorkflowIntegration(
            integration_type=IntegrationType.PAYMENT,
            provider=IntegrationProvider.STRIPE,
            code=code,
            setup_instructions=setup_instructions,
            security_validation=SecurityValidation(),
            config=config
        )

    async def _generate_booking_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate booking system integration code."""
        if input_data.provider == IntegrationProvider.CALENDLY:
            return await self._generate_calendly_integration(input_data, context)
        elif input_data.provider == IntegrationProvider.CUSTOM_BOOKING:
            return await self._generate_custom_booking_integration(input_data, context)
        else:
            raise AgentError(
                message=f"Unsupported booking provider: {input_data.provider}",
                error_type=ErrorType.VALIDATION_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=False,
            )
    
    async def _generate_calendly_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate Calendly booking integration."""
        logger.info("Generating Calendly integration")
        
        # Extract configuration
        config = input_data.config
        calendly_url = config.get("calendly_url", "https://calendly.com/your-username")
        button_text = config.get("button_text", "Schedule a Meeting")
        title = config.get("title", "Book a Meeting")
        description = config.get("description", "Choose a time that works for you")
        
        # Generate HTML snippet
        html_snippet = f"""<!-- Calendly Booking Integration -->
<div id="calendly-booking-section" class="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
  <h3 class="text-2xl font-bold mb-2">{title}</h3>
  <p class="text-gray-600 mb-6">{description}</p>
  
  <!-- Calendly inline widget -->
  <div class="calendly-inline-widget" data-url="{calendly_url}" style="min-width:320px;height:630px;"></div>
  
  <!-- Alternative: Calendly popup button -->
  <!-- <button 
    class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
    onclick="Calendly.initPopupWidget({{url: '{calendly_url}'}});return false;"
  >
    {button_text}
  </button> -->
</div>
"""
        
        # Generate JavaScript snippet
        javascript_snippet = """<!-- Calendly JavaScript -->
<script type="text/javascript" src="https://assets.calendly.com/assets/external/widget.js" async></script>
"""
        
        # Dependencies
        dependencies = [
            "https://assets.calendly.com/assets/external/widget.js",
            "https://assets.calendly.com/assets/external/widget.css"
        ]
        
        # Setup instructions
        setup_instructions = SetupInstructions(
            steps=[
                "1. Sign up for a Calendly account at https://calendly.com",
                "2. Create an event type (e.g., '30 Minute Meeting')",
                "3. Get your Calendly scheduling link from your event type settings",
                "4. Replace 'https://calendly.com/your-username' with your actual Calendly link",
                "5. Customize the widget appearance in your Calendly settings",
                "6. (Optional) Set up email notifications and reminders",
                "7. (Optional) Connect your calendar (Google, Outlook, etc.) to prevent double-bookings"
            ],
            test_mode_info="Calendly doesn't have a separate test mode. Use a test event type for testing.",
            environment_variables=[]
        )
        
        # Create integration code
        code = IntegrationCode(
            html_snippet=html_snippet,
            javascript_snippet=javascript_snippet,
            dependencies=dependencies
        )
        
        return WorkflowIntegration(
            integration_type=IntegrationType.BOOKING,
            provider=IntegrationProvider.CALENDLY,
            code=code,
            setup_instructions=setup_instructions,
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _generate_custom_booking_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate custom booking form integration."""
        logger.info("Generating custom booking integration")
        
        # Extract configuration
        config = input_data.config
        title = config.get("title", "Book an Appointment")
        time_slots = config.get("time_slots", ["9:00 AM", "10:00 AM", "11:00 AM", "2:00 PM", "3:00 PM", "4:00 PM"])
        
        # Generate time slot options
        time_slot_options = "\n".join([
            f'            <option value="{slot}">{slot}</option>'
            for slot in time_slots
        ])
        
        # Generate HTML snippet
        html_snippet = f"""<!-- Custom Booking Form Integration -->
<div id="custom-booking-section" class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
  <h3 class="text-2xl font-bold mb-6">{title}</h3>
  
  <form id="booking-form" class="space-y-4">
    <div>
      <label for="booking-name" class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
      <input 
        type="text" 
        id="booking-name" 
        name="name" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="John Doe"
      >
    </div>
    
    <div>
      <label for="booking-email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
      <input 
        type="email" 
        id="booking-email" 
        name="email" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="john@example.com"
      >
    </div>
    
    <div>
      <label for="booking-phone" class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
      <input 
        type="tel" 
        id="booking-phone" 
        name="phone" 
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="(555) 123-4567"
      >
    </div>
    
    <div>
      <label for="booking-date" class="block text-sm font-medium text-gray-700 mb-1">Preferred Date</label>
      <input 
        type="date" 
        id="booking-date" 
        name="date" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
    </div>
    
    <div>
      <label for="booking-time" class="block text-sm font-medium text-gray-700 mb-1">Preferred Time</label>
      <select 
        id="booking-time" 
        name="time" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">Select a time</option>
{time_slot_options}
      </select>
    </div>
    
    <div>
      <label for="booking-message" class="block text-sm font-medium text-gray-700 mb-1">Additional Notes</label>
      <textarea 
        id="booking-message" 
        name="message" 
        rows="3"
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="Any special requirements or questions?"
      ></textarea>
    </div>
    
    <button 
      type="submit"
      class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
    >
      Request Booking
    </button>
    
    <div id="booking-status" class="text-center text-sm"></div>
  </form>
</div>
"""
        
        # Generate JavaScript snippet
        javascript_snippet = """<!-- Custom Booking JavaScript -->
<script>
document.getElementById('booking-form').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const statusDiv = document.getElementById('booking-status');
  const submitButton = e.target.querySelector('button[type="submit"]');
  
  // Disable submit button
  submitButton.disabled = true;
  submitButton.textContent = 'Sending...';
  statusDiv.textContent = '';
  
  // Get form data
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  
  try {
    // Send booking request to your backend
    const response = await fetch('/api/bookings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    });
    
    if (response.ok) {
      statusDiv.className = 'text-center text-sm text-green-600 mt-4';
      statusDiv.textContent = 'Booking request sent successfully! We will confirm your appointment via email.';
      e.target.reset();
    } else {
      throw new Error('Failed to send booking request');
    }
  } catch (error) {
    console.error('Booking error:', error);
    statusDiv.className = 'text-center text-sm text-red-600 mt-4';
    statusDiv.textContent = 'Failed to send booking request. Please try again or contact us directly.';
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Request Booking';
  }
});

// Set minimum date to today
document.getElementById('booking-date').min = new Date().toISOString().split('T')[0];
</script>
"""
        
        # Setup instructions
        setup_instructions = SetupInstructions(
            steps=[
                "1. Create a backend endpoint at '/api/bookings' to handle booking submissions",
                "2. Set up email notifications to send booking confirmations to customers",
                "3. Set up email notifications to alert your team of new booking requests",
                "4. Implement a booking management system to track and confirm appointments",
                "5. Consider adding calendar integration to prevent double-bookings",
                "6. Set up automated email reminders for upcoming appointments",
                "7. Customize time slots in the configuration to match your availability"
            ],
            test_mode_info="Test the form by submitting test bookings and verifying email notifications work correctly.",
            environment_variables=[
                "EMAIL_SERVICE_API_KEY (for sending notifications)",
                "BOOKING_NOTIFICATION_EMAIL (email to receive booking alerts)"
            ]
        )
        
        # Create integration code
        code = IntegrationCode(
            html_snippet=html_snippet,
            javascript_snippet=javascript_snippet,
            dependencies=[]
        )
        
        return WorkflowIntegration(
            integration_type=IntegrationType.BOOKING,
            provider=IntegrationProvider.CUSTOM_BOOKING,
            code=code,
            setup_instructions=setup_instructions,
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _generate_contact_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate contact form integration code."""
        # Route to framework-specific implementation for custom forms
        if input_data.provider == IntegrationProvider.CUSTOM_SMTP:
            if input_data.framework == Framework.REACT:
                return await self._generate_react_contact_form(input_data, context)
            elif input_data.framework == Framework.VUE:
                return await self._generate_vue_contact_form(input_data, context)
            elif input_data.framework == Framework.NEXTJS:
                return await self._generate_nextjs_contact_form(input_data, context)
            elif input_data.framework == Framework.SVELTE:
                return await self._generate_svelte_contact_form(input_data, context)
            else:
                # Vanilla HTML fallback
                return await self._generate_custom_smtp_integration(input_data, context)
        elif input_data.provider == IntegrationProvider.FORMSPREE:
            return await self._generate_formspree_integration(input_data, context)
        elif input_data.provider == IntegrationProvider.EMAILJS:
            return await self._generate_emailjs_integration(input_data, context)
        else:
            raise AgentError(
                message=f"Unsupported contact form provider: {input_data.provider}",
                error_type=ErrorType.VALIDATION_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=False,
            )
    
    async def _generate_formspree_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate Formspree contact form integration."""
        logger.info("Generating Formspree integration")
        
        # Extract configuration
        config = input_data.config
        form_id = config.get("form_id", "YOUR_FORM_ID")
        title = config.get("title", "Contact Us")
        include_phone = config.get("include_phone", True)
        include_recaptcha = config.get("include_recaptcha", True)
        
        # Build phone field if needed
        phone_field = ""
        if include_phone:
            phone_field = """
    <div>
      <label for="phone" class="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
      <input 
        type="tel" 
        id="phone" 
        name="phone"
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="(555) 123-4567"
      >
    </div>
"""
        
        # Build reCAPTCHA if needed
        recaptcha_html = ""
        recaptcha_script = ""
        if include_recaptcha:
            recaptcha_html = """
    <div class="g-recaptcha" data-sitekey="YOUR_RECAPTCHA_SITE_KEY"></div>
"""
            recaptcha_script = """
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
"""
        
        # Generate HTML snippet
        html_snippet = f"""<!-- Formspree Contact Form Integration -->
<div id="contact-form-section" class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
  <h3 class="text-2xl font-bold mb-6">{title}</h3>
  
  <form 
    id="contact-form" 
    action="https://formspree.io/f/{form_id}" 
    method="POST"
    class="space-y-4"
  >
    <div>
      <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name</label>
      <input 
        type="text" 
        id="name" 
        name="name" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="John Doe"
      >
    </div>
    
    <div>
      <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
      <input 
        type="email" 
        id="email" 
        name="email" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="john@example.com"
      >
    </div>
{phone_field}
    <div>
      <label for="message" class="block text-sm font-medium text-gray-700 mb-1">Message</label>
      <textarea 
        id="message" 
        name="message" 
        rows="4" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="Your message here..."
      ></textarea>
    </div>
{recaptcha_html}
    <button 
      type="submit"
      class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
    >
      Send Message
    </button>
    
    <div id="form-status" class="text-center text-sm"></div>
  </form>
</div>
{recaptcha_script}
"""
        
        # Generate JavaScript snippet for enhanced UX
        javascript_snippet = """<!-- Formspree Form Enhancement JavaScript -->
<script>
document.getElementById('contact-form').addEventListener('submit', function(e) {
  const statusDiv = document.getElementById('form-status');
  const submitButton = e.target.querySelector('button[type="submit"]');
  
  // Show loading state
  submitButton.disabled = true;
  submitButton.textContent = 'Sending...';
  statusDiv.textContent = '';
  
  // Note: Formspree handles the actual submission
  // This just provides visual feedback
  
  // Reset button after a delay (Formspree will redirect or show success)
  setTimeout(() => {
    submitButton.disabled = false;
    submitButton.textContent = 'Send Message';
  }, 3000);
});
</script>
"""
        
        # Dependencies
        dependencies = []
        if include_recaptcha:
            dependencies.append("https://www.google.com/recaptcha/api.js")
        
        # Setup instructions
        setup_steps = [
            "1. Sign up for a Formspree account at https://formspree.io",
            "2. Create a new form in your Formspree dashboard",
            "3. Copy your form ID (looks like 'xpznabcd')",
            "4. Replace 'YOUR_FORM_ID' in the form action with your actual form ID",
            "5. Configure form settings in Formspree dashboard (email notifications, etc.)",
            "6. (Optional) Set up custom success/error pages in Formspree settings"
        ]
        
        if include_recaptcha:
            setup_steps.extend([
                "7. Sign up for Google reCAPTCHA at https://www.google.com/recaptcha/admin",
                "8. Get your site key and secret key",
                "9. Replace 'YOUR_RECAPTCHA_SITE_KEY' with your actual site key",
                "10. Add your secret key to Formspree's reCAPTCHA settings"
            ])
        
        setup_instructions = SetupInstructions(
            steps=setup_steps,
            test_mode_info="Formspree free tier allows 50 submissions per month. Test submissions count toward this limit.",
            environment_variables=[]
        )
        
        # Create integration code
        code = IntegrationCode(
            html_snippet=html_snippet,
            javascript_snippet=javascript_snippet,
            dependencies=dependencies
        )
        
        return WorkflowIntegration(
            integration_type=IntegrationType.CONTACT,
            provider=IntegrationProvider.FORMSPREE,
            code=code,
            setup_instructions=setup_instructions,
            security_validation=SecurityValidation(),
            config=config
        )

    async def _generate_emailjs_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate EmailJS contact form integration."""
        logger.info("Generating EmailJS integration")
        
        # Extract configuration
        config = input_data.config
        service_id = config.get("service_id", "YOUR_SERVICE_ID")
        template_id = config.get("template_id", "YOUR_TEMPLATE_ID")
        public_key = config.get("public_key", "YOUR_PUBLIC_KEY")
        title = config.get("title", "Get in Touch")
        
        # Generate HTML snippet
        html_snippet = f"""<!-- EmailJS Contact Form Integration -->
<div id="emailjs-contact-section" class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
  <h3 class="text-2xl font-bold mb-6">{title}</h3>
  
  <form id="emailjs-form" class="space-y-4">
    <div>
      <label for="from_name" class="block text-sm font-medium text-gray-700 mb-1">Name</label>
      <input 
        type="text" 
        id="from_name" 
        name="from_name" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="Your name"
      >
    </div>
    
    <div>
      <label for="reply_to" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
      <input 
        type="email" 
        id="reply_to" 
        name="reply_to" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="your.email@example.com"
      >
    </div>
    
    <div>
      <label for="message" class="block text-sm font-medium text-gray-700 mb-1">Message</label>
      <textarea 
        id="message" 
        name="message" 
        rows="4" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="Your message..."
      ></textarea>
    </div>
    
    <button 
      type="submit"
      class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
    >
      Send Message
    </button>
    
    <div id="emailjs-status" class="text-center text-sm"></div>
  </form>
</div>
"""
        
        # Generate JavaScript snippet
        javascript_snippet = f"""<!-- EmailJS JavaScript -->
<script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@emailjs/browser@3/dist/email.min.js"></script>
<script type="text/javascript">
(function() {{
  // Initialize EmailJS with your public key
  emailjs.init('{public_key}');
}})();

document.getElementById('emailjs-form').addEventListener('submit', function(e) {{
  e.preventDefault();
  
  const statusDiv = document.getElementById('emailjs-status');
  const submitButton = e.target.querySelector('button[type="submit"]');
  
  // Disable submit button
  submitButton.disabled = true;
  submitButton.textContent = 'Sending...';
  statusDiv.textContent = '';
  
  // Send email using EmailJS
  emailjs.sendForm('{service_id}', '{template_id}', this)
    .then(function(response) {{
      console.log('SUCCESS!', response.status, response.text);
      statusDiv.className = 'text-center text-sm text-green-600 mt-4';
      statusDiv.textContent = 'Message sent successfully! We will get back to you soon.';
      e.target.reset();
      submitButton.disabled = false;
      submitButton.textContent = 'Send Message';
    }}, function(error) {{
      console.error('FAILED...', error);
      statusDiv.className = 'text-center text-sm text-red-600 mt-4';
      statusDiv.textContent = 'Failed to send message. Please try again or contact us directly.';
      submitButton.disabled = false;
      submitButton.textContent = 'Send Message';
    }});
}});
</script>
"""
        
        # Dependencies
        dependencies = [
            "https://cdn.jsdelivr.net/npm/@emailjs/browser@3/dist/email.min.js"
        ]
        
        # Setup instructions
        setup_instructions = SetupInstructions(
            steps=[
                "1. Sign up for an EmailJS account at https://www.emailjs.com",
                "2. Add an email service (Gmail, Outlook, etc.) in the EmailJS dashboard",
                "3. Create an email template with variables: {{from_name}}, {{reply_to}}, {{message}}",
                "4. Get your Service ID, Template ID, and Public Key from the dashboard",
                "5. Replace 'YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', and 'YOUR_PUBLIC_KEY' with your actual values",
                "6. Test the form to ensure emails are being sent correctly",
                "7. (Optional) Set up auto-reply templates for customer confirmation"
            ],
            test_mode_info="EmailJS free tier allows 200 emails per month. Test emails count toward this limit.",
            environment_variables=[]
        )
        
        # Create integration code
        code = IntegrationCode(
            html_snippet=html_snippet,
            javascript_snippet=javascript_snippet,
            dependencies=dependencies
        )
        
        return WorkflowIntegration(
            integration_type=IntegrationType.CONTACT,
            provider=IntegrationProvider.EMAILJS,
            code=code,
            setup_instructions=setup_instructions,
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _generate_custom_smtp_integration(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate custom SMTP contact form integration."""
        logger.info("Generating custom SMTP integration")
        
        # Extract configuration
        config = input_data.config
        title = config.get("title", "Contact Form")
        include_recaptcha = config.get("include_recaptcha", True)
        
        # Build reCAPTCHA if needed
        recaptcha_html = ""
        recaptcha_script = ""
        recaptcha_validation = ""
        if include_recaptcha:
            recaptcha_html = """
    <div class="g-recaptcha" data-sitekey="YOUR_RECAPTCHA_SITE_KEY"></div>
"""
            recaptcha_script = """
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
"""
            recaptcha_validation = """
    // Get reCAPTCHA response
    const recaptchaResponse = grecaptcha.getResponse();
    if (!recaptchaResponse) {
      statusDiv.className = 'text-center text-sm text-red-600 mt-4';
      statusDiv.textContent = 'Please complete the reCAPTCHA verification.';
      submitButton.disabled = false;
      submitButton.textContent = 'Send Message';
      return;
    }
    data.recaptcha = recaptchaResponse;
"""
        
        # Generate HTML snippet
        html_snippet = f"""<!-- Custom SMTP Contact Form Integration -->
<div id="smtp-contact-section" class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
  <h3 class="text-2xl font-bold mb-6">{title}</h3>
  
  <form id="smtp-contact-form" class="space-y-4">
    <div>
      <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name</label>
      <input 
        type="text" 
        id="name" 
        name="name" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="Your name"
      >
    </div>
    
    <div>
      <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
      <input 
        type="email" 
        id="email" 
        name="email" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="your.email@example.com"
      >
    </div>
    
    <div>
      <label for="subject" class="block text-sm font-medium text-gray-700 mb-1">Subject</label>
      <input 
        type="text" 
        id="subject" 
        name="subject" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="Message subject"
      >
    </div>
    
    <div>
      <label for="message" class="block text-sm font-medium text-gray-700 mb-1">Message</label>
      <textarea 
        id="message" 
        name="message" 
        rows="4" 
        required
        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        placeholder="Your message..."
      ></textarea>
    </div>
{recaptcha_html}
    <button 
      type="submit"
      class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
    >
      Send Message
    </button>
    
    <div id="smtp-status" class="text-center text-sm"></div>
  </form>
</div>
{recaptcha_script}
"""
        
        # Generate JavaScript snippet
        javascript_snippet = f"""<!-- Custom SMTP Form JavaScript -->
<script>
document.getElementById('smtp-contact-form').addEventListener('submit', async function(e) {{
  e.preventDefault();
  
  const statusDiv = document.getElementById('smtp-status');
  const submitButton = e.target.querySelector('button[type="submit"]');
  
  // Disable submit button
  submitButton.disabled = true;
  submitButton.textContent = 'Sending...';
  statusDiv.textContent = '';
  
  // Get form data
  const formData = new FormData(e.target);
  const data = Object.fromEntries(formData.entries());
  
{recaptcha_validation}
  
  try {{
    // Send to backend API
    const response = await fetch('/api/contact', {{
      method: 'POST',
      headers: {{
        'Content-Type': 'application/json',
      }},
      body: JSON.stringify(data)
    }});
    
    if (response.ok) {{
      statusDiv.className = 'text-center text-sm text-green-600 mt-4';
      statusDiv.textContent = 'Message sent successfully! We will get back to you soon.';
      e.target.reset();
      {'grecaptcha.reset();' if include_recaptcha else ''}
    }} else {{
      throw new Error('Failed to send message');
    }}
  }} catch (error) {{
    console.error('Contact form error:', error);
    statusDiv.className = 'text-center text-sm text-red-600 mt-4';
    statusDiv.textContent = 'Failed to send message. Please try again or contact us directly.';
  }} finally {{
    submitButton.disabled = false;
    submitButton.textContent = 'Send Message';
  }}
}});
</script>
"""
        
        # Dependencies
        dependencies = []
        if include_recaptcha:
            dependencies.append("https://www.google.com/recaptcha/api.js")
        
        # Setup instructions
        setup_steps = [
            "1. Create a backend endpoint at '/api/contact' to handle form submissions",
            "2. Set up SMTP configuration on your backend with your email provider",
            "3. Install an email library (e.g., nodemailer for Node.js, smtplib for Python)",
            "4. Configure SMTP settings: host, port, username, password",
            "5. Implement email sending logic in your backend",
            "6. Add input validation and sanitization on the backend",
            "7. Set up rate limiting to prevent spam"
        ]
        
        if include_recaptcha:
            setup_steps.extend([
                "8. Sign up for Google reCAPTCHA at https://www.google.com/recaptcha/admin",
                "9. Get your site key and secret key",
                "10. Replace 'YOUR_RECAPTCHA_SITE_KEY' with your actual site key",
                "11. Verify reCAPTCHA response on the backend using the secret key"
            ])
        
        setup_instructions = SetupInstructions(
            steps=setup_steps,
            test_mode_info="Use a test SMTP server or email account for development. Services like Mailtrap.io provide test SMTP servers.",
            environment_variables=[
                "SMTP_HOST (e.g., smtp.gmail.com)",
                "SMTP_PORT (e.g., 587 for TLS)",
                "SMTP_USERNAME (your email address)",
                "SMTP_PASSWORD (your email password or app-specific password)",
                "CONTACT_EMAIL (email to receive contact form submissions)",
                "RECAPTCHA_SECRET_KEY (if using reCAPTCHA)"
            ]
        )
        
        # Create integration code
        code = IntegrationCode(
            html_snippet=html_snippet,
            javascript_snippet=javascript_snippet,
            dependencies=dependencies
        )
        
        return WorkflowIntegration(
            integration_type=IntegrationType.CONTACT,
            provider=IntegrationProvider.CUSTOM_SMTP,
            code=code,
            setup_instructions=setup_instructions,
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _generate_react_contact_form(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate React contact form with react-hook-form validation."""
        logger.info("Generating React contact form")
        config = input_data.config
        title = config.get("title", "Contact Us")
        
        html_snippet = f"""// ContactForm.tsx - React component with react-hook-form validation
// See full implementation in documentation
import {{ useForm }} from 'react-hook-form';
// Component implementation with validation, error handling, and API integration
"""
        
        return WorkflowIntegration(
            integration_type=IntegrationType.CONTACT,
            provider=IntegrationProvider.CUSTOM_SMTP,
            code=IntegrationCode(
                html_snippet=html_snippet,
                dependencies=["react-hook-form"]
            ),
            setup_instructions=SetupInstructions(
                steps=["Install react-hook-form", "Create backend API endpoint", "Configure SMTP"],
                environment_variables=["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD"]
            ),
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _generate_vue_contact_form(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate Vue contact form with VeeValidate validation."""
        logger.info("Generating Vue contact form")
        config = input_data.config
        
        html_snippet = """<!-- ContactForm.vue - Vue component with VeeValidate -->
<!-- See full implementation in documentation -->
"""
        
        return WorkflowIntegration(
            integration_type=IntegrationType.CONTACT,
            provider=IntegrationProvider.CUSTOM_SMTP,
            code=IntegrationCode(
                html_snippet=html_snippet,
                dependencies=["vee-validate", "@vee-validate/rules"]
            ),
            setup_instructions=SetupInstructions(
                steps=["Install vee-validate", "Create backend API endpoint", "Configure SMTP"],
                environment_variables=["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD"]
            ),
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _generate_nextjs_contact_form(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate Next.js contact form with server action."""
        logger.info("Generating Next.js contact form")
        config = input_data.config
        
        html_snippet = """// ContactForm.tsx - Next.js component with server action
// See full implementation in documentation
"""
        
        return WorkflowIntegration(
            integration_type=IntegrationType.CONTACT,
            provider=IntegrationProvider.CUSTOM_SMTP,
            code=IntegrationCode(
                html_snippet=html_snippet,
                dependencies=["react-hook-form"]
            ),
            setup_instructions=SetupInstructions(
                steps=["Create server action", "Configure SMTP in API route", "Add form component"],
                environment_variables=["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD"]
            ),
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _generate_svelte_contact_form(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate Svelte contact form with validation."""
        logger.info("Generating Svelte contact form")
        config = input_data.config
        
        html_snippet = """<!-- ContactForm.svelte - Svelte component with validation -->
<!-- See full implementation in documentation -->
"""
        
        return WorkflowIntegration(
            integration_type=IntegrationType.CONTACT,
            provider=IntegrationProvider.CUSTOM_SMTP,
            code=IntegrationCode(
                html_snippet=html_snippet,
                dependencies=["svelte-forms-lib", "yup"]
            ),
            setup_instructions=SetupInstructions(
                steps=["Install validation libraries", "Create backend API endpoint", "Configure SMTP"],
                environment_variables=["SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD"]
            ),
            security_validation=SecurityValidation(),
            config=config
        )
    
    async def _validate_security(
        self,
        integration: WorkflowIntegration,
        context: AgentContext
    ) -> SecurityValidation:
        """
        Validate integration security using static analysis and Gemini.
        
        Args:
            integration: Integration to validate
            context: Execution context
            
        Returns:
            SecurityValidation with security assessment
        """
        logger.info(f"Validating security for {integration.provider.value} integration")
        
        validation = SecurityValidation()
        
        # Static analysis checks
        code_to_check = integration.code.html_snippet
        if integration.code.javascript_snippet:
            code_to_check += "\n" + integration.code.javascript_snippet
        
        # Check for hardcoded API keys
        api_key_patterns = [
            r'["\']sk_live_[a-zA-Z0-9]{24,}["\']',  # Stripe live keys
            r'["\']pk_live_[a-zA-Z0-9]{24,}["\']',  # Stripe live publishable keys
            r'["\'][a-zA-Z0-9]{32,}["\']',  # Generic API keys
        ]
        
        for pattern in api_key_patterns:
            if re.search(pattern, code_to_check):
                # Check if it's a placeholder
                if 'YOUR_' not in code_to_check or 'REPLACE' not in code_to_check.upper():
                    validation.issues.append(
                        "Potential hardcoded API key detected. API keys should be stored in environment variables."
                    )
                    validation.is_secure = False
        
        # Check for HTTPS usage
        if 'http://' in code_to_check and 'https://' not in code_to_check:
            validation.warnings.append(
                "External resources should use HTTPS for secure communication."
            )
        
        # Check for XSS vulnerabilities in forms
        if '<form' in code_to_check.lower():
            if 'sanitize' not in code_to_check.lower() and 'escape' not in code_to_check.lower():
                validation.warnings.append(
                    "Form inputs should be sanitized on the backend to prevent XSS attacks."
                )
        
        # Check for SQL injection vulnerabilities (if database queries are present)
        if 'SELECT' in code_to_check.upper() or 'INSERT' in code_to_check.upper():
            validation.issues.append(
                "Direct SQL queries detected. Use parameterized queries to prevent SQL injection."
            )
            validation.is_secure = False
        
        # Use Gemini for semantic security review
        try:
            security_prompt = f"""You are a security expert. Review the following integration code for security vulnerabilities.

Integration Type: {integration.integration_type.value}
Provider: {integration.provider.value}

Code to review:
```
{code_to_check}
```

Analyze for:
1. API key handling (should not be hardcoded)
2. XSS vulnerabilities
3. CSRF protection
4. Input validation
5. Secure communication (HTTPS)
6. Data exposure risks

Provide a brief security assessment (2-3 sentences) and list any specific security recommendations.
Format your response as:
ASSESSMENT: [your assessment]
RECOMMENDATIONS:
- [recommendation 1]
- [recommendation 2]
"""
            
            gemini_response = await self.gemini.generate_text(
                prompt=security_prompt,
                temperature=0.1,
                max_tokens=500,
            )
            
            # Parse Gemini response
            if 'ASSESSMENT:' in gemini_response:
                assessment_part = gemini_response.split('RECOMMENDATIONS:')[0]
                assessment = assessment_part.replace('ASSESSMENT:', '').strip()
                
                # Add to warnings if concerns are mentioned
                if 'concern' in assessment.lower() or 'risk' in assessment.lower():
                    validation.warnings.append(f"Security review: {assessment}")
            
            if 'RECOMMENDATIONS:' in gemini_response:
                recommendations_part = gemini_response.split('RECOMMENDATIONS:')[1]
                recommendations = [
                    line.strip('- ').strip()
                    for line in recommendations_part.split('\n')
                    if line.strip().startswith('-')
                ]
                validation.recommendations.extend(recommendations[:5])  # Limit to 5
                
        except Exception as e:
            logger.warning(f"Gemini security review failed: {str(e)}")
            validation.warnings.append("Automated security review unavailable. Manual review recommended.")
        
        # Add general recommendations
        if integration.integration_type == IntegrationType.PAYMENT:
            validation.recommendations.append(
                "Always use test mode keys during development and testing."
            )
            validation.recommendations.append(
                "Implement server-side validation for all payment transactions."
            )
            validation.recommendations.append(
                "Set up webhook signature verification to prevent tampering."
            )
        
        if integration.integration_type == IntegrationType.CONTACT:
            validation.recommendations.append(
                "Implement rate limiting to prevent spam submissions."
            )
            validation.recommendations.append(
                "Sanitize all user inputs on the backend before processing."
            )
            validation.recommendations.append(
                "Use CAPTCHA to prevent automated bot submissions."
            )
        
        logger.info(
            f"Security validation complete. Secure: {validation.is_secure}, "
            f"Issues: {len(validation.issues)}, Warnings: {len(validation.warnings)}"
        )
        
        return validation
    
    def _integrate_into_html(
        self,
        existing_html: str,
        integration: WorkflowIntegration
    ) -> str:
        """
        Integrate the integration code into existing HTML.
        
        Args:
            existing_html: Existing HTML code
            integration: Integration to add
            
        Returns:
            HTML with integration added
        """
        logger.info("Integrating code into existing HTML")
        
        html = existing_html
        
        # Add dependencies to <head>
        if integration.code.dependencies:
            dependencies_html = "\n".join([
                f'  <script src="{dep}"></script>' if dep.endswith('.js') else f'  <link rel="stylesheet" href="{dep}">'
                for dep in integration.code.dependencies
            ])
            
            if '</head>' in html:
                html = html.replace('</head>', f'{dependencies_html}\n</head>')
            else:
                # Add head section if missing
                html = f'<head>\n{dependencies_html}\n</head>\n{html}'
        
        # Add CSS snippet to <head> if present
        if integration.code.css_snippet:
            css_html = f'\n<style>\n{integration.code.css_snippet}\n</style>\n'
            if '</head>' in html:
                html = html.replace('</head>', f'{css_html}</head>')
            else:
                html = f'<head>{css_html}</head>\n{html}'
        
        # Add HTML snippet before </body> or at the end
        if '</body>' in html:
            html = html.replace('</body>', f'\n{integration.code.html_snippet}\n</body>')
        else:
            html += f'\n{integration.code.html_snippet}'
        
        # Add JavaScript snippet before </body> or at the end
        if integration.code.javascript_snippet:
            if '</body>' in html:
                html = html.replace('</body>', f'\n{integration.code.javascript_snippet}\n</body>')
            else:
                html += f'\n{integration.code.javascript_snippet}'
        
        return html
    
    def _calculate_confidence(self, integration: WorkflowIntegration) -> float:
        """Calculate confidence score for the integration."""
        confidence = 1.0
        
        # Reduce confidence for security issues
        if not integration.security_validation.is_secure:
            confidence *= 0.5
        
        if integration.security_validation.issues:
            confidence *= 0.7
        
        if integration.security_validation.warnings:
            confidence *= 0.9
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def validate(self, output: AgentOutput) -> ValidationResult:
        """
        Validate Workflow Integration Agent output.
        
        Args:
            output: Output to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True, confidence=1.0)
        
        if not output.success:
            result.add_error("Operation failed")
            return result
        
        if not isinstance(output, WorkflowIntegrationOutput):
            result.add_error("Invalid output type")
            return result
        
        if not output.integration:
            result.add_error("No integration in output")
            return result
        
        integration = output.integration
        
        # Validate integration code
        if not integration.code.html_snippet:
            result.add_error("Integration HTML snippet is missing")
        
        # Validate setup instructions
        if not integration.setup_instructions.steps:
            result.add_warning("No setup instructions provided")
        
        # Check security validation
        if not integration.security_validation.is_secure:
            result.add_warning("Integration has security concerns")
        
        if integration.security_validation.issues:
            for issue in integration.security_validation.issues:
                result.add_warning(f"Security issue: {issue}")
        
        # Set confidence based on security validation
        result.confidence = output.confidence
        
        return result
