"""
Design style definitions and prompt templates for code generation.

Provides design style specifications for Bold Minimalism, Brutalism,
Flat Minimalist, Anti-Design, Vibrant Blocks, Organic Fluid,
Retro/Nostalgic, and Experimental styles.
"""
from typing import Dict, List, Any
from pydantic import BaseModel, Field


class DesignStyle(BaseModel):
    """Design style definition."""
    name: str
    description: str
    color_palette: List[str]
    typography: Dict[str, str]
    spacing: str
    animations: str
    characteristics: List[str]
    tailwind_config: Dict[str, Any]
    prompt_additions: str


class DesignStyleLibrary:
    """Library of design styles."""
    
    def __init__(self):
        """Initialize design style library."""
        self.styles: Dict[str, DesignStyle] = {}
        self._load_styles()
    
    def _load_styles(self):
        """Load all design styles."""
        # Bold Minimalism
        self.styles["bold_minimalism"] = DesignStyle(
            name="Bold Minimalism",
            description="Clean layouts with striking typography and generous white space",
            color_palette=["gray-50", "gray-900", "blue-600", "white"],
            typography={
                "heading": "font-bold text-6xl md:text-7xl",
                "subheading": "font-semibold text-2xl md:text-3xl",
                "body": "font-normal text-lg"
            },
            spacing="generous padding and margins (py-20, px-8)",
            animations="subtle fade-ins and smooth transitions",
            characteristics=[
                "Minimal color palette with one accent color",
                "Large, bold typography",
                "Generous white space",
                "Clean geometric shapes",
                "High contrast",
                "Simple navigation"
            ],
            tailwind_config={
                "colors": {
                    "primary": "#2563eb",
                    "secondary": "#1e40af",
                    "accent": "#3b82f6"
                }
            },
            prompt_additions="""
**Bold Minimalism Style Guidelines:**
- Use a minimal color palette (mostly white/gray with one bold accent color)
- Implement large, bold typography for headings (text-6xl or larger)
- Add generous white space between sections (py-20 or more)
- Keep layouts clean and uncluttered
- Use simple geometric shapes
- Maintain high contrast for readability
- Add subtle fade-in animations on scroll
- Use simple, intuitive navigation
"""
        )
        
        # Brutalism/Neo-Brutalism
        self.styles["brutalism"] = DesignStyle(
            name="Brutalism/Neo-Brutalism",
            description="Raw elements with big blocks and bold fonts",
            color_palette=["black", "white", "yellow-400", "red-500"],
            typography={
                "heading": "font-black text-5xl md:text-6xl uppercase",
                "subheading": "font-bold text-xl md:text-2xl",
                "body": "font-mono text-base"
            },
            spacing="tight spacing with bold borders",
            animations="none or abrupt transitions",
            characteristics=[
                "Raw, unpolished aesthetic",
                "Bold, thick borders",
                "High contrast colors",
                "Monospace fonts",
                "Asymmetric layouts",
                "Visible grid structures"
            ],
            tailwind_config={
                "colors": {
                    "primary": "#000000",
                    "secondary": "#ffffff",
                    "accent": "#facc15"
                }
            },
            prompt_additions="""
**Brutalism Style Guidelines:**
- Use raw, unpolished aesthetic with bold borders (border-4 or border-8)
- Implement thick black borders around elements
- Use high contrast colors (black, white, bright accent colors)
- Add monospace fonts for body text
- Create asymmetric, unconventional layouts
- Show visible grid structures
- Avoid smooth animations (use instant transitions or none)
- Use uppercase text for headings
- Add overlapping elements for depth
"""
        )
        
        # Flat Minimalist
        self.styles["flat_minimalist"] = DesignStyle(
            name="Flat Minimalist",
            description="Highly functional interfaces emphasizing simplicity",
            color_palette=["gray-100", "gray-800", "blue-500", "green-500"],
            typography={
                "heading": "font-semibold text-4xl md:text-5xl",
                "subheading": "font-medium text-xl md:text-2xl",
                "body": "font-normal text-base"
            },
            spacing="consistent, moderate spacing",
            animations="smooth, functional transitions",
            characteristics=[
                "Flat design with no shadows",
                "Simple color palette",
                "Clear hierarchy",
                "Functional focus",
                "Clean icons",
                "Grid-based layouts"
            ],
            tailwind_config={
                "colors": {
                    "primary": "#3b82f6",
                    "secondary": "#10b981",
                    "accent": "#6366f1"
                }
            },
            prompt_additions="""
**Flat Minimalist Style Guidelines:**
- Use flat design with no shadows or gradients
- Implement simple, limited color palette
- Create clear visual hierarchy
- Focus on functionality and usability
- Use clean, simple icons
- Maintain grid-based layouts
- Add smooth, functional transitions
- Keep navigation simple and intuitive
- Use consistent spacing throughout
"""
        )
        
        # Anti-Design
        self.styles["anti_design"] = DesignStyle(
            name="Anti-Design",
            description="Asymmetric layouts with experimental typography",
            color_palette=["purple-600", "pink-500", "yellow-300", "black"],
            typography={
                "heading": "font-extrabold text-5xl md:text-7xl italic",
                "subheading": "font-bold text-2xl md:text-3xl",
                "body": "font-normal text-lg"
            },
            spacing="irregular, creative spacing",
            animations="unexpected, creative animations",
            characteristics=[
                "Asymmetric layouts",
                "Experimental typography",
                "Overlapping elements",
                "Creative imperfections",
                "Unconventional navigation",
                "Bold color combinations"
            ],
            tailwind_config={
                "colors": {
                    "primary": "#9333ea",
                    "secondary": "#ec4899",
                    "accent": "#fde047"
                }
            },
            prompt_additions="""
**Anti-Design Style Guidelines:**
- Create asymmetric, unconventional layouts
- Use experimental typography (mix fonts, sizes, styles)
- Add overlapping elements and layers
- Implement creative imperfections intentionally
- Use unconventional navigation patterns
- Combine bold, contrasting colors
- Add unexpected animations and interactions
- Break traditional design rules purposefully
- Create visual tension and interest
"""
        )
        
        # Vibrant Blocks
        self.styles["vibrant_blocks"] = DesignStyle(
            name="Vibrant Blocks",
            description="Big blocks with vivid contrasts and vibrant colors",
            color_palette=["red-500", "blue-600", "yellow-400", "green-500", "purple-600"],
            typography={
                "heading": "font-bold text-5xl md:text-6xl",
                "subheading": "font-semibold text-2xl md:text-3xl",
                "body": "font-medium text-lg"
            },
            spacing="large blocks with clear separation",
            animations="bold, energetic transitions",
            characteristics=[
                "Large color blocks",
                "Vivid, contrasting colors",
                "Bold typography",
                "Clear section separation",
                "Energetic feel",
                "Grid-based layouts"
            ],
            tailwind_config={
                "colors": {
                    "primary": "#ef4444",
                    "secondary": "#2563eb",
                    "accent": "#facc15"
                }
            },
            prompt_additions="""
**Vibrant Blocks Style Guidelines:**
- Use large, bold color blocks for sections
- Implement vivid, high-contrast color combinations
- Create clear separation between sections
- Use bold, impactful typography
- Add energetic, bold transitions
- Maintain grid-based layouts with large blocks
- Use multiple vibrant colors throughout
- Create an energetic, dynamic feel
- Add hover effects with color changes
"""
        )
        
        # Organic Fluid
        self.styles["organic_fluid"] = DesignStyle(
            name="Organic Fluid",
            description="Organic, fluid shapes for intuitive navigation",
            color_palette=["teal-400", "blue-300", "purple-400", "pink-300"],
            typography={
                "heading": "font-semibold text-5xl md:text-6xl",
                "subheading": "font-medium text-2xl md:text-3xl",
                "body": "font-normal text-lg"
            },
            spacing="flowing, natural spacing",
            animations="smooth, flowing transitions",
            characteristics=[
                "Curved, organic shapes",
                "Fluid layouts",
                "Soft color gradients",
                "Natural flow",
                "Smooth animations",
                "Asymmetric balance"
            ],
            tailwind_config={
                "colors": {
                    "primary": "#2dd4bf",
                    "secondary": "#93c5fd",
                    "accent": "#c084fc"
                }
            },
            prompt_additions="""
**Organic Fluid Style Guidelines:**
- Use curved, organic shapes (rounded-3xl or custom SVG shapes)
- Implement fluid, flowing layouts
- Add soft color gradients
- Create natural, intuitive flow
- Use smooth, flowing animations
- Maintain asymmetric balance
- Add blob shapes and curved elements
- Use soft shadows for depth
- Create a calming, natural aesthetic
"""
        )
        
        # Retro/Nostalgic
        self.styles["retro_nostalgic"] = DesignStyle(
            name="Retro/Nostalgic",
            description="Retro elements with playful geometric shapes",
            color_palette=["orange-400", "yellow-300", "pink-400", "teal-500"],
            typography={
                "heading": "font-bold text-5xl md:text-6xl",
                "subheading": "font-semibold text-2xl md:text-3xl",
                "body": "font-normal text-lg"
            },
            spacing="playful, varied spacing",
            animations="bouncy, playful transitions",
            characteristics=[
                "Retro color palettes",
                "Geometric shapes",
                "Playful elements",
                "Vintage typography",
                "Nostalgic feel",
                "Fun patterns"
            ],
            tailwind_config={
                "colors": {
                    "primary": "#fb923c",
                    "secondary": "#fde047",
                    "accent": "#f472b6"
                }
            },
            prompt_additions="""
**Retro/Nostalgic Style Guidelines:**
- Use retro color palettes (warm oranges, yellows, pinks)
- Add playful geometric shapes and patterns
- Implement vintage-inspired typography
- Create a nostalgic, fun atmosphere
- Use patterns and textures
- Add bouncy, playful animations
- Include retro design elements (circles, stripes, dots)
- Use warm, inviting colors
- Create a friendly, approachable feel
"""
        )
        
        # Experimental
        self.styles["experimental"] = DesignStyle(
            name="Experimental",
            description="Experimental navigation with dynamic typography",
            color_palette=["indigo-600", "violet-500", "fuchsia-500", "cyan-400"],
            typography={
                "heading": "font-black text-6xl md:text-8xl",
                "subheading": "font-bold text-3xl md:text-4xl",
                "body": "font-medium text-lg"
            },
            spacing="dynamic, unconventional spacing",
            animations="complex, creative animations",
            characteristics=[
                "Experimental navigation",
                "Dynamic typography",
                "Non-traditional scrolling",
                "Interactive elements",
                "Cutting-edge design",
                "Unique interactions"
            ],
            tailwind_config={
                "colors": {
                    "primary": "#4f46e5",
                    "secondary": "#8b5cf6",
                    "accent": "#22d3ee"
                }
            },
            prompt_additions="""
**Experimental Style Guidelines:**
- Create experimental, non-traditional navigation
- Use dynamic, animated typography
- Implement non-traditional scrolling effects
- Add highly interactive elements
- Use cutting-edge design techniques
- Create unique, memorable interactions
- Add complex animations and transitions
- Break conventional design patterns
- Push creative boundaries
- Use bold, futuristic color combinations
"""
        )
    
    def get_style(self, style_name: str) -> DesignStyle:
        """
        Get design style by name.
        
        Args:
            style_name: Name of the design style
            
        Returns:
            DesignStyle object or default style
        """
        style_key = style_name.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        return self.styles.get(style_key, self.styles["bold_minimalism"])
    
    def list_styles(self) -> List[str]:
        """List all available design style names."""
        return [style.name for style in self.styles.values()]
    
    def get_style_prompt_addition(self, style_name: str) -> str:
        """Get prompt additions for a specific design style."""
        style = self.get_style(style_name)
        return style.prompt_additions
    
    def get_tailwind_config(self, style_name: str) -> Dict[str, Any]:
        """Get Tailwind configuration for a specific design style."""
        style = self.get_style(style_name)
        return style.tailwind_config


# Global design style library instance
design_style_library = DesignStyleLibrary()
