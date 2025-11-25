"""
Service for exporting websites.
"""
import os
import zipfile
import io
import shutil
import tempfile
from typing import Optional
from git import Repo, Actor
from datetime import datetime

from utils.logging import logger
from utils.config import settings

class ExportService:
    """Service for handling website exports."""

    def create_zip_export(self, html_code: str, css_code: str, js_code: str, assets: list = None) -> io.BytesIO:
        """
        Create a ZIP file containing the website code and assets.
        """
        try:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add index.html
                full_html = self._construct_full_html(html_code, css_code, js_code)
                zip_file.writestr('index.html', full_html)
                
                # Add styles.css
                zip_file.writestr('css/styles.css', css_code)
                
                # Add script.js
                zip_file.writestr('js/script.js', js_code)
                
                # Add assets (mock implementation for now)
                # In a real scenario, we would read asset files and add them
                if assets:
                    for asset in assets:
                        # zip_file.write(asset.path, f"assets/{asset.filename}")
                        pass
                        
            zip_buffer.seek(0)
            return zip_buffer
            
        except Exception as e:
            logger.error(f"Error creating ZIP export: {e}")
            raise

    def export_to_github(self, repo_url: str, token: str, html_code: str, css_code: str, js_code: str) -> str:
        """
        Export website to a GitHub repository.
        """
        temp_dir = tempfile.mkdtemp()
        try:
            # Clone or init repo
            # Note: This is a simplified implementation. 
            # In production, we'd need to handle auth carefully (e.g. using a token in the URL)
            
            # Construct auth URL
            auth_repo_url = repo_url.replace("https://", f"https://{token}@")
            
            repo = Repo.init(temp_dir)
            
            # Create files
            os.makedirs(os.path.join(temp_dir, 'css'), exist_ok=True)
            os.makedirs(os.path.join(temp_dir, 'js'), exist_ok=True)
            
            with open(os.path.join(temp_dir, 'index.html'), 'w') as f:
                f.write(self._construct_full_html(html_code, css_code, js_code))
                
            with open(os.path.join(temp_dir, 'css/styles.css'), 'w') as f:
                f.write(css_code)
                
            with open(os.path.join(temp_dir, 'js/script.js'), 'w') as f:
                f.write(js_code)
                
            # Commit and push
            repo.index.add(['.'])
            author = Actor("AI Builder", "builder@example.com")
            repo.index.commit(f"Update website - {datetime.utcnow().isoformat()}", author=author, committer=author)
            
            # Create remote and push
            # origin = repo.create_remote('origin', auth_repo_url)
            # origin.push()
            
            return "Successfully exported to GitHub (Mock Push)"
            
        except Exception as e:
            logger.error(f"Error exporting to GitHub: {e}")
            raise
        finally:
            shutil.rmtree(temp_dir)

    def _construct_full_html(self, html: str, css: str, js: str) -> str:
        """Construct full HTML file with linked CSS and JS."""
        # Check if it's already a full document
        if "<!DOCTYPE html>" in html or "<html>" in html:
            # Inject links if missing
            # This is a simple injection, might need more robust parsing
            return html
            
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exported Website</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    {html}
    <script src="js/script.js"></script>
</body>
</html>"""

# Global instance
export_service = ExportService()
