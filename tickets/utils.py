import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import os

def generer_qr_code(donnees, nom_fichier):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(donnees)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    file_name = f"{nom_fichier}.png"
    path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', file_name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(buffer.getvalue())
    return f"qr_codes/{file_name}"