"""
Input Agent for parsing and extracting structured requirements from user input.

This agent:
- Processes natural language input (text or voice)
- Extracts structured requirements using Gemini
- Validates completeness of requirements
- Generates clarifying questions when needed
- Stores conversation history in Redis
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from agents.base_agent import (
    BaseAgent,
    AgentInput,
    AgentOutput,
    AgentContext,
    ValidationResult,
    AgentError,
    ErrorType,
)
from services.gemini_service import gemini_service
from services.redis_service import redis_service
from utils.logging import logger


# Input Models
class ParseRequirementsInput(AgentInput):
    """Input for parsing user requirements."""
    raw_input: str = Field(..., description="Raw user input describing website needs")
    input_type: str = Field(default="text", description="Type of input: 'text' or 'voice'")
    session_id: str = Field(..., description="Session ID for conversation history")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Previous conversation messages for context"
    )


class ClarifyRequirementsInput(AgentInput):
    """Input for handling clarifying questions."""
    session_id: str = Field(..., description="Session ID")
    user_response: str = Field(..., description="User's response to clarifying questions")
    previous_requirements: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Previously extracted partial requirements"
    )
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Conversation history"
    )


# Framework and Design Style enums
from enum import Enum

class Framework(str, Enum):
    """Supported frontend frameworks."""
    VANILLA = "vanilla"
    REACT = "react"
    VUE = "vue"
    NEXTJS = "nextjs"
    SVELTE = "svelte"


class DesignStyle(str, Enum):
    """Supported design styles."""
    BOLD_MINIMALISM = "bold_minimalism"
    BRUTALISM = "brutalism"
    FLAT_MINIMALIST = "flat_minimalist"
    ANTI_DESIGN = "anti_design"
    VIBRANT_BLOCKS = "vibrant_blocks"
    ORGANIC_FLUID = "organic_fluid"
    RETRO_NOSTALGIC = "retro_nostalgic"
    EXPERIMENTAL = "experimental"


# Output Models
class SiteRequirements(BaseModel):
    """Structured site requirements extracted from user input."""
    site_type: str = Field(..., description="Type of site (e.g., portfolio, blog, landing page)")
    pages: List[str] = Field(default_factory=list, description="List of pages to include")
    color_palette: Optional[str] = Field(None, description="Color scheme or palette")
    key_features: List[str] = Field(default_factory=list, description="Key features to implement")
    design_style: Optional[DesignStyle] = Field(None, description="Design style from predefined options")
    target_audience: Optional[str] = Field(None, description="Target audience for the site")
    content_tone: Optional[str] = Field(None, description="Tone of content (e.g., professional, casual)")
    framework: Optional[Framework] = Field(None, description="Preferred frontend framework")
    additional_details: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Any additional details"
    )


class FrameworkRecommendation(BaseModel):
    """Framework recommendation with explanation."""
    framework: Framework = Field(..., description="Recommended framework")
    explanation: str = Field(..., description="Explanation for the recommendation")
    confidence: float = Field(..., description="Confidence score (0-1)")


class RequirementsOutput(AgentOutput):
    """Output for requirements parsing."""
    requirements: Optional[SiteRequirements] = None
    needs_clarification: bool = False
    clarifying_questions: List[str] = Field(default_factory=list)
    conversation_id: Optional[str] = None
    framework_recommendation: Optional[FrameworkRecommendation] = None


class InputAgent(BaseAgent):
    """
    Input Agent for parsing natural language requirements.
    
    Responsibilities:
    - Parse text/voice input into structured requirements
    - Validate completeness of requirements
    - Generate clarifying questions for ambiguous input
    - Maintain conversation history in Redis
    """
    
    def __init__(self):
        """Initialize Input Agent."""
        super().__init__(name="InputAgent")
        self.gemini = gemini_service
        self.redis = redis_service
        logger.info("Input Agent initialized")
    
    async def execute(self, input_data: AgentInput, context: AgentContext) -> AgentOutput:
        """
        Execute input parsing based on input type.
        
        Args:
            input_data: Input data for parsing
            context: Execution context
            
        Returns:
            RequirementsOutput with parsed requirements or clarifying questions
            
        Raises:
            AgentError: If parsing fails
        """
        try:
            # Route to appropriate handler
            if isinstance(input_data, ParseRequirementsInput):
                return await self._parse_requirements(input_data, context)
            elif isinstance(input_data, ClarifyRequirementsInput):
                return await self._handle_clarification(input_data, context)
            else:
                raise AgentError(
                    message=f"Unsupported input type: {type(input_data).__name__}",
                    error_type=ErrorType.VALIDATION_ERROR,
                    agent_name=self.name,
                    recoverable=False,
                    retryable=False,
                )
        except AgentError:
            raise
        except Exception as e:
            logger.error(f"Input Agent execution error: {str(e)}")
            raise AgentError(
                message=f"Input parsing failed: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _parse_requirements(
        self,
        input_data: ParseRequirementsInput,
        context: AgentContext
    ) -> RequirementsOutput:
        """Parse user input into structured requirements."""
        try:
            # Load conversation history from Redis if not provided
            conversation_history = input_data.conversation_history or []
            if not conversation_history:
                cached_history = self._load_conversation_history(input_data.session_id)
                if cached_history:
                    conversation_history = cached_history
            
            # Build prompt for Gemini
            prompt = self._build_parsing_prompt(
                input_data.raw_input,
                conversation_history
            )
            
            # Define schema for structured output
            schema = {
                "type": "object",
                "properties": {
                    "site_type": {"type": "string"},
                    "pages": {"type": "array", "items": {"type": "string"}},
                    "color_palette": {"type": "string"},
                    "key_features": {"type": "array", "items": {"type": "string"}},
                    "design_style": {
                        "type": "string",
                        "enum": [
                            "bold_minimalism",
                            "brutalism",
                            "flat_minimalist",
                            "anti_design",
                            "vibrant_blocks",
                            "organic_fluid",
                            "retro_nostalgic",
                            "experimental"
                        ]
                    },
                    "target_audience": {"type": "string"},
                    "content_tone": {"type": "string"},
                    "framework": {
                        "type": "string",
                        "enum": ["vanilla", "react", "vue", "nextjs", "svelte"]
                    },
                    "additional_details": {"type": "object"}
                },
                "required": ["site_type", "key_features"]
            }
            
            # Call Gemini to extract requirements
            logger.info(f"Parsing requirements for session {input_data.session_id}")
            response = await self.gemini.generate_json(
                prompt=prompt,
                schema=schema,
                temperature=0.2,  # Low temperature for consistency
            )
            
            # Parse into SiteRequirements model
            requirements = SiteRequirements(**response)
            
            # Update conversation history
            conversation_history.append({
                "role": "user",
                "content": input_data.raw_input,
                "timestamp": datetime.utcnow().isoformat()
            })
            conversation_history.append({
                "role": "assistant",
                "content": f"Extracted requirements: {requirements.model_dump_json()}",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Save conversation history to Redis
            self._save_conversation_history(input_data.session_id, conversation_history)
            
            # Check if requirements are complete
            is_complete, missing_info = self._check_completeness(requirements)
            
            if not is_complete:
                # Generate clarifying questions
                questions = await self._generate_clarifying_questions(
                    requirements,
                    missing_info,
                    conversation_history
                )
                
                logger.info(f"Requirements incomplete, generated {len(questions)} clarifying questions")
                
                return RequirementsOutput(
                    success=True,
                    requirements=requirements,
                    needs_clarification=True,
                    clarifying_questions=questions,
                    conversation_id=input_data.session_id,
                    data={
                        "requirements": requirements.model_dump(),
                        "needs_clarification": True,
                        "clarifying_questions": questions,
                        "missing_info": missing_info
                    }
                )
            
            # Generate framework recommendation if not specified
            framework_recommendation = None
            if not requirements.framework:
                logger.info("No framework specified, generating recommendation")
                framework_recommendation = await self.recommend_framework(requirements)
                # Update requirements with recommended framework
                requirements.framework = framework_recommendation.framework
            
            logger.info(f"Successfully parsed complete requirements for session {input_data.session_id}")
            
            return RequirementsOutput(
                success=True,
                requirements=requirements,
                needs_clarification=False,
                conversation_id=input_data.session_id,
                framework_recommendation=framework_recommendation,
                data={
                    "requirements": requirements.model_dump(),
                    "needs_clarification": False,
                    "framework_recommendation": framework_recommendation.model_dump() if framework_recommendation else None
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing requirements: {str(e)}")
            raise AgentError(
                message=f"Failed to parse requirements: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _handle_clarification(
        self,
        input_data: ClarifyRequirementsInput,
        context: AgentContext
    ) -> RequirementsOutput:
        """Handle user response to clarifying questions."""
        try:
            # Load conversation history
            conversation_history = input_data.conversation_history or []
            if not conversation_history:
                cached_history = self._load_conversation_history(input_data.session_id)
                if cached_history:
                    conversation_history = cached_history
            
            # Build prompt with previous requirements and new response
            prompt = self._build_clarification_prompt(
                input_data.user_response,
                input_data.previous_requirements,
                conversation_history
            )
            
            # Define schema
            schema = {
                "type": "object",
                "properties": {
                    "site_type": {"type": "string"},
                    "pages": {"type": "array", "items": {"type": "string"}},
                    "color_palette": {"type": "string"},
                    "key_features": {"type": "array", "items": {"type": "string"}},
                    "design_style": {
                        "type": "string",
                        "enum": [
                            "bold_minimalism",
                            "brutalism",
                            "flat_minimalist",
                            "anti_design",
                            "vibrant_blocks",
                            "organic_fluid",
                            "retro_nostalgic",
                            "experimental"
                        ]
                    },
                    "target_audience": {"type": "string"},
                    "content_tone": {"type": "string"},
                    "framework": {
                        "type": "string",
                        "enum": ["vanilla", "react", "vue", "nextjs", "svelte"]
                    },
                    "additional_details": {"type": "object"}
                },
                "required": ["site_type", "key_features"]
            }
            
            # Call Gemini to update requirements
            logger.info(f"Processing clarification for session {input_data.session_id}")
            response = await self.gemini.generate_json(
                prompt=prompt,
                schema=schema,
                temperature=0.2,
            )
            
            # Parse updated requirements
            requirements = SiteRequirements(**response)
            
            # Update conversation history
            conversation_history.append({
                "role": "user",
                "content": input_data.user_response,
                "timestamp": datetime.utcnow().isoformat()
            })
            conversation_history.append({
                "role": "assistant",
                "content": f"Updated requirements: {requirements.model_dump_json()}",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Save conversation history
            self._save_conversation_history(input_data.session_id, conversation_history)
            
            # Check completeness again
            is_complete, missing_info = self._check_completeness(requirements)
            
            if not is_complete:
                # Generate more clarifying questions
                questions = await self._generate_clarifying_questions(
                    requirements,
                    missing_info,
                    conversation_history
                )
                
                logger.info(f"Still need clarification, generated {len(questions)} more questions")
                
                return RequirementsOutput(
                    success=True,
                    requirements=requirements,
                    needs_clarification=True,
                    clarifying_questions=questions,
                    conversation_id=input_data.session_id,
                    data={
                        "requirements": requirements.model_dump(),
                        "needs_clarification": True,
                        "clarifying_questions": questions,
                        "missing_info": missing_info
                    }
                )
            
            # Generate framework recommendation if not specified
            framework_recommendation = None
            if not requirements.framework:
                logger.info("No framework specified, generating recommendation")
                framework_recommendation = await self.recommend_framework(requirements)
                # Update requirements with recommended framework
                requirements.framework = framework_recommendation.framework
            
            logger.info(f"Requirements now complete for session {input_data.session_id}")
            
            return RequirementsOutput(
                success=True,
                requirements=requirements,
                needs_clarification=False,
                conversation_id=input_data.session_id,
                framework_recommendation=framework_recommendation,
                data={
                    "requirements": requirements.model_dump(),
                    "needs_clarification": False,
                    "framework_recommendation": framework_recommendation.model_dump() if framework_recommendation else None
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling clarification: {str(e)}")
            raise AgentError(
                message=f"Failed to process clarification: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    def _build_parsing_prompt(
        self,
        raw_input: str,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Build prompt for parsing requirements."""
        prompt = """You are an elite requirements analyst and technical consultant specializing in web development projects. You have 10+ years of experience translating client needs into precise technical specifications.

**YOUR ROLE:**
Extract structured, actionable website requirements from natural language descriptions. Be thorough, intelligent, and context-aware in your analysis.

**INFORMATION TO EXTRACT:**

1. **site_type** (REQUIRED): The primary purpose/category of the website
   - Examples: portfolio, blog, landing page, e-commerce, SaaS product, corporate website, personal website, agency site, restaurant site, real estate listing, event page, documentation site, community forum, educational platform
   - Be specific: "portfolio for photographer" vs just "portfolio"

2. **pages** (List): All pages/sections that should be included
   - Common pages: home, about, services, portfolio, blog, contact, pricing, testimonials, FAQ, team, careers
   - For single-page sites, list sections: hero, features, about, testimonials, contact
   - Infer standard pages based on site type if not explicitly mentioned

3. **color_palette** (String): Color scheme preferences
   - Extract specific colors mentioned (e.g., "blue and white", "dark theme with purple accents")
   - Note preferences like "professional", "vibrant", "minimal", "dark mode", "pastel"
   - Infer from industry standards if not specified (e.g., tech = blue/purple, health = green/blue, creative = bold colors)

4. **key_features** (List - REQUIRED): Functional requirements and interactive elements
   - Examples: contact form, image gallery, blog posts, search functionality, user authentication, shopping cart, booking system, newsletter signup, social media integration, live chat, testimonials slider, video background, parallax scrolling, animations
   - Be comprehensive - include both explicitly stated and implied features
   - Prioritize features that enhance user experience

5. **design_style** (Enum): Visual aesthetic from these specific options:
   - **bold_minimalism**: Clean layouts, striking typography, generous white space, subtle accent colors
   - **brutalism**: Raw elements, big blocks, bold fonts, authentic presentation
   - **flat_minimalist**: Highly functional, emphasizing simplicity and usability
   - **anti_design**: Asymmetric layouts, experimental typography, creative imperfections
   - **vibrant_blocks**: Big blocks, vivid contrasts, vibrant color palettes
   - **organic_fluid**: Organic, fluid, asymmetrical shapes for intuitive navigation
   - **retro_nostalgic**: Retro elements, playful geometric shapes, pastel color schemes
   - **experimental**: Experimental navigation, non-traditional scrolling, dynamic typography
   
   **MATCHING LOGIC:**
   - "modern" or "clean" → bold_minimalism
   - "simple" or "minimal" → flat_minimalist
   - "creative" or "artistic" → anti_design
   - "colorful" or "vibrant" → vibrant_blocks
   - "organic" or "natural" → organic_fluid
   - "vintage" or "retro" → retro_nostalgic
   - "unique" or "experimental" → experimental
   - If unclear, choose based on site type and target audience

6. **target_audience** (String): Who will use this website
   - Demographics: age range, profession, interests
   - Examples: "young professionals 25-35", "small business owners", "tech enthusiasts", "parents with young children", "luxury consumers"
   - Infer from site type if not stated (e.g., portfolio → potential clients/employers)

7. **content_tone** (String): Voice and style of written content
   - Options: professional, casual, friendly, authoritative, playful, inspirational, technical, conversational, formal, witty
   - Match to target audience and site type
   - Default to "professional" for business sites, "friendly" for personal sites

8. **framework** (Enum - Optional): Preferred frontend technology
   - Only extract if EXPLICITLY mentioned by user
   - Options: vanilla, react, vue, nextjs, svelte
   - Leave null if not specified - the system will recommend one

9. **additional_details** (Object): Any other relevant information
   - Brand guidelines, competitor references, specific functionality, integrations needed, content management requirements, hosting preferences, timeline, budget constraints

**EXTRACTION GUIDELINES:**

**Be Intelligent:**
- Read between the lines - infer reasonable requirements from context
- If user says "I need a site for my photography business" → infer: portfolio site, image gallery, contact form, about page, services page
- If user mentions "blog" → infer: blog listing page, individual post pages, categories, search
- Consider industry standards and best practices

**Be Comprehensive:**
- Don't just extract what's explicitly stated
- Add standard features for the site type (e.g., every business site needs a contact form)
- Include UX best practices (e.g., mobile menu, footer with links, clear CTAs)

**Be Contextual:**
- Use previous conversation history to build upon earlier requirements
- Resolve ambiguities using context from the conversation
- Maintain consistency with previously stated preferences

**Be Specific:**
- "Modern design" → Translate to specific design_style enum value
- "Nice colors" → Infer color_palette based on site type and target audience
- "Contact me" → Add "contact form" to key_features

**QUALITY CHECKS:**
- Ensure site_type and key_features are always populated (REQUIRED fields)
- Verify design_style matches one of the enum values exactly
- Check that pages list is appropriate for the site type
- Confirm target_audience and content_tone align with each other

"""
        
        # Add conversation history if available
        if conversation_history:
            prompt += "\n**PREVIOUS CONVERSATION:**\n"
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                prompt += f"{role.capitalize()}: {content}\n"
            prompt += "\n"
        
        prompt += f"""
**CURRENT USER INPUT:**
{raw_input}

**INSTRUCTIONS:**
1. Analyze the user input carefully, considering context and implications
2. Extract ALL relevant information into the structured format
3. Fill in reasonable defaults for optional fields when you can infer them
4. Be thorough - include both explicit and implicit requirements
5. Ensure design_style matches EXACTLY one of the enum values
6. Leave framework as null unless explicitly mentioned

**OUTPUT:**
Respond with valid JSON matching the schema provided. Be comprehensive and intelligent in your extraction.
"""
        
        return prompt
    
    def _build_clarification_prompt(
        self,
        user_response: str,
        previous_requirements: Optional[Dict[str, Any]],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Build prompt for processing clarification responses."""
        prompt = """You are an expert at extracting structured website requirements from natural language descriptions.

The user has provided additional information in response to clarifying questions. Update the requirements based on this new information.

"""
        
        # Add previous requirements
        if previous_requirements:
            prompt += f"\nPrevious requirements:\n{previous_requirements}\n"
        
        # Add conversation history
        if conversation_history:
            prompt += "\nConversation history:\n"
            for msg in conversation_history[-5:]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                prompt += f"{role.capitalize()}: {content}\n"
            prompt += "\n"
        
        prompt += f"""
User's response:
{user_response}

Update the requirements based on the user's response. Merge the new information with the previous requirements. If the user clarifies or changes something, update that field accordingly.

Respond with valid JSON matching the schema provided."""
        
        return prompt
    
    def _check_completeness(self, requirements: SiteRequirements) -> tuple[bool, List[str]]:
        """
        Check if requirements are complete.
        
        Returns:
            Tuple of (is_complete, missing_info)
        """
        missing_info = []
        
        # Required fields
        if not requirements.site_type:
            missing_info.append("site_type")
        
        if not requirements.key_features or len(requirements.key_features) == 0:
            missing_info.append("key_features")
        
        # Check if we have at least some basic information
        # Optional fields don't block completion, but we note if they're missing
        optional_missing = []
        
        if not requirements.pages or len(requirements.pages) == 0:
            optional_missing.append("pages")
        
        if not requirements.color_palette:
            optional_missing.append("color_palette")
        
        # Requirements are complete if all required fields are present
        is_complete = len(missing_info) == 0
        
        return is_complete, missing_info + optional_missing
    
    async def _generate_clarifying_questions(
        self,
        requirements: SiteRequirements,
        missing_info: List[str],
        conversation_history: List[Dict[str, str]]
    ) -> List[str]:
        """Generate clarifying questions for incomplete requirements."""
        try:
            prompt = f"""You are helping a user define requirements for their website. Based on the information gathered so far, generate 2-3 specific clarifying questions to fill in the gaps.

Current requirements:
{requirements.model_dump_json(indent=2)}

Missing or unclear information:
{', '.join(missing_info)}

Generate specific, actionable questions that will help clarify the requirements. Focus on the most important missing information first.

Respond with a JSON array of questions, for example:
["What specific features would you like on your site?", "What color scheme do you prefer?"]
"""
            
            response = await self.gemini.generate_json(
                prompt=prompt,
                temperature=0.3,
            )
            
            # Extract questions from response
            if isinstance(response, dict) and "questions" in response:
                return response["questions"]
            elif isinstance(response, list):
                return response
            else:
                # Fallback to generic questions
                return self._generate_fallback_questions(missing_info)
                
        except Exception as e:
            logger.warning(f"Error generating clarifying questions: {str(e)}, using fallback")
            return self._generate_fallback_questions(missing_info)
    
    def _generate_fallback_questions(self, missing_info: List[str]) -> List[str]:
        """Generate fallback questions when LLM fails."""
        question_map = {
            "site_type": "What type of website would you like to create? (e.g., portfolio, blog, landing page)",
            "key_features": "What key features would you like on your website? (e.g., contact form, image gallery, blog)",
            "pages": "What pages should your website have? (e.g., home, about, contact)",
            "color_palette": "What color scheme would you prefer for your website?",
            "design_style": "What design style are you looking for? (e.g., modern, minimalist, professional)",
            "target_audience": "Who is your target audience?",
            "content_tone": "What tone should the content have? (e.g., professional, casual, friendly)"
        }
        
        questions = []
        for info in missing_info[:3]:  # Max 3 questions
            if info in question_map:
                questions.append(question_map[info])
        
        if not questions:
            questions.append("Could you provide more details about what you'd like your website to include?")
        
        return questions
    
    async def recommend_framework(self, requirements: SiteRequirements) -> FrameworkRecommendation:
        """
        Recommend a framework based on site requirements.
        
        Analyzes site complexity, interactivity, SEO needs, and other factors
        to recommend the most appropriate frontend framework.
        
        Args:
            requirements: Site requirements
            
        Returns:
            FrameworkRecommendation with framework, explanation, and confidence
        """
        try:
            # Build prompt for framework recommendation
            prompt = f"""You are a senior technical architect and frontend consultant with 15+ years of experience. You specialize in selecting the optimal technology stack for web projects based on requirements, scalability needs, and business constraints.

**YOUR TASK:**
Analyze the website requirements below and recommend the SINGLE BEST frontend framework. Your recommendation will directly impact development time, performance, maintainability, and user experience.

**PROJECT REQUIREMENTS:**
- **Site Type**: {requirements.site_type}
- **Key Features**: {', '.join(requirements.key_features)}
- **Pages**: {', '.join(requirements.pages) if requirements.pages else 'Not specified'}
- **Target Audience**: {requirements.target_audience or 'Not specified'}
- **Design Style**: {requirements.design_style or 'Not specified'}

**AVAILABLE FRAMEWORKS:**

1. **vanilla** - Plain HTML/CSS/JavaScript
   - **Best For**: Simple static sites, landing pages, minimal interactivity, portfolio sites, informational pages
   - **Pros**: Fastest load time, no build step, easy deployment, SEO-friendly, minimal complexity
   - **Cons**: Limited scalability, manual DOM manipulation, harder to maintain complex state
   - **Ideal Complexity**: 1-5 pages, <10 interactive features
   - **Examples**: Personal portfolio, restaurant menu, event landing page, simple contact form

2. **react** - React Library (with Vite)
   - **Best For**: Complex interactive UIs, SPAs, dashboards, applications with heavy state management
   - **Pros**: Component reusability, massive ecosystem, excellent for complex UIs, great developer tools
   - **Cons**: Client-side rendering (poor initial SEO), larger bundle size, steeper learning curve
   - **Ideal Complexity**: 5+ pages, 10+ interactive features, real-time updates, complex forms
   - **Examples**: Admin dashboard, SaaS application, social media platform, interactive tools

3. **vue** - Vue.js Framework (with Vite)
   - **Best For**: Progressive enhancement, moderate complexity, rapid prototyping, balanced projects
   - **Pros**: Easy learning curve, flexible architecture, good documentation, reactive data binding
   - **Cons**: Smaller ecosystem than React, less corporate backing
   - **Ideal Complexity**: 3-10 pages, 5-15 interactive features, moderate state management
   - **Examples**: Business website with forms, product catalog, member portal, booking system

4. **nextjs** - Next.js Framework (React-based with SSR/SSG)
   - **Best For**: SEO-critical sites, blogs, e-commerce, marketing sites, content-heavy applications
   - **Pros**: Server-side rendering, static generation, excellent SEO, image optimization, API routes
   - **Cons**: More complex setup, requires Node.js server (or Vercel), overkill for simple sites
   - **Ideal Complexity**: Any size, especially content-driven sites needing SEO
   - **Examples**: Blog, e-commerce store, corporate website, documentation site, news portal

5. **svelte** - Svelte Framework
   - **Best For**: Performance-critical apps, smaller bundle sizes, reactive programming, modern UX
   - **Pros**: Smallest bundle size, true reactivity, no virtual DOM, excellent performance
   - **Cons**: Smaller ecosystem, fewer resources, less mature tooling
   - **Ideal Complexity**: 3-10 pages, performance-sensitive applications
   - **Examples**: Interactive visualizations, performance-critical web apps, modern landing pages

**DECISION CRITERIA:**

**1. SEO Requirements (Weight: HIGH)**
- Does the site need to rank in search engines?
- Is it content-driven (blog, marketing, e-commerce)?
- **If YES → Strongly favor Next.js**
- **If NO → Consider React, Vue, Svelte, or Vanilla**

**2. Site Complexity (Weight: HIGH)**
- How many interactive features are required?
- How complex is the state management?
- **Simple (1-3 features) → Vanilla**
- **Moderate (4-10 features) → Vue or Svelte**
- **Complex (10+ features) → React or Next.js**

**3. Interactivity Level (Weight: MEDIUM)**
- How much user interaction is expected?
- Are there real-time updates, complex forms, or dynamic content?
- **Low → Vanilla or Next.js (SSG)**
- **Medium → Vue or Svelte**
- **High → React or Next.js**

**4. Performance Requirements (Weight: MEDIUM)**
- Is page load speed critical?
- Is the target audience on slow connections?
- **Critical → Svelte or Vanilla**
- **Important → Next.js (SSG) or Vue**
- **Standard → React**

**5. Development Speed (Weight: LOW)**
- How quickly does this need to be built?
- **Fast → Vanilla or Vue**
- **Moderate → React or Svelte**
- **Can take time → Next.js**

**6. Scalability (Weight: MEDIUM)**
- Will this grow significantly in the future?
- Will there be many developers working on it?
- **High scalability → React or Next.js**
- **Moderate → Vue**
- **Low → Vanilla or Svelte**

**RECOMMENDATION FRAMEWORK:**

**Analyze the requirements using this logic:**

1. **Check for SEO-critical keywords** in site_type:
   - "blog", "marketing", "ecommerce", "e-commerce", "corporate", "news", "magazine" → **Next.js** (confidence: 0.85+)

2. **Count interactive features**:
   - 0-3 features AND simple site_type → **Vanilla** (confidence: 0.80+)
   - 10+ features OR "dashboard", "admin", "app" in site_type → **React** (confidence: 0.85+)

3. **Check for performance keywords**:
   - "fast", "performance", "lightweight" in requirements → **Svelte** (confidence: 0.75+)

4. **Default to balanced choice**:
   - Moderate complexity, no strong signals → **Vue** (confidence: 0.70)

**OUTPUT FORMAT:**
Provide your recommendation as JSON:
{{
    "framework": "vanilla|react|vue|nextjs|svelte",
    "explanation": "2-3 sentence explanation covering: (1) Why this framework fits the requirements, (2) What specific features/characteristics make it ideal, (3) What trade-offs were considered",
    "confidence": 0.75
}}

**CONFIDENCE SCORING:**
- **0.90-1.00**: Perfect fit, clear choice, no better alternative
- **0.75-0.89**: Strong fit, minor trade-offs, recommended choice
- **0.60-0.74**: Reasonable fit, notable trade-offs, acceptable choice
- **0.50-0.59**: Marginal fit, significant trade-offs, consider alternatives

**CRITICAL INSTRUCTIONS:**
- Choose ONLY ONE framework
- Be decisive - don't hedge or suggest multiple options
- Provide specific, actionable reasoning
- Consider the user's actual needs, not theoretical best practices
- Prioritize simplicity when in doubt (prefer Vanilla or Vue over complex frameworks)
- Your recommendation will be implemented immediately - make it count

**Begin your analysis now:**"""

            # Call Gemini for recommendation
            logger.info(f"Generating framework recommendation for site type: {requirements.site_type}")
            response = await self.gemini.generate_json(
                prompt=prompt,
                temperature=0.3,  # Slightly higher for reasoning
            )
            
            # Parse response
            framework_str = response.get("framework", "vanilla")
            explanation = response.get("explanation", "")
            confidence = float(response.get("confidence", 0.7))
            
            # Validate framework
            try:
                framework = Framework(framework_str)
            except ValueError:
                logger.warning(f"Invalid framework '{framework_str}' recommended, defaulting to vanilla")
                framework = Framework.VANILLA
                explanation = f"Defaulted to vanilla HTML/CSS/JS. Original recommendation was invalid: {framework_str}"
                confidence = 0.5
            
            recommendation = FrameworkRecommendation(
                framework=framework,
                explanation=explanation,
                confidence=confidence
            )
            
            logger.info(
                f"Framework recommendation: {framework.value} "
                f"(confidence: {confidence:.2f})"
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating framework recommendation: {str(e)}")
            # Return fallback recommendation
            return self._get_fallback_framework_recommendation(requirements)
    
    def _get_fallback_framework_recommendation(
        self,
        requirements: SiteRequirements
    ) -> FrameworkRecommendation:
        """
        Generate fallback framework recommendation using rule-based logic.
        
        Args:
            requirements: Site requirements
            
        Returns:
            FrameworkRecommendation
        """
        # Simple rule-based recommendation
        site_type = requirements.site_type.lower()
        features = [f.lower() for f in requirements.key_features]
        
        # Check for SEO-critical sites
        if any(keyword in site_type for keyword in ["blog", "marketing", "ecommerce", "e-commerce"]):
            return FrameworkRecommendation(
                framework=Framework.NEXTJS,
                explanation="Next.js is recommended for SEO-critical sites like blogs and e-commerce, "
                           "providing server-side rendering and static generation capabilities.",
                confidence=0.75
            )
        
        # Check for high interactivity
        interactive_features = ["dashboard", "admin", "real-time", "chat", "interactive"]
        if any(keyword in ' '.join(features) for keyword in interactive_features):
            return FrameworkRecommendation(
                framework=Framework.REACT,
                explanation="React is recommended for highly interactive applications with complex UI requirements.",
                confidence=0.75
            )
        
        # Check for simple sites
        simple_types = ["landing", "portfolio", "contact", "simple"]
        if any(keyword in site_type for keyword in simple_types) and len(features) <= 3:
            return FrameworkRecommendation(
                framework=Framework.VANILLA,
                explanation="Vanilla HTML/CSS/JS is recommended for simple sites with minimal interactivity, "
                           "providing fast load times and easy deployment.",
                confidence=0.7
            )
        
        # Default to Vue for moderate complexity
        return FrameworkRecommendation(
            framework=Framework.VUE,
            explanation="Vue.js is recommended as a balanced choice for moderate complexity sites, "
                       "offering good developer experience and progressive enhancement.",
            confidence=0.65
        )
    
    def _save_conversation_history(self, session_id: str, history: List[Dict[str, str]]):
        """Save conversation history to Redis."""
        try:
            key = f"conversation:{session_id}"
            ttl = 3600 * 24  # 24 hours
            self.redis.set(key, history, ttl)
            logger.debug(f"Saved conversation history for session {session_id}")
        except Exception as e:
            logger.warning(f"Failed to save conversation history: {str(e)}")
    
    def _load_conversation_history(self, session_id: str) -> Optional[List[Dict[str, str]]]:
        """Load conversation history from Redis."""
        try:
            key = f"conversation:{session_id}"
            history = self.redis.get(key)
            if history:
                logger.debug(f"Loaded conversation history for session {session_id}")
                return history
            return None
        except Exception as e:
            logger.warning(f"Failed to load conversation history: {str(e)}")
            return None
    
    def validate(self, output: AgentOutput) -> ValidationResult:
        """
        Validate Input Agent output.
        
        Args:
            output: Output to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True, confidence=1.0)
        
        if not output.success:
            result.add_error("Operation failed")
            return result
        
        if not isinstance(output, RequirementsOutput):
            result.add_error("Invalid output type")
            return result
        
        # If needs clarification, questions should be present
        if output.needs_clarification:
            if not output.clarifying_questions or len(output.clarifying_questions) == 0:
                result.add_error("Needs clarification but no questions provided")
            else:
                result.add_warning(f"Requires clarification: {len(output.clarifying_questions)} questions")
        
        # If complete, requirements should be valid
        if not output.needs_clarification and output.requirements:
            req = output.requirements
            
            # Check required fields
            if not req.site_type:
                result.add_error("Missing required field: site_type")
            
            if not req.key_features or len(req.key_features) == 0:
                result.add_error("Missing required field: key_features")
            
            # Warnings for optional fields
            if not req.pages or len(req.pages) == 0:
                result.add_warning("No pages specified")
            
            if not req.color_palette:
                result.add_warning("No color palette specified")
        
        return result
