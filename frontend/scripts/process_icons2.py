from PIL import Image
import os
import glob

def process_icon(filepath):
    print(f"Processing {filepath}...")
    img = Image.open(filepath).convert("RGBA")
    
    # Get bounding box of non-transparent pixels
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    img.save(filepath, "PNG")

for f in glob.glob("public/icons/*.png"):
    process_icon(f)
