from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps


def optimize_profile_image(uploaded_file, stem="profile"):
    """Rotate, strip metadata, resize and return a compact JPEG upload."""
    if not uploaded_file:
        return uploaded_file
    image = Image.open(uploaded_file)
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "L"):
        background = Image.new("RGB", image.size, "white")
        if image.mode == "RGBA":
            background.paste(image, mask=image.getchannel("A"))
        else:
            background.paste(image.convert("RGB"))
        image = background
    else:
        image = image.convert("RGB")
    image.thumbnail((768, 768), Image.Resampling.LANCZOS)
    output = BytesIO()
    image.save(output, format="JPEG", quality=86, optimize=True)
    output.seek(0)
    return ContentFile(output.read(), name=f"{stem}.jpg")
