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
        prompt = """You are an expert at extracting structured website requirements from natural language descriptions.

Your task is to analyze the user's input and extract the following information:
- site_type: The type of website (e.g., portfolio, blog, landing page, e-commerce, contact form)
- pages: List of pages to include (e.g., ["home", "about", "contact"])
- color_palette: Color scheme or specific colors mentioned
- key_features: List of features to implement (e.g., ["contact form", "image gallery", "blog posts"])
- design_style: Design aesthetic from these options:
  * bold_minimalism: Clean layouts, striking typography, generous white space, subtle accent colors
  * brutalism: Raw elements, big blocks, bold fonts, authentic presentation
  * flat_minimalist: Highly functional, emphasizing simplicity and usability
  * anti_design: Asymmetric layouts, experimental typography, creative imperfections
  * vibrant_blocks: Big blocks, vivid contrasts, vibrant color palettes
  * organic_fluid: Organic, fluid, asymmetrical shapes for intuitive navigation
  * retro_nostalgic: Retro elements, playful geometric shapes, pastel color schemes
  * experimental: Experimental navigation, non-traditional scrolling, dynamic typography
  Extract if the user mentions a specific style or aesthetic that matches one of these options.
- target_audience: Who the site is for
- content_tone: Tone of the content (e.g., professional, casual, friendly)
- framework: Preferred frontend framework (vanilla, react, vue, nextjs, svelte). Extract if explicitly mentioned by the user.
- additional_details: Any other relevant information

"""
        
        # Add conversation history if available
        if conversation_history:
            prompt += "\nPrevious conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                prompt += f"{role.capitalize()}: {content}\n"
            prompt += "\n"
        
        prompt += f"""
Current user input:
{raw_input}

Extract as much information as possible from the input. If information is not explicitly mentioned, you can infer reasonable defaults based on the site type, but mark optional fields as null if truly ambiguous.

Respond with valid JSON matching the schema provided."""
        
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
            prompt = f"""You are an expert frontend developer who helps choose the right framework for web projects.

Analyze the following website requirements and recommend the most appropriate frontend framework:

Site Type: {requirements.site_type}
Key Features: {', '.join(requirements.key_features)}
Pages: {', '.join(requirements.pages) if requirements.pages else 'Not specified'}
Target Audience: {requirements.target_audience or 'Not specified'}
Design Style: {requirements.design_style or 'Not specified'}

Available frameworks:
1. vanilla - Plain HTML/CSS/JavaScript (best for simple static sites, landing pages, minimal interactivity)
2. react - React library (best for complex interactive UIs, SPAs, large applications, component reusability)
3. vue - Vue.js framework (best for progressive enhancement, moderate complexity, easy learning curve)
4. nextjs - Next.js framework (best for SEO-critical sites, server-side rendering, static generation, blogs, e-commerce)
5. svelte - Svelte framework (best for performance-critical apps, smaller bundle sizes, reactive programming)

Consider these factors:
- Site complexity: Simple sites work well with vanilla, complex apps need React/Vue/Svelte
- SEO requirements: Blogs, marketing sites, e-commerce benefit from Next.js SSR/SSG
- Interactivity: High interactivity needs React/Vue/Svelte
- Performance: Svelte and vanilla offer smallest bundle sizes
- Development speed: Vue and Next.js offer good developer experience
- Scalability: React and Next.js scale well for large applications

Recommend ONE framework that best fits these requirements. Provide a clear explanation of why this framework is the best choice.

Respond with JSON in this format:
{{
    "framework": "vanilla|react|vue|nextjs|svelte",
    "explanation": "Detailed explanation of why this framework is recommended",
    "confidence": 0.85
}}

The confidence should be between 0 and 1, where 1 means you're very confident this is the best choice."""

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
