"""
Google Cloud Function for BuyersMatch Marketing Post Generator
Serverless API that creates professional property marketing posts
"""

import functions_framework
from flask import Request, jsonify, send_file
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageOps
import numpy as np
import piexif
import os
import random
import io
import base64
from typing import Optional, List
import tempfile
import logging
from template_generator import BuyersMatchTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def remove_metadata(image_bytes):
    """Removes metadata from image bytes."""
    img = Image.open(io.BytesIO(image_bytes))
    output_buffer = io.BytesIO()
    img.save(output_buffer, format="JPEG", quality=95)
    return output_buffer.getvalue()

def add_watermark(img, text="BuyersMatch", opacity=120, position='center'):
    """Adds semi-transparent watermark text to the image."""
    watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    
    # Larger font size for visibility
    font_size = int(img.size[1] * 0.08)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
    except AttributeError:
        text_size = draw.textsize(text, font=font)
    
    if position == 'center':
        text_pos = ((img.size[0] - text_size[0]) // 2, (img.size[1] - text_size[1]) // 2)
    else:  # bottom-right
        text_pos = (img.size[0] - text_size[0] - 20, img.size[1] - text_size[1] - 20)
    
    draw.text(text_pos, text, font=font, fill=(255, 255, 255, opacity))
    
    return Image.alpha_composite(img.convert('RGBA'), watermark).convert('RGB')

def slightly_rotate_and_flip(img, max_angle=0.3):
    """Apply very minimal rotation to avoid distortion."""
    angle = random.uniform(-max_angle, max_angle)
    return img.rotate(angle, expand=False, fillcolor=(255, 255, 255))

def compress_and_resize(img, quality=92, max_size=None):
    """Compress with minimal size change."""
    if max_size and (img.size[0] > max_size or img.size[1] > max_size):
        img.thumbnail((max_size, max_size), Image.LANCZOS)
    return img

def add_noise(img, amount=0.005):
    """Add minimal noise to image."""
    np_img = np.array(img)
    noise = np.random.randint(-int(255 * amount), int(255 * amount), np_img.shape, dtype=np.int16)
    np_img = np.clip(np_img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(np_img)

def protect_image_bytes(image_bytes):
    """Apply minimal transformations without center watermark."""
    img = Image.open(io.BytesIO(image_bytes))
    
    img = slightly_rotate_and_flip(img)
    img = compress_and_resize(img)
    img = add_noise(img, amount=0.005)
    # Removed center watermark - only keep the one on the circular image
    
    output_buffer = io.BytesIO()
    img.save(output_buffer, format="JPEG", quality=92)
    output_buffer.seek(0)
    
    return output_buffer.getvalue()

@functions_framework.http
def generate_marketing_post(request: Request):
    """
    Google Cloud Function endpoint for generating BuyersMatch marketing posts.
    
    Accepts multipart form data with images and property information.
    Returns a professional marketing post image.
    """
    
    # Handle CORS for web requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    # Set CORS headers for actual request
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    if request.method != 'POST':
        return jsonify({'error': 'Method not allowed'}), 405, headers
    
    try:
        # Get form data
        form_data = request.form
        files = request.files
        
        logger.info(f"Received form data: {list(form_data.keys())}")
        logger.info(f"Received files: {list(files.keys())}")
        
        # Validate required fields
        required_fields = ['date', 'yield_rate', 'purchase_price', 'current_valuation']
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400, headers
        
        # Validate main image
        if 'main_image' not in files:
            return jsonify({'error': 'Main image is required'}), 400, headers
        
        main_image_file = files['main_image']
        if not main_image_file.content_type.startswith('image/'):
            return jsonify({'error': 'Main file must be an image'}), 400, headers
        
        # Read main image
        main_image_bytes = main_image_file.read()
        main_img = Image.open(io.BytesIO(main_image_bytes))
        
        # Read logo if provided
        logo_img = None
        if 'logo' in files and files['logo'].content_type.startswith('image/'):
            logo_bytes = files['logo'].read()
            logo_img = Image.open(io.BytesIO(logo_bytes))
        
        # Read interior images if provided
        interior_images = []
        for interior_key in ['interior1', 'interior2', 'interior3']:
            if interior_key in files and files[interior_key].content_type.startswith('image/'):
                interior_bytes = files[interior_key].read()
                interior_img = Image.open(io.BytesIO(interior_bytes))
                interior_images.append(interior_img)
        
        # Prepare comprehensive property data
        property_data = {
            'date': form_data.get('date'),
            'yield': form_data.get('yield_rate'),
            'purchase_price': form_data.get('purchase_price'),
            'current_valuation': form_data.get('current_valuation'),
            'property_title': form_data.get('property_title'),
            'property_type': form_data.get('property_type'),
            'bedrooms': form_data.get('bedrooms'),
            'bathrooms': form_data.get('bathrooms'),
            'location': form_data.get('location')
        }
        
        logger.info(f"Processing property data: {property_data}")
        
        # Generate template
        generator = BuyersMatchTemplate()
        template_image = generator.create_property_template(
            property_data, 
            main_img, 
            interior_images if interior_images else None,
            logo_img
        )
        
        # Apply anti-search protection if requested
        apply_protection = form_data.get('apply_protection', 'true').lower() == 'true'
        output_format = form_data.get('output_format', 'PNG').upper()
        
        if apply_protection:
            # Convert template to bytes for protection processing
            temp_buffer = io.BytesIO()
            template_image.save(temp_buffer, format="JPEG", quality=95)
            temp_buffer.seek(0)
            
            # Apply protection
            protected_bytes = protect_image_bytes(temp_buffer.getvalue())
            final_image_bytes = protected_bytes
            content_type = "image/jpeg"
        else:
            # Save without protection
            output_buffer = io.BytesIO()
            template_image.save(output_buffer, format=output_format, quality=95)
            output_buffer.seek(0)
            final_image_bytes = output_buffer.getvalue()
            content_type = f"image/{output_format.lower()}"
        
        logger.info(f"Generated marketing post successfully. Size: {len(final_image_bytes)} bytes")
        
        # Return the image
        return send_file(
            io.BytesIO(final_image_bytes),
            mimetype=content_type,
            as_attachment=True,
            download_name=f"buyersmatch_post_{form_data.get('date', 'unknown').replace(' ', '_')}.{output_format.lower()}"
        )
        
    except Exception as e:
        logger.error(f"Error generating marketing post: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Error generating marketing post: {str(e)}'
        }), 500, headers

@functions_framework.http
def health_check(request: Request):
    """Health check endpoint for the Google Cloud Function."""
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    return jsonify({
        'status': 'healthy',
        'service': 'BuyersMatch Marketing Post Generator',
        'version': '2.0.0'
    }), 200, headers
