"""
Template library for code generation.

Provides pre-built templates for common website types that can be
customized based on user requirements.
"""
from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from jinja2 import Template


class SiteTemplate(BaseModel):
    """Template definition for a website type."""
    name: str
    site_type: str
    description: str
    template_content: str
    default_features: List[str] = Field(default_factory=list)
    customization_points: List[str] = Field(default_factory=list)


class TemplateLibrary:
    """Library of website templates."""
    
    def __init__(self):
        """Initialize template library."""
        self.templates: Dict[str, SiteTemplate] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all available templates."""
        # Portfolio template
        self.templates["portfolio"] = SiteTemplate(
            name="portfolio",
            site_type="portfolio",
            description="Professional portfolio website template",
            template_content=self._get_portfolio_template(),
            default_features=["about section", "projects gallery", "contact form", "skills showcase"],
            customization_points=["color_scheme", "hero_text", "projects", "skills", "contact_info"]
        )
        
        # Blog template
        self.templates["blog"] = SiteTemplate(
            name="blog",
            site_type="blog",
            description="Clean blog website template",
            template_content=self._get_blog_template(),
            default_features=["blog posts", "categories", "search", "author bio"],
            customization_points=["color_scheme", "blog_title", "posts", "categories", "author_info"]
        )
        
        # Landing page template
        self.templates["landing"] = SiteTemplate(
            name="landing",
            site_type="landing page",
            description="High-conversion landing page template",
            template_content=self._get_landing_template(),
            default_features=["hero section", "features", "testimonials", "CTA buttons"],
            customization_points=["color_scheme", "hero_text", "features", "testimonials", "cta_text"]
        )
        
        # Contact form template
        self.templates["contact"] = SiteTemplate(
            name="contact",
            site_type="contact form",
            description="Simple contact form page template",
            template_content=self._get_contact_template(),
            default_features=["contact form", "location map", "contact info"],
            customization_points=["color_scheme", "company_name", "contact_info", "form_fields"]
        )
    
    def get_template(self, site_type: str) -> Optional[SiteTemplate]:
        """
        Get template by site type.
        
        Args:
            site_type: Type of site (e.g., "portfolio", "blog")
            
        Returns:
            SiteTemplate if found, None otherwise
        """
        # Normalize site type
        site_type_lower = site_type.lower().strip()
        
        # Direct match
        if site_type_lower in self.templates:
            return self.templates[site_type_lower]
        
        # Fuzzy match
        for key, template in self.templates.items():
            if key in site_type_lower or site_type_lower in key:
                return template
        
        return None
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())
    
    def customize_template(
        self,
        template: SiteTemplate,
        customizations: Dict[str, any]
    ) -> str:
        """
        Customize a template with user-specific values.
        
        Args:
            template: Template to customize
            customizations: Dictionary of customization values
            
        Returns:
            Customized template content
        """
        try:
            jinja_template = Template(template.template_content)
            return jinja_template.render(**customizations)
        except Exception as e:
            # If Jinja rendering fails, return original template
            return template.template_content
    
    def _get_portfolio_template(self) -> str:
        """Get portfolio template with Jinja2 placeholders."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{ description | default('Professional portfolio showcasing my work and skills') }}">
    <title>{{ site_title | default('My Portfolio') }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-{{ bg_color | default('gray-50') }} text-{{ text_color | default('gray-900') }}">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg fixed w-full z-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between h-16">
                <div class="flex items-center">
                    <span class="text-2xl font-bold text-{{ accent_color | default('blue-600') }}">{{ name | default('Your Name') }}</span>
                </div>
                <div class="hidden md:flex items-center space-x-8">
                    <a href="#about" class="text-gray-700 hover:text-{{ accent_color | default('blue-600') }} transition">About</a>
                    <a href="#projects" class="text-gray-700 hover:text-{{ accent_color | default('blue-600') }} transition">Projects</a>
                    <a href="#skills" class="text-gray-700 hover:text-{{ accent_color | default('blue-600') }} transition">Skills</a>
                    <a href="#contact" class="text-gray-700 hover:text-{{ accent_color | default('blue-600') }} transition">Contact</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="pt-32 pb-20 px-4">
        <div class="max-w-7xl mx-auto text-center">
            <h1 class="text-5xl md:text-6xl font-bold mb-6">{{ hero_title | default('Hi, I\'m a Creative Professional') }}</h1>
            <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">{{ hero_subtitle | default('I create beautiful and functional digital experiences') }}</p>
            <a href="#contact" class="bg-{{ accent_color | default('blue-600') }} text-white px-8 py-3 rounded-lg hover:bg-{{ accent_color | default('blue-700') }} transition">Get In Touch</a>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-20 px-4 bg-white">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-4xl font-bold mb-8 text-center">About Me</h2>
            <div class="max-w-3xl mx-auto text-lg text-gray-700 leading-relaxed">
                <p>{{ about_text | default('I am a passionate professional with expertise in creating innovative solutions. With years of experience, I bring creativity and technical skills to every project.') }}</p>
            </div>
        </div>
    </section>

    <!-- Projects Section -->
    <section id="projects" class="py-20 px-4">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-4xl font-bold mb-12 text-center">My Projects</h2>
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                {% for project in projects | default([
                    {'title': 'Project 1', 'description': 'A showcase of innovative design and functionality', 'image': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=400'},
                    {'title': 'Project 2', 'description': 'Creative solution for modern challenges', 'image': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=400'},
                    {'title': 'Project 3', 'description': 'Elegant and user-friendly application', 'image': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=400'}
                ]) %}
                <div class="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition">
                    <img src="{{ project.image }}" alt="{{ project.title }}" class="w-full h-48 object-cover">
                    <div class="p-6">
                        <h3 class="text-xl font-bold mb-2">{{ project.title }}</h3>
                        <p class="text-gray-600">{{ project.description }}</p>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- Skills Section -->
    <section id="skills" class="py-20 px-4 bg-white">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-4xl font-bold mb-12 text-center">Skills</h2>
            <div class="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
                {% for skill in skills | default(['Web Development', 'UI/UX Design', 'Project Management', 'Creative Problem Solving', 'Team Collaboration', 'Agile Methodologies']) %}
                <div class="bg-{{ accent_color | default('blue-50') }} p-6 rounded-lg text-center">
                    <p class="font-semibold text-lg">{{ skill }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="py-20 px-4">
        <div class="max-w-3xl mx-auto">
            <h2 class="text-4xl font-bold mb-12 text-center">Get In Touch</h2>
            <form class="space-y-6">
                <div>
                    <label class="block text-sm font-medium mb-2">Name</label>
                    <input type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-{{ accent_color | default('blue-600') }} focus:border-transparent" required>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">Email</label>
                    <input type="email" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-{{ accent_color | default('blue-600') }} focus:border-transparent" required>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">Message</label>
                    <textarea rows="5" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-{{ accent_color | default('blue-600') }} focus:border-transparent" required></textarea>
                </div>
                <button type="submit" class="w-full bg-{{ accent_color | default('blue-600') }} text-white py-3 rounded-lg hover:bg-{{ accent_color | default('blue-700') }} transition">Send Message</button>
            </form>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-8 px-4">
        <div class="max-w-7xl mx-auto text-center">
            <p>&copy; 2024 {{ name | default('Your Name') }}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _get_blog_template(self) -> str:
        """Get blog template with Jinja2 placeholders."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{ description | default('A blog about interesting topics and insights') }}">
    <title>{{ blog_title | default('My Blog') }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <h1 class="text-3xl font-bold text-{{ accent_color | default('indigo-600') }}">{{ blog_title | default('My Blog') }}</h1>
            <p class="text-gray-600 mt-2">{{ tagline | default('Thoughts, stories, and ideas') }}</p>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="grid lg:grid-cols-3 gap-8">
            <!-- Blog Posts -->
            <div class="lg:col-span-2 space-y-8">
                {% for post in posts | default([
                    {'title': 'Getting Started with Web Development', 'excerpt': 'Learn the fundamentals of building modern websites', 'date': '2024-01-15', 'category': 'Tutorial', 'image': 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=600'},
                    {'title': 'Design Principles for Better UX', 'excerpt': 'Explore key principles that make user experiences exceptional', 'date': '2024-01-10', 'category': 'Design', 'image': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=600'},
                    {'title': 'The Future of Technology', 'excerpt': 'Insights into emerging trends and innovations', 'date': '2024-01-05', 'category': 'Technology', 'image': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=600'}
                ]) %}
                <article class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition">
                    <img src="{{ post.image }}" alt="{{ post.title }}" class="w-full h-64 object-cover">
                    <div class="p-6">
                        <div class="flex items-center text-sm text-gray-500 mb-3">
                            <span class="bg-{{ accent_color | default('indigo-100') }} text-{{ accent_color | default('indigo-800') }} px-3 py-1 rounded-full mr-3">{{ post.category }}</span>
                            <span>{{ post.date }}</span>
                        </div>
                        <h2 class="text-2xl font-bold mb-3 hover:text-{{ accent_color | default('indigo-600') }} cursor-pointer">{{ post.title }}</h2>
                        <p class="text-gray-600 mb-4">{{ post.excerpt }}</p>
                        <a href="#" class="text-{{ accent_color | default('indigo-600') }} font-semibold hover:underline">Read More →</a>
                    </div>
                </article>
                {% endfor %}
            </div>

            <!-- Sidebar -->
            <aside class="space-y-8">
                <!-- About -->
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-xl font-bold mb-4">About</h3>
                    <p class="text-gray-600">{{ about_text | default('Welcome to my blog where I share insights, tutorials, and thoughts on various topics.') }}</p>
                </div>

                <!-- Categories -->
                <div class="bg-white rounded-lg shadow-md p-6">
                    <h3 class="text-xl font-bold mb-4">Categories</h3>
                    <ul class="space-y-2">
                        {% for category in categories | default(['Tutorial', 'Design', 'Technology', 'Lifestyle']) %}
                        <li><a href="#" class="text-gray-600 hover:text-{{ accent_color | default('indigo-600') }} transition">{{ category }}</a></li>
                        {% endfor %}
                    </ul>
                </div>
            </aside>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-8 px-4 mt-12">
        <div class="max-w-7xl mx-auto text-center">
            <p>&copy; 2024 {{ blog_title | default('My Blog') }}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _get_landing_template(self) -> str:
        """Get landing page template with Jinja2 placeholders."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{ description | default('Transform your business with our innovative solution') }}">
    <title>{{ page_title | default('Welcome') }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-white">
    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-{{ accent_color | default('purple-600') }} to-{{ secondary_color | default('blue-600') }} text-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
            <div class="text-center">
                <h1 class="text-5xl md:text-6xl font-bold mb-6">{{ hero_title | default('Transform Your Business Today') }}</h1>
                <p class="text-xl md:text-2xl mb-8 max-w-3xl mx-auto">{{ hero_subtitle | default('Discover the power of innovation and take your success to the next level') }}</p>
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <a href="#" class="bg-white text-{{ accent_color | default('purple-600') }} px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition">{{ cta_primary | default('Get Started') }}</a>
                    <a href="#" class="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-{{ accent_color | default('purple-600') }} transition">{{ cta_secondary | default('Learn More') }}</a>
                </div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section class="py-20 px-4">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-4xl font-bold text-center mb-12">Why Choose Us</h2>
            <div class="grid md:grid-cols-3 gap-8">
                {% for feature in features | default([
                    {'title': 'Fast & Reliable', 'description': 'Lightning-fast performance you can count on', 'icon': '⚡'},
                    {'title': 'Easy to Use', 'description': 'Intuitive interface designed for everyone', 'icon': '✨'},
                    {'title': '24/7 Support', 'description': 'Always here when you need us', 'icon': '🛟'}
                ]) %}
                <div class="text-center p-6">
                    <div class="text-5xl mb-4">{{ feature.icon }}</div>
                    <h3 class="text-xl font-bold mb-3">{{ feature.title }}</h3>
                    <p class="text-gray-600">{{ feature.description }}</p>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- Testimonials Section -->
    <section class="py-20 px-4 bg-gray-50">
        <div class="max-w-7xl mx-auto">
            <h2 class="text-4xl font-bold text-center mb-12">What Our Customers Say</h2>
            <div class="grid md:grid-cols-3 gap-8">
                {% for testimonial in testimonials | default([
                    {'name': 'Sarah Johnson', 'role': 'CEO, TechCorp', 'text': 'This solution transformed our business operations completely!', 'rating': 5},
                    {'name': 'Michael Chen', 'role': 'Founder, StartupXYZ', 'text': 'Incredible results in just a few weeks. Highly recommended!', 'rating': 5},
                    {'name': 'Emily Davis', 'role': 'Director, Innovation Inc', 'text': 'The best investment we made this year. Outstanding!', 'rating': 5}
                ]) %}
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <div class="flex mb-4">
                        {% for i in range(testimonial.rating) %}
                        <span class="text-yellow-400">★</span>
                        {% endfor %}
                    </div>
                    <p class="text-gray-700 mb-4">"{{ testimonial.text }}"</p>
                    <div class="font-semibold">{{ testimonial.name }}</div>
                    <div class="text-sm text-gray-500">{{ testimonial.role }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20 px-4 bg-{{ accent_color | default('purple-600') }} text-white">
        <div class="max-w-4xl mx-auto text-center">
            <h2 class="text-4xl font-bold mb-6">{{ cta_title | default('Ready to Get Started?') }}</h2>
            <p class="text-xl mb-8">{{ cta_text | default('Join thousands of satisfied customers today') }}</p>
            <a href="#" class="bg-white text-{{ accent_color | default('purple-600') }} px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition inline-block">{{ cta_button | default('Start Your Free Trial') }}</a>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-8 px-4">
        <div class="max-w-7xl mx-auto text-center">
            <p>&copy; 2024 {{ company_name | default('Your Company') }}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""
    
    def _get_contact_template(self) -> str:
        """Get contact form template with Jinja2 placeholders."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{{ description | default('Get in touch with us') }}">
    <title>{{ page_title | default('Contact Us') }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <h1 class="text-3xl font-bold text-{{ accent_color | default('blue-600') }}">{{ company_name | default('Company Name') }}</h1>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="text-center mb-12">
            <h2 class="text-4xl font-bold mb-4">{{ heading | default('Get In Touch') }}</h2>
            <p class="text-xl text-gray-600">{{ subheading | default('We\'d love to hear from you') }}</p>
        </div>

        <div class="grid lg:grid-cols-2 gap-12">
            <!-- Contact Form -->
            <div class="bg-white rounded-lg shadow-md p-8">
                <h3 class="text-2xl font-bold mb-6">Send us a message</h3>
                <form class="space-y-6">
                    <div>
                        <label class="block text-sm font-medium mb-2">Name</label>
                        <input type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-{{ accent_color | default('blue-600') }} focus:border-transparent" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-2">Email</label>
                        <input type="email" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-{{ accent_color | default('blue-600') }} focus:border-transparent" required>
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-2">Phone</label>
                        <input type="tel" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-{{ accent_color | default('blue-600') }} focus:border-transparent">
                    </div>
                    <div>
                        <label class="block text-sm font-medium mb-2">Message</label>
                        <textarea rows="5" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-{{ accent_color | default('blue-600') }} focus:border-transparent" required></textarea>
                    </div>
                    <button type="submit" class="w-full bg-{{ accent_color | default('blue-600') }} text-white py-3 rounded-lg hover:bg-{{ accent_color | default('blue-700') }} transition font-semibold">Send Message</button>
                </form>
            </div>

            <!-- Contact Information -->
            <div class="space-y-8">
                <div class="bg-white rounded-lg shadow-md p-8">
                    <h3 class="text-2xl font-bold mb-6">Contact Information</h3>
                    <div class="space-y-4">
                        <div class="flex items-start">
                            <span class="text-2xl mr-4">📍</span>
                            <div>
                                <div class="font-semibold">Address</div>
                                <div class="text-gray-600">{{ address | default('123 Main Street, City, State 12345') }}</div>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <span class="text-2xl mr-4">📧</span>
                            <div>
                                <div class="font-semibold">Email</div>
                                <div class="text-gray-600">{{ email | default('contact@example.com') }}</div>
                            </div>
                        </div>
                        <div class="flex items-start">
                            <span class="text-2xl mr-4">📞</span>
                            <div>
                                <div class="font-semibold">Phone</div>
                                <div class="text-gray-600">{{ phone | default('(555) 123-4567') }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="bg-white rounded-lg shadow-md p-8">
                    <h3 class="text-2xl font-bold mb-6">Business Hours</h3>
                    <div class="space-y-2 text-gray-600">
                        {% for day, hours in business_hours | default([
                            ('Monday - Friday', '9:00 AM - 6:00 PM'),
                            ('Saturday', '10:00 AM - 4:00 PM'),
                            ('Sunday', 'Closed')
                        ]) %}
                        <div class="flex justify-between">
                            <span class="font-semibold">{{ day }}</span>
                            <span>{{ hours }}</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-8 px-4 mt-12">
        <div class="max-w-7xl mx-auto text-center">
            <p>&copy; 2024 {{ company_name | default('Company Name') }}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""


# Global template library instance
template_library = TemplateLibrary()
