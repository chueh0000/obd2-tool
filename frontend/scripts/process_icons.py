from PIL import Image
import os
import glob

def process_icon(filepath):
    print(f"Processing {filepath}...")
    img = Image.open(filepath).convert("RGBA")
    data = img.getdata()
    
    new_data = []
    for item in data:
        r, g, b, a = item
        # Calculate luminance (0 = black, 255 = white)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        
        # If it's fully transparent originally, keep it transparent
        if a < 10:
            new_data.append((255, 255, 255, 0))
            continue
            
        # We want dark pixels to become white and opaque
        # We want light pixels (like white background) to become transparent
        # Invert luminance to get opacity (0 = transparent, 255 = opaque)
        darkness = 255 - lum
        
        # If the original image was just a solid icon with an alpha channel (like fuel.png might be)
        # where the icon is dark grey and background is transparent, the 'a' already handles background.
        # But if the background is solid white, 'a' is 255, and darkness will be 0, making it transparent.
        
        # We combine both original alpha and darkness
        new_a = int((darkness / 255.0) * a)
        
        # Tweak: if it's very dark, just make it fully opaque
        if new_a > 200:
            new_a = 255
            
        new_data.append((255, 255, 255, new_a))
        
    img.putdata(new_data)
    img.save(filepath, "PNG")

for f in glob.glob("public/icons/*.png"):
    process_icon(f)
