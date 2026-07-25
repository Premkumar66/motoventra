from PIL import Image
import os

filepath = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\images\bmw_g310gs.png"
if os.path.exists(filepath):
    im = Image.open(filepath)
    im.thumbnail((1200, 800), Image.Resampling.LANCZOS)
    im.save(filepath, "PNG", optimize=True)
    print(f"Resized bmw_g310gs.png to {os.path.getsize(filepath)//1024} KB")
