"""
Auto-fix service for automatically fixing common audit issues.
"""
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup, Tag
import re


class AutoFixService:
    """Service for automatically fixing common audit issues."""
    
    def __init__(self):
        self.fixes_applied = []
    
    def fix_all(self, html_code: str, issues: List[Dict]) -> Tuple[str, List[Dict]]:
        """
        Apply all possible auto-fixes to HTML code.
        
        Args:
            html_code: Original HTML code
            issues: List of audit issues
            
        Returns:
            Tuple of (fixed_html, list_of_fixes_applied)
        """
        self.fixes_applied = []
        soup = BeautifulSoup(html_code, 'html.parser')
        
        for issue in issues:
            if issue.get('auto_fixable', False):
                self._apply_fix(soup, issue)
        
        return str(soup), self.fixes_applied
    
    def _apply_fix(self, soup: BeautifulSoup, issue: Dict):
        """Apply a specific fix based on issue type."""
        issue_type = issue.get('type', '')
        
        if issue_type == 'missing_meta_description':
            self._fix_missing_meta_description(soup)
        elif issue_type == 'missing_title':
            self._fix_missing_title(soup)
        elif issue_type == 'missing_alt_text':
            self._fix_missing_alt_text(soup, issue.get('location'))
        elif issue_type == 'missing_lang_attribute':
            self._fix_missing_lang_attribute(soup)
        elif issue_type == 'missing_viewport':
            self._fix_missing_viewport(soup)
        elif issue_type == 'missing_charset':
            self._fix_missing_charset(soup)
        elif issue_type == 'heading_hierarchy':
            self._fix_heading_hierarchy(soup)
        elif issue_type == 'missing_aria_labels':
            self._fix_missing_aria_labels(soup)
        elif issue_type == 'missing_form_labels':
            self._fix_missing_form_labels(soup)
        elif issue_type == 'image_lazy_loading':
            self._fix_image_lazy_loading(soup)
    
    def _fix_missing_meta_description(self, soup: BeautifulSoup):
        """Add missing meta description."""
        if not soup.find('meta', attrs={'name': 'description'}):
            head = soup.find('head')
            if not head:
                head = soup.new_tag('head')
                if soup.html:
                    soup.html.insert(0, head)
                else:
                    soup.insert(0, head)
            
            meta = soup.new_tag('meta', attrs={
                'name': 'description',
                'content': 'A website built with AI-powered website builder'
            })
            head.append(meta)
            
            self.fixes_applied.append({
                'type': 'missing_meta_description',
                'description': 'Added meta description tag',
                'severity': 'warning'
            })
    
    def _fix_missing_title(self, soup: BeautifulSoup):
        """Add missing title tag."""
        if not soup.find('title'):
            head = soup.find('head')
            if not head:
                head = soup.new_tag('head')
                if soup.html:
                    soup.html.insert(0, head)
                else:
                    soup.insert(0, head)
            
            title = soup.new_tag('title')
            title.string = 'My Website'
            head.append(title)
            
            self.fixes_applied.append({
                'type': 'missing_title',
                'description': 'Added title tag',
                'severity': 'critical'
            })
    
    def _fix_missing_alt_text(self, soup: BeautifulSoup, location: Optional[str] = None):
        """Add missing alt text to images."""
        images = soup.find_all('img')
        fixed_count = 0
        
        for img in images:
            if not img.get('alt'):
                # Try to generate meaningful alt text from src
                src = img.get('src', '')
                filename = src.split('/')[-1].split('.')[0]
                alt_text = filename.replace('-', ' ').replace('_', ' ').title()
                
                if not alt_text:
                    alt_text = 'Image'
                
                img['alt'] = alt_text
                fixed_count += 1
        
        if fixed_count > 0:
            self.fixes_applied.append({
                'type': 'missing_alt_text',
                'description': f'Added alt text to {fixed_count} images',
                'severity': 'warning'
            })
    
    def _fix_missing_lang_attribute(self, soup: BeautifulSoup):
        """Add missing lang attribute to html tag."""
        html_tag = soup.find('html')
        if html_tag and not html_tag.get('lang'):
            html_tag['lang'] = 'en'
            
            self.fixes_applied.append({
                'type': 'missing_lang_attribute',
                'description': 'Added lang="en" to html tag',
                'severity': 'warning'
            })
    
    def _fix_missing_viewport(self, soup: BeautifulSoup):
        """Add missing viewport meta tag."""
        if not soup.find('meta', attrs={'name': 'viewport'}):
            head = soup.find('head')
            if not head:
                head = soup.new_tag('head')
                if soup.html:
                    soup.html.insert(0, head)
                else:
                    soup.insert(0, head)
            
            meta = soup.new_tag('meta', attrs={
                'name': 'viewport',
                'content': 'width=device-width, initial-scale=1.0'
            })
            head.append(meta)
            
            self.fixes_applied.append({
                'type': 'missing_viewport',
                'description': 'Added viewport meta tag',
                'severity': 'critical'
            })
    
    def _fix_missing_charset(self, soup: BeautifulSoup):
        """Add missing charset meta tag."""
        if not soup.find('meta', attrs={'charset': True}):
            head = soup.find('head')
            if not head:
                head = soup.new_tag('head')
                if soup.html:
                    soup.html.insert(0, head)
                else:
                    soup.insert(0, head)
            
            meta = soup.new_tag('meta', attrs={'charset': 'UTF-8'})
            # Insert at beginning of head
            if head.contents:
                head.insert(0, meta)
            else:
                head.append(meta)
            
            self.fixes_applied.append({
                'type': 'missing_charset',
                'description': 'Added charset meta tag',
                'severity': 'critical'
            })
    
    def _fix_heading_hierarchy(self, soup: BeautifulSoup):
        """Fix heading hierarchy issues."""
        # This is a simplified fix - in production, you'd want more sophisticated logic
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        if headings:
            # Ensure there's at least one H1
            h1_count = len([h for h in headings if h.name == 'h1'])
            
            if h1_count == 0 and headings:
                # Convert first heading to H1
                first_heading = headings[0]
                first_heading.name = 'h1'
                
                self.fixes_applied.append({
                    'type': 'heading_hierarchy',
                    'description': 'Converted first heading to H1',
                    'severity': 'warning'
                })
    
    def _fix_missing_aria_labels(self, soup: BeautifulSoup):
        """Add missing ARIA labels to interactive elements."""
        # Fix buttons without text or aria-label
        buttons = soup.find_all('button')
        fixed_count = 0
        
        for button in buttons:
            if not button.get_text(strip=True) and not button.get('aria-label'):
                button['aria-label'] = 'Button'
                fixed_count += 1
        
        # Fix links without text or aria-label
        links = soup.find_all('a')
        for link in links:
            if not link.get_text(strip=True) and not link.get('aria-label'):
                link['aria-label'] = 'Link'
                fixed_count += 1
        
        if fixed_count > 0:
            self.fixes_applied.append({
                'type': 'missing_aria_labels',
                'description': f'Added ARIA labels to {fixed_count} elements',
                'severity': 'warning'
            })
    
    def _fix_missing_form_labels(self, soup: BeautifulSoup):
        """Add missing labels to form inputs."""
        inputs = soup.find_all('input')
        fixed_count = 0
        
        for input_elem in inputs:
            input_id = input_elem.get('id')
            input_type = input_elem.get('type', 'text')
            
            # Skip hidden inputs
            if input_type == 'hidden':
                continue
            
            # Check if label exists
            if input_id:
                label = soup.find('label', attrs={'for': input_id})
                if not label:
                    # Create label
                    label = soup.new_tag('label', attrs={'for': input_id})
                    label.string = input_type.title()
                    
                    # Insert before input
                    input_elem.insert_before(label)
                    fixed_count += 1
            else:
                # Add ID if missing
                input_id = f'input-{fixed_count}'
                input_elem['id'] = input_id
                
                # Create label
                label = soup.new_tag('label', attrs={'for': input_id})
                label.string = input_type.title()
                input_elem.insert_before(label)
                fixed_count += 1
        
        if fixed_count > 0:
            self.fixes_applied.append({
                'type': 'missing_form_labels',
                'description': f'Added labels to {fixed_count} form inputs',
                'severity': 'warning'
            })
    
    def _fix_image_lazy_loading(self, soup: BeautifulSoup):
        """Add lazy loading to images."""
        images = soup.find_all('img')
        fixed_count = 0
        
        for img in images:
            if not img.get('loading'):
                img['loading'] = 'lazy'
                fixed_count += 1
        
        if fixed_count > 0:
            self.fixes_applied.append({
                'type': 'image_lazy_loading',
                'description': f'Added lazy loading to {fixed_count} images',
                'severity': 'info'
            })


# Singleton instance
auto_fix_service = AutoFixService()
