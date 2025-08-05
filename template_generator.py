"""
Template generator for BuyersMatch real estate marketing slides - Google Cloud Function version
Creates professional property marketing templates similar to the provided examples.
Optimized for serverless deployment with embedded fonts and efficient memory usage.
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np
import io
import os
from typing import Dict, List, Optional, Tuple
import base64

class BuyersMatchTemplate:
    def __init__(self):
        # Exact brand colors from the examples
        self.brand_teal = (78, 205, 196)      # BuyersMatch teal/turquoise
        self.brand_brown = (139, 101, 69)     # Brown for banners
        self.cream_bg = (245, 240, 232)       # Cream background
        self.dark_brown = (101, 67, 33)       # Darker brown for date
        self.white = (255, 255, 255)
        self.black = (34, 34, 34)             # Soft black for text
        
        # Standard template size matching examples
        self.template_size = (1080, 1080)     # Square format
        
        # Font cache for serverless efficiency
        self._font_cache = {}
        
    def _get_font(self, size: int, bold: bool = False):
        """Get font with caching for serverless efficiency"""
        cache_key = f"{size}_{bold}"
        
        if cache_key not in self._font_cache:
            try:
                if bold:
                    # Try common bold font paths in Google Cloud
                    font_paths = [
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                        "arialbd.ttf"
                    ]
                else:
                    font_paths = [
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                        "arial.ttf"
                    ]
                
                font = None
                for font_path in font_paths:
                    try:
                        font = ImageFont.truetype(font_path, size)
                        break
                    except:
                        continue
                
                if font is None:
                    font = ImageFont.load_default()
                
                self._font_cache[cache_key] = font
            except:
                self._font_cache[cache_key] = ImageFont.load_default()
        
        return self._font_cache[cache_key]
        
    def create_property_template(self, 
                               property_data: Dict,
                               main_image: Image.Image,
                               interior_images: List[Image.Image] = None,
                               logo_image: Image.Image = None) -> Image.Image:
        """
        Create a property marketing template matching BuyersMatch examples exactly.
        
        Args:
            property_data: Dict with keys like 'date', 'yield', 'purchase_price', 'current_valuation', etc.
            main_image: Main property exterior image
            interior_images: List of up to 3 interior images
            logo_image: Optional BuyersMatch logo file (thumbs up + text)
        """
        # Create base template with flat cream background
        template = Image.new('RGB', self.template_size, self.cream_bg)
        draw = ImageDraw.Draw(template)
        
        # Add simple dot patterns like in examples (no 3D effects)
        self._add_simple_dot_patterns(draw)
        
        # Add BuyersMatch logo (top left) - use custom logo if provided
        if logo_image:
            # Resize and place custom logo
            logo_resized = logo_image.resize((180, 80), Image.LANCZOS)
            if logo_resized.mode != 'RGBA':
                logo_resized = logo_resized.convert('RGBA')
            
            # Place logo with transparency
            template.paste(logo_resized, (30, 30), logo_resized)
            
            # Add date below custom logo
            date_text = property_data.get('date', 'DEC 2024')
            date_font = self._get_font(32, bold=True)
            
            if logo_resized.size[1] > 60:  # Taller logo
                draw.text((30, 140), date_text, font=date_font, fill=self.dark_brown)
            else:
                draw.text((30, 120), date_text, font=date_font, fill=self.dark_brown)
        else:
            self._add_exact_brand_header(draw, property_data.get('date', 'DEC 2024'), None)
        
        # Add main circular property image - large and clean
        main_circle = self._create_clean_circular_image(main_image, 650)  # Large size
        # Position exactly like examples
        circle_x = self.template_size[0] - 630  # Right side positioning
        circle_y = 100  # Top positioning
        template.paste(main_circle, (circle_x, circle_y), main_circle)
        
        # Add property details section (left side) - clean styling
        self._add_clean_property_details(draw, property_data)
        
        # Add current valuation banner - flat brown banner like examples
        self._add_clean_valuation_banner(draw, property_data.get('current_valuation', '$295,000'))
        
        # Add interior images (bottom) - simple rectangular frames
        if interior_images:
            self._add_clean_interior_images(template, interior_images)
        
        # Add contact information (bottom brown bar)
        self._add_clean_contact_info(draw)
        
        # Add subtle watermark on main image
        self._add_clean_buyersmatch_watermark(template, circle_x, circle_y, 500)
        
        return template
    
    def _add_simple_dot_patterns(self, draw: ImageDraw.Draw):
        """Add simple flat dot patterns like in examples"""
        # Small dots in corners - flat, no gradients
        dot_color = (220, 220, 220)  # Light gray
        dot_size = 3
        
        # Top left area dots
        for i in range(5):
            for j in range(3):
                x = 200 + i * 15
                y = 80 + j * 15
                draw.ellipse([x, y, x + dot_size, y + dot_size], fill=dot_color)
        
        # Bottom right area dots
        for i in range(4):
            for j in range(2):
                x = 850 + i * 15
                y = 950 + j * 15
                draw.ellipse([x, y, x + dot_size, y + dot_size], fill=dot_color)
    
    def _add_exact_brand_header(self, draw: ImageDraw.Draw, date: str, logo_path: Optional[str]):
        """Add exact BuyersMatch header matching examples"""
        # Teal banner (flat, no shadows)
        banner_height = 80
        draw.rectangle([30, 30, 400, 30 + banner_height], fill=self.brand_teal)
        
        # BuyersMatch text
        title_font = self._get_font(36, bold=True)
        subtitle_font = self._get_font(20)
        
        draw.text((40, 50), "BUYERS", fill=self.white, font=title_font)
        draw.text((180, 50), "MATCH", fill=self.white, font=title_font)
        draw.text((40, 90), "Buyers Advocacy", fill=self.white, font=subtitle_font)
        
        # Add date
        date_font = self._get_font(32, bold=True)
        draw.text((30, 130), date, fill=self.brand_brown, font=date_font)
    
    def _create_clean_circular_image(self, image: Image.Image, size: int) -> Image.Image:
        """Create clean circular image without shadows or borders"""
        # Resize image to fit circle
        image = image.resize((size, size), Image.LANCZOS)
        
        # Create circular mask
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, size, size], fill=255)
        
        # Apply mask to create circular image
        circular_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        circular_img.paste(image, (0, 0))
        circular_img.putalpha(mask)
        
        return circular_img
    
    def _add_clean_property_details(self, draw: ImageDraw.Draw, data: Dict):
        """Add property details exactly like examples - no backgrounds"""
        label_font = self._get_font(20)  # Labels remain normal
        value_font = self._get_font(38, bold=True)  # Values bold and larger
        small_font = self._get_font(18)  # For additional info
        small_bold_font = self._get_font(24, bold=True)  # For additional values
        
        current_y = 220
        
        # Property title/address (if provided)
        if data.get('property_title'):
            draw.text((30, current_y), data['property_title'], font=small_bold_font, fill=self.dark_brown)
            current_y += 35
        
        # Property type, bedrooms, bathrooms in one line (if provided)
        property_details = []
        if data.get('property_type'):
            property_details.append(data['property_type'])
        if data.get('bedrooms'):
            property_details.append(f"{data['bedrooms']} bed")
        if data.get('bathrooms'):
            property_details.append(f"{data['bathrooms']} bath")
        
        if property_details:
            details_text = " • ".join(property_details)
            draw.text((30, current_y), details_text, font=small_font, fill=self.dark_brown)
            current_y += 30
        
        # Location (if provided)
        if data.get('location'):
            draw.text((30, current_y), data['location'], font=small_font, fill=self.dark_brown)
            current_y += 35
        
        # Add some spacing before main details
        current_y += 15
        
        # Yield section - simple text, no backgrounds
        draw.text((30, current_y), "YIELD", font=label_font, fill=self.dark_brown)
        yield_value = data.get('yield', '5.59%')
        draw.text((30, current_y + 30), yield_value, font=value_font, fill=self.dark_brown)
        
        # Purchase price section
        price_y = current_y + 100
        draw.text((30, price_y), "PURCHASE PRICE", font=label_font, fill=self.dark_brown)
        price_value = data.get('purchase_price', '$488,000')
        draw.text((30, price_y + 30), price_value, font=value_font, fill=self.dark_brown)
    
    def _add_clean_valuation_banner(self, draw: ImageDraw.Draw, valuation: str):
        """Add flat brown valuation banner exactly like examples"""
        banner_y = 680
        banner_height = 80
        
        # Simple flat banner - no shadows or 3D effects
        banner_points = [
            (30, banner_y), 
            (450, banner_y), 
            (480, banner_y + 40),  # Arrow point
            (450, banner_y + banner_height), 
            (30, banner_y + banner_height)
        ]
        draw.polygon(banner_points, fill=self.brand_brown)
        
        label_font = self._get_font(18)  # Label stays normal
        value_font = self._get_font(48, bold=True)  # Value bold and larger
        
        # White text on brown banner
        draw.text((50, banner_y + 15), "CURRENT VALUATION", font=label_font, fill=self.white)
        draw.text((50, banner_y + 40), valuation, font=value_font, fill=self.white)
    
    def _add_clean_interior_images(self, template: Image.Image, interior_images: List[Image.Image]):
        """Add interior images in clean rectangular frames"""
        if not interior_images:
            return
        
        # Position for interior images (bottom section)
        start_x = 30
        start_y = 800
        image_size = (120, 90)  # Rectangular, not square
        spacing = 140
        
        for i, interior_img in enumerate(interior_images[:3]):  # Max 3 images
            # Resize and position
            resized_img = interior_img.resize(image_size, Image.LANCZOS)
            
            # Position calculation
            x_pos = start_x + (i * spacing)
            y_pos = start_y
            
            # Paste the image
            template.paste(resized_img, (x_pos, y_pos))
    
    def _add_clean_contact_info(self, draw: ImageDraw.Draw):
        """Add contact information bar at bottom"""
        # Simple brown bar at bottom
        bar_y = 950
        bar_height = 80
        draw.rectangle([0, bar_y, self.template_size[0], bar_y + bar_height], fill=self.brand_brown)
        
        # Contact text
        contact_font = self._get_font(24)
        draw.text((30, bar_y + 15), "Contact us today", font=contact_font, fill=self.white)
        draw.text((30, bar_y + 45), "1300 025 376 | admin@buyersmatch.com.au", font=contact_font, fill=self.white)
    
    def _add_clean_buyersmatch_watermark(self, template: Image.Image, circle_x: int, circle_y: int, circle_size: int):
        """Add subtle BUYERSMATCH watermark like in examples"""
        # Create watermark overlay for just the circular area
        watermark = Image.new('RGBA', (circle_size, circle_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)
        
        watermark_font = self._get_font(65, bold=True)  # Bold watermark
        
        text = "BUYERS MATCH"
        try:
            bbox = draw.textbbox((0, 0), text, font=watermark_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            text_width, text_height = draw.textsize(text, font=watermark_font)
        
        # Center the text in the circle
        text_x = (circle_size - text_width) // 2
        text_y = (circle_size - text_height) // 2
        
        # Very subtle white text - like in examples
        draw.text((text_x, text_y), text, font=watermark_font, fill=(255, 255, 255, 100))
        
        # Composite the watermark onto the template
        template.paste(watermark, (circle_x, circle_y), watermark)

def create_sample_template():
    """Create a sample template for testing"""
    generator = BuyersMatchTemplate()
    
    # Sample data
    sample_data = {
        'date': '15 DEC 2024',
        'yield': '7.94%',
        'purchase_price': '$850,000',
        'current_valuation': '$920,000',
        'property_title': '123 Sample Street',
        'property_type': 'Apartment',
        'bedrooms': '3',
        'bathrooms': '2',
        'location': 'Melbourne VIC'
    }
    
    # Create a sample image
    sample_image = Image.new('RGB', (400, 300), (100, 150, 200))
    
    return generator.create_property_template(sample_data, sample_image)
