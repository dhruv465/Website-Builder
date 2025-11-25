"""
Template data structure and starter templates for the AI Website Builder.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

class Template:
    """Template data structure."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        category: str,
        tags: List[str],
        thumbnail_url: str,
        preview_url: Optional[str],
        html_code: str,
        css_code: str,
        js_code: str,
        framework: str = "html",
        design_style: str = "modern",
        features: List[str] = None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.tags = tags
        self.thumbnail_url = thumbnail_url
        self.preview_url = preview_url
        self.html_code = html_code
        self.css_code = css_code
        self.js_code = js_code
        self.framework = framework
        self.design_style = design_style
        self.features = features or []
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "thumbnail_url": self.thumbnail_url,
            "preview_url": self.preview_url,
            "html_code": self.html_code,
            "css_code": self.css_code,
            "js_code": self.js_code,
            "framework": self.framework,
            "design_style": self.design_style,
            "features": self.features,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Template Categories
CATEGORIES = [
    "portfolio",
    "business",
    "blog",
    "landing-page",
    "e-commerce",
    "restaurant",
    "agency",
    "personal",
    "saas",
    "education",
]


# Starter Templates
STARTER_TEMPLATES = [
    # 1. Portfolio - Photographer
    Template(
        id="portfolio-photographer",
        name="Photographer Portfolio",
        description="A stunning portfolio template for photographers with a full-screen image gallery and elegant typography.",
        category="portfolio",
        tags=["photography", "creative", "gallery", "minimalist"],
        thumbnail_url="/templates/thumbnails/portfolio-photographer.jpg",
        preview_url=None,
        framework="html",
        design_style="bold_minimalism",
        features=["hero-section", "image-gallery", "about-section", "contact-form"],
        html_code="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jane Doe - Photographer</title>
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">JANE DOE</div>
        <ul class="nav-menu">
            <li><a href="#work">Work</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>

    <section class="hero">
        <div class="hero-content">
            <h1 class="hero-title">Capturing Moments</h1>
            <p class="hero-subtitle">Professional Photography & Visual Storytelling</p>
        </div>
    </section>

    <section id="work" class="gallery">
        <div class="gallery-grid">
            <div class="gallery-item"><img src="https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=800" alt="Photo 1"></div>
            <div class="gallery-item"><img src="https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=800" alt="Photo 2"></div>
            <div class="gallery-item"><img src="https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800" alt="Photo 3"></div>
            <div class="gallery-item"><img src="https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=800" alt="Photo 4"></div>
            <div class="gallery-item"><img src="https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800" alt="Photo 5"></div>
            <div class="gallery-item"><img src="https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800" alt="Photo 6"></div>
        </div>
    </section>

    <section id="about" class="about">
        <div class="about-content">
            <h2>About Me</h2>
            <p>I'm a passionate photographer based in San Francisco, specializing in landscape and portrait photography. With over 10 years of experience, I capture the beauty of the world through my lens.</p>
        </div>
    </section>

    <section id="contact" class="contact">
        <div class="contact-content">
            <h2>Get In Touch</h2>
            <form class="contact-form">
                <input type="text" placeholder="Your Name" required>
                <input type="email" placeholder="Your Email" required>
                <textarea placeholder="Your Message" rows="5" required></textarea>
                <button type="submit">Send Message</button>
            </form>
        </div>
    </section>

    <footer class="footer">
        <p>&copy; 2024 Jane Doe Photography. All rights reserved.</p>
    </footer>
</body>
</html>
        """,
        css_code="""
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
    color: #1a1a1a;
}

.navbar {
    position: fixed;
    top: 0;
    width: 100%;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 1.5rem 5%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1000;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.nav-brand {
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 2px;
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-menu a {
    text-decoration: none;
    color: #1a1a1a;
    font-weight: 500;
    transition: opacity 0.3s;
}

.nav-menu a:hover {
    opacity: 0.6;
}

.hero {
    height: 100vh;
    background: linear-gradient(rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)),
                url('https://images.unsplash.com/photo-1452587925148-ce544e77e70d?w=1920') center/cover;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: white;
}

.hero-title {
    font-size: 4rem;
    font-weight: 700;
    margin-bottom: 1rem;
    letter-spacing: -1px;
}

.hero-subtitle {
    font-size: 1.5rem;
    font-weight: 300;
    letter-spacing: 1px;
}

.gallery {
    padding: 5rem 5%;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
}

.gallery-item {
    aspect-ratio: 4/3;
    overflow: hidden;
    border-radius: 8px;
}

.gallery-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s;
}

.gallery-item:hover img {
    transform: scale(1.05);
}

.about {
    padding: 5rem 5%;
    background: #f8f8f8;
}

.about-content {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
}

.about-content h2 {
    font-size: 2.5rem;
    margin-bottom: 2rem;
}

.about-content p {
    font-size: 1.2rem;
    line-height: 1.8;
    color: #666;
}

.contact {
    padding: 5rem 5%;
}

.contact-content {
    max-width: 600px;
    margin: 0 auto;
}

.contact-content h2 {
    font-size: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
}

.contact-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.contact-form input,
.contact-form textarea {
    padding: 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.3s;
}

.contact-form input:focus,
.contact-form textarea:focus {
    outline: none;
    border-color: #1a1a1a;
}

.contact-form button {
    padding: 1rem 2rem;
    background: #1a1a1a;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.3s;
}

.contact-form button:hover {
    background: #333;
}

.footer {
    padding: 2rem 5%;
    background: #1a1a1a;
    color: white;
    text-align: center;
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
    }
    
    .gallery-grid {
        grid-template-columns: 1fr;
    }
    
    .nav-menu {
        gap: 1rem;
    }
}
        """,
        js_code="""
// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form submission handler
document.querySelector('.contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Thank you for your message! I will get back to you soon.');
    this.reset();
});

// Navbar scroll effect
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        navbar.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
    } else {
        navbar.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
});
        """,
    ),
    
    # 2. Business - Agency
    Template(
        id="business-agency",
        name="Creative Agency",
        description="A modern business template for creative agencies with bold typography and dynamic sections.",
        category="business",
        tags=["agency", "corporate", "modern", "services"],
        thumbnail_url="/templates/thumbnails/business-agency.jpg",
        preview_url=None,
        framework="html",
        design_style="vibrant_blocks",
        features=["hero-section", "services", "portfolio", "team", "contact-form"],
        html_code="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Creative Studio - Digital Agency</title>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <div class="nav-brand">CREATIVE</div>
            <ul class="nav-menu">
                <li><a href="#services">Services</a></li>
                <li><a href="#work">Work</a></li>
                <li><a href="#team">Team</a></li>
                <li><a href="#contact" class="btn-primary">Contact</a></li>
            </ul>
        </div>
    </nav>

    <section class="hero">
        <div class="container">
            <h1 class="hero-title">We Create<br>Digital Experiences</h1>
            <p class="hero-subtitle">A full-service creative agency specializing in branding, web design, and digital marketing.</p>
            <a href="#contact" class="btn-large">Start a Project</a>
        </div>
    </section>

    <section id="services" class="services">
        <div class="container">
            <h2 class="section-title">Our Services</h2>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-icon">🎨</div>
                    <h3>Brand Identity</h3>
                    <p>Creating memorable brands that stand out in the market.</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">💻</div>
                    <h3>Web Design</h3>
                    <p>Beautiful, responsive websites that convert visitors into customers.</p>
                </div>
                <div class="service-card">
                    <div class="service-icon">📱</div>
                    <h3>Digital Marketing</h3>
                    <p>Data-driven strategies to grow your online presence.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="work" class="work">
        <div class="container">
            <h2 class="section-title">Featured Work</h2>
            <div class="work-grid">
                <div class="work-item">
                    <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800" alt="Project 1">
                    <div class="work-overlay">
                        <h3>Brand Redesign</h3>
                        <p>Tech Startup</p>
                    </div>
                </div>
                <div class="work-item">
                    <img src="https://images.unsplash.com/photo-1551650975-87deedd944c3?w=800" alt="Project 2">
                    <div class="work-overlay">
                        <h3>E-commerce Platform</h3>
                        <p>Fashion Retailer</p>
                    </div>
                </div>
                <div class="work-item">
                    <img src="https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800" alt="Project 3">
                    <div class="work-overlay">
                        <h3>Mobile App Design</h3>
                        <p>Fitness Company</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="contact" class="contact">
        <div class="container">
            <h2 class="section-title">Let's Work Together</h2>
            <form class="contact-form">
                <div class="form-row">
                    <input type="text" placeholder="Name" required>
                    <input type="email" placeholder="Email" required>
                </div>
                <input type="text" placeholder="Company">
                <textarea placeholder="Tell us about your project" rows="5" required></textarea>
                <button type="submit" class="btn-large">Send Message</button>
            </form>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 Creative Studio. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
        """,
        css_code="""
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
    color: #1a1a1a;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}

.navbar {
    position: fixed;
    top: 0;
    width: 100%;
    background: white;
    padding: 1.5rem 0;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand {
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -1px;
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 2rem;
    align-items: center;
}

.nav-menu a {
    text-decoration: none;
    color: #1a1a1a;
    font-weight: 500;
    transition: color 0.3s;
}

.nav-menu a:hover {
    color: #6366f1;
}

.btn-primary {
    background: #6366f1;
    color: white !important;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
}

.btn-large {
    display: inline-block;
    background: #6366f1;
    color: white;
    padding: 1rem 2.5rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    transition: transform 0.3s, box-shadow 0.3s;
}

.btn-large:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
}

.hero {
    padding: 12rem 0 8rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
}

.hero-title {
    font-size: 4.5rem;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 1.5rem;
    letter-spacing: -2px;
}

.hero-subtitle {
    font-size: 1.3rem;
    margin-bottom: 2.5rem;
    opacity: 0.9;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.section-title {
    font-size: 3rem;
    font-weight: 800;
    text-align: center;
    margin-bottom: 4rem;
    letter-spacing: -1px;
}

.services {
    padding: 8rem 0;
}

.services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 3rem;
}

.service-card {
    padding: 3rem 2rem;
    background: #f8f9fa;
    border-radius: 16px;
    text-align: center;
    transition: transform 0.3s, box-shadow 0.3s;
}

.service-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.service-icon {
    font-size: 3rem;
    margin-bottom: 1.5rem;
}

.service-card h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
}

.service-card p {
    color: #666;
    line-height: 1.8;
}

.work {
    padding: 8rem 0;
    background: #f8f9fa;
}

.work-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
}

.work-item {
    position: relative;
    aspect-ratio: 4/3;
    border-radius: 16px;
    overflow: hidden;
    cursor: pointer;
}

.work-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s;
}

.work-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
    color: white;
    padding: 2rem;
    transform: translateY(100%);
    transition: transform 0.3s;
}

.work-item:hover img {
    transform: scale(1.1);
}

.work-item:hover .work-overlay {
    transform: translateY(0);
}

.contact {
    padding: 8rem 0;
}

.contact-form {
    max-width: 600px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}

.contact-form input,
.contact-form textarea {
    padding: 1rem;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.3s;
}

.contact-form input:focus,
.contact-form textarea:focus {
    outline: none;
    border-color: #6366f1;
}

.contact-form button {
    width: 100%;
}

.footer {
    padding: 3rem 0;
    background: #1a1a1a;
    color: white;
    text-align: center;
}

@media (max-width: 768px) {
    .hero-title {
        font-size: 2.5rem;
    }
    
    .section-title {
        font-size: 2rem;
    }
    
    .form-row {
        grid-template-columns: 1fr;
    }
    
    .nav-menu {
        gap: 1rem;
    }
}
        """,
        js_code="""
// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form submission
document.querySelector('.contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Thank you! We will get back to you soon.');
    this.reset();
});

// Scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

document.querySelectorAll('.service-card, .work-item').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s, transform 0.6s';
    observer.observe(el);
});
        """,
    ),
]


def get_all_templates() -> List[Template]:
    """Get all available templates."""
    return STARTER_TEMPLATES


def get_template_by_id(template_id: str) -> Optional[Template]:
    """Get a template by ID."""
    for template in STARTER_TEMPLATES:
        if template.id == template_id:
            return template
    return None


def get_templates_by_category(category: str) -> List[Template]:
    """Get templates by category."""
    return [t for t in STARTER_TEMPLATES if t.category == category]


def search_templates(query: str) -> List[Template]:
    """Search templates by name, description, or tags."""
    query = query.lower()
    results = []
    for template in STARTER_TEMPLATES:
        if (query in template.name.lower() or
            query in template.description.lower() or
            any(query in tag.lower() for tag in template.tags)):
            results.append(template)
    return results
