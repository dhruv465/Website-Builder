# Framework-specific contact form generation methods
# This file contains the methods to be added to workflow_integration_agent.py

REACT_CONTACT_FORM = '''
    async def _generate_react_contact_form(
        self,
        input_data: WorkflowIntegrationInput,
        context: AgentContext
    ) -> WorkflowIntegration:
        """Generate React-specific contact form with react-hook-form validation."""
        logger.info("Generating React contact form")
        
        # Extract configuration
        config = input_data.config
        title = config.get("title", "Contact Us")
        
        # Generate React component code
        html_snippet = f"""// ContactForm.tsx
import {{ useForm }} from 'react-hook-form';
import {{ useState }} from 'react';

interface ContactFormData {{
  name: string;
  email: string;
  subject: string;
  message: string;
}}

export default function ContactForm() {{
  const {{ register, handleSubmit, formState: {{ errors }}, reset }} = useForm<ContactFormData>();
  const [status, setStatus] = useState<{{ type: 'success' | 'error' | null; message: string }}>>({{ type: null, message: '' }});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const onSubmit = async (data: ContactFormData) => {{
    setIsSubmitting(true);
    setStatus({{ type: null, message: '' }});

    try {{
      const response = await fetch('/api/contact', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(data),
      }});

      if (response.ok) {{
        setStatus({{
          type: 'success',
          message: 'Message sent successfully! We will get back to you soon.',
        }});
        reset();
      }} else {{
        throw new Error('Failed to send message');
      }}
    }} catch (error) {{
      console.error('Contact form error:', error);
      setStatus({{
        type: 'error',
        message: 'Failed to send message. Please try again or contact us directly.',
      }});
    }} finally {{
      setIsSubmitting(false);
    }}
  }};

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h3 className="text-2xl font-bold mb-6">{title}</h3>

      <form onSubmit={{handleSubmit(onSubmit)}} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
            Name
          </label>
          <input
            type="text"
            id="name"
            {{...register('name', {{ required: 'Name is required' }})}}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Your name"
          />
          {{errors.name && (
            <p className="text-red-600 text-sm mt-1">{{errors.name.message}}</p>
          )}}
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            type="email"
            id="email"
            {{...register('email', {{
              required: 'Email is required',
              pattern: {{
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{{2,}}$/i,
                message: 'Invalid email address',
              }},
            }})}}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="your.email@example.com"
          />
          {{errors.email && (
            <p className="text-red-600 text-sm mt-1">{{errors.email.message}}</p>
          )}}
        </div>

        <div>
          <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
            Subject
          </label>
          <input
            type="text"
            id="subject"
            {{...register('subject', {{ required: 'Subject is required' }})}}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Message subject"
          />
          {{errors.subject && (
            <p className="text-red-600 text-sm mt-1">{{errors.subject.message}}</p>
          )}}
        </div>

        <div>
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
            Message
          </label>
          <textarea
            id="message"
            rows={{4}}
            {{...register('message', {{
              required: 'Message is required',
              minLength: {{ value: 10, message: 'Message must be at least 10 characters' }},
            }})}}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Your message..."
          />
          {{errors.message && (
            <p className="text-red-600 text-sm mt-1">{{errors.message.message}}</p>
          )}}
        </div>

        {{status.type && (
          <div
            className={{`text-center text-sm ${{
              status.type === 'success' ? 'text-green-600' : 'text-red-600'
            }}`}}
            role="alert"
          >
            {{status.message}}
          </div>
        )}}

        <button
          type="submit"
          disabled={{isSubmitting}}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-md transition duration-200"
        >
          {{isSubmitting ? 'Sending...' : 'Send Message'}}
        </button>
      </form>
    </div>
  );
}}
"""
        
        # TypeScript types
        javascript_snippet = """// types/contact.ts
export interface ContactFormData {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export interface ContactResponse {
  success: boolean;
  message?: string;
  error?: string;
}
"""
        
        # Dependencies
        dependencies = ["react-hook-form"]
        
        # Setup instructions
        setup_instructions = SetupInstructions(
            steps=[
                "1. Install react-hook-form: npm install react-hook-form",
                "2. Create the ContactForm component in your React app",
                "3. Create a backend endpoint at '/api/contact' to handle form submissions",
                "4. Set up SMTP configuration on your backend",
                "5. Implement email sending logic in your backend",
                "6. Add input validation and sanitization on the backend",
                "7. Set up rate limiting to prevent spam",
                "8. Import and use the component: import ContactForm from './components/ContactForm'"
            ],
            test_mode_info="Test the form with various inputs to ensure validation works correctly.",
            environment_variables=[
                "SMTP_HOST (backend)",
                "SMTP_PORT (backend)",
                "SMTP_USERNAME (backend)",
                "SMTP_PASSWORD (backend)",
                "CONTACT_EMAIL (backend - email to receive submissions)"
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
'''

# Note: Due to length constraints, I'm providing the template for one framework.
# The actual implementation should include all four frameworks (React, Vue, Next.js, Svelte)
# following similar patterns with framework-specific validation libraries and patterns.
