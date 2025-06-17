from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SlideRenderer:
    def __init__(self, width: int = 1080, height: int = 1920):
        self.width = width
        self.height = height
        self.font_path = self._get_font_path()
        
    def _get_font_path(self) -> str:
        """Get path to Roboto Serif font."""
        font_paths = [
            "data/fonts/RobotoSerif-Regular.ttf",
            "/System/Library/Fonts/Times.ttc",  # macOS fallback
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",  # Linux fallback
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        
        # If no font found, use default
        return None
    
    def _calculate_font_size(self, text: str, max_width: int, min_size: int = 60, max_size: int = 90) -> int:
        """Calculate optimal font size based on text length."""
        if len(text) <= 50:
            return max_size
        elif len(text) <= 100:
            return max_size - 15
        elif len(text) <= 150:
            return max_size - 25
        else:
            return min_size
    
    def _wrap_text(self, text: str, font: ImageFont, max_width: int) -> list:
        """Wrap text to fit within max width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def render_slide_1(self, quote_text: str, author: str, background_path: str, 
                      icon_path: Optional[str] = None) -> Image.Image:
        """Render slide 1: Quote of the day with quote, author, and lotus icon."""
        logger.info(f"Rendering slide 1 - Quote: {quote_text[:50]}...")
        logger.info(f"Background path: {background_path}, exists: {os.path.exists(background_path)}")
        logger.info(f"Icon path: {icon_path}, exists: {os.path.exists(icon_path) if icon_path else 'None'}")
        
        # Load background
        try:
            background = Image.open(background_path).convert('RGBA')
            logger.info(f"Background loaded: {background.size}")
            background = background.resize((self.width, self.height), Image.Resampling.LANCZOS)
            logger.info(f"Background resized to: {background.size}")
        except Exception as e:
            logger.error(f"Failed to load background: {e}")
            # Create fallback background
            background = Image.new('RGBA', (self.width, self.height), (50, 50, 50, 255))
            logger.info("Created fallback background")
        
        # Create overlay for text
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Title "Cytat dnia"
        # title_font_size = 50
        # title_font = ImageFont.truetype(self.font_path, title_font_size) if self.font_path else ImageFont.load_default()
        # title_bbox = title_font.getbbox("Cytat dnia")
        # title_width = title_bbox[2] - title_bbox[0]
        # title_x = (self.width - title_width) // 2
        # title_y = 200
        
        # draw.text((title_x, title_y), "Cytat dnia", fill="#3D3D3D", font=title_font)
        
        # Quote text
        quote_font_size = self._calculate_font_size(quote_text, self.width - 100)
        quote_font = ImageFont.truetype(self.font_path, quote_font_size) if self.font_path else ImageFont.load_default()
        
        # Wrap quote text
        quote_lines = self._wrap_text(quote_text, quote_font, self.width - 100)
        
        # Calculate quote position - moved closer to bottom
        line_height = quote_font_size + 50  # Increased spacing to fill more space
        total_quote_height = len(quote_lines) * line_height
        # Position text in lower 2/3 of screen
        quote_start_y = int(self.height * 0.65) - (total_quote_height // 2)
        
        # Draw quote lines
        for i, line in enumerate(quote_lines):
            line_bbox = quote_font.getbbox(line)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (self.width - line_width) // 2
            line_y = quote_start_y + (i * line_height)
            draw.text((line_x, line_y), line, fill="#3D3D3D", font=quote_font)
        
        # Author
        author_font_size = 40
        author_font = ImageFont.truetype(self.font_path, author_font_size) if self.font_path else ImageFont.load_default()
        author_text = f"— {author}"
        author_bbox = author_font.getbbox(author_text)
        author_width = author_bbox[2] - author_bbox[0]
        author_x = (self.width - author_width) // 2
        author_y = quote_start_y + total_quote_height + 50
        
        # Apply opacity to author color
        author_color = (123, 123, 123, int(255 * 0.7))  # #7B7B7B with 70% opacity
        draw.text((author_x, author_y), author_text, fill=author_color, font=author_font)
        
        # Add lotus icon if provided
        if icon_path and os.path.exists(icon_path):
            try:
                icon = Image.open(icon_path).convert('RGBA')
                icon_size = 80
                icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                icon_x = (self.width - icon_size) // 2
                icon_y = author_y + 80
                overlay.paste(icon, (icon_x, icon_y), icon)
            except Exception:
                pass  # Ignore icon errors
        
        # Combine background and overlay
        result = Image.alpha_composite(background, overlay)
        return result.convert('RGB')
    
    def render_slide_2(self, reflection_text: str, background_path: str, 
                      icon_path: Optional[str] = None) -> Image.Image:
        """Render slide 2: Reflection with reflection text and meditation icon."""
        # Load background
        background = Image.open(background_path).convert('RGBA')
        background = background.resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        # Create overlay for text
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Title "Refleksja" - removed as it was unexpected
        # title_font_size = 50
        # title_font = ImageFont.truetype(self.font_path, title_font_size) if self.font_path else ImageFont.load_default()
        # title_bbox = title_font.getbbox("Refleksja")
        # title_width = title_bbox[2] - title_bbox[0]
        # title_x = (self.width - title_width) // 2
        # title_y = 200
        # 
        # draw.text((title_x, title_y), "Refleksja", fill="#3D3D3D", font=title_font)
        
        # Reflection text
        reflection_font_size = self._calculate_font_size(reflection_text, self.width - 100)
        reflection_font = ImageFont.truetype(self.font_path, reflection_font_size) if self.font_path else ImageFont.load_default()
        
        # Wrap reflection text
        reflection_lines = self._wrap_text(reflection_text, reflection_font, self.width - 100)
        
        # Calculate reflection position - moved closer to bottom
        line_height = reflection_font_size + 50  # Increased spacing to fill more space
        total_reflection_height = len(reflection_lines) * line_height
        # Position text in lower 2/3 of screen
        reflection_start_y = int(self.height * 0.65) - (total_reflection_height // 2)
        
        # Draw reflection lines
        for i, line in enumerate(reflection_lines):
            line_bbox = reflection_font.getbbox(line)
            line_width = line_bbox[2] - line_bbox[0]
            line_x = (self.width - line_width) // 2
            line_y = reflection_start_y + (i * line_height)
            draw.text((line_x, line_y), line, fill="#3D3D3D", font=reflection_font)
        
        # Add meditation icon if provided
        if icon_path and os.path.exists(icon_path):
            try:
                icon = Image.open(icon_path).convert('RGBA')
                icon_size = 80
                icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
                icon_x = (self.width - icon_size) // 2
                icon_y = reflection_start_y + total_reflection_height + 50
                overlay.paste(icon, (icon_x, icon_y), icon)
            except Exception:
                pass  # Ignore icon errors
        
        # Combine background and overlay
        result = Image.alpha_composite(background, overlay)
        return result.convert('RGB')
    
    def add_watermark(self, image: Image.Image, text: str = "jakmedytowac.pl") -> Image.Image:
        """Add watermark to image."""
        watermark_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_overlay)
        
        # Watermark font
        watermark_font_size = 24
        watermark_font = ImageFont.truetype(self.font_path, watermark_font_size) if self.font_path else ImageFont.load_default()
        
        # Position watermark in bottom right corner
        watermark_bbox = watermark_font.getbbox(text)
        watermark_width = watermark_bbox[2] - watermark_bbox[0]
        watermark_height = watermark_bbox[3] - watermark_bbox[1]
        
        watermark_x = image.width - watermark_width - 20
        watermark_y = image.height - watermark_height - 20
        
        # Semi-transparent white color
        watermark_color = (255, 255, 255, 180)
        draw.text((watermark_x, watermark_y), text, fill=watermark_color, font=watermark_font)
        
        # Apply watermark
        result = Image.alpha_composite(image.convert('RGBA'), watermark_overlay)
        return result.convert('RGB')