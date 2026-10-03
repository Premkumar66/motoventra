import os
import zipfile

pptx_path = r"c:\CCP PROJECT\Motoventra\MotoMod_AI_Presentation.pptx"
html_path = r"C:\Users\rrpre\.gemini\antigravity\brain\dcf80aaa-c323-407f-888c-e29c09e9a9eb\presentation_viewer.html"
zip_out = r"c:\CCP PROJECT\Motoventra\motomod-ai\backend\app\static\MotoMod_AI_Presentation_Package.zip"

with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(pptx_path, arcname="MotoMod_AI_Presentation.pptx")
    z.write(html_path, arcname="MotoMod_AI_Interactive_Deck.html")

print("Created presentation ZIP package at:", zip_out)
