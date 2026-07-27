import sys
try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

image_path = r"C:\Network\media\company_logos\noa_erp_logo_v2.png"
out_path = r"C:\Network\media\company_logos\noa_erp_logo_v3.png"
static_out = r"C:\Network\static\company_logos\noa_erp_logo_v3.png"

try:
    img = Image.open(image_path).convert("RGBA")
    
    # Create a new white image with the same size
    white_bg = Image.new("RGBA", img.size, "WHITE")
    
    # Paste the original image on top of the white background
    white_bg.paste(img, (0, 0), img)
    
    # Convert back to RGB to save as PNG without transparency
    final_img = white_bg.convert("RGB")
    
    final_img.save(out_path)
    final_img.save(static_out)
    print("Successfully processed the logo with a white background.")
except Exception as e:
    print(f"Error processing image: {e}")
