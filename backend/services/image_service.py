from pathlib import Path
from uuid import uuid4
from io import BytesIO

from PIL import Image, UnidentifiedImageError

from backend.config import settings


ALLOWED_FORMATS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp"
}


def validate_image(image_bytes: bytes):

    max_size = settings.max_image_size_mb * 1024 * 1024

    if len(image_bytes) > max_size:
        raise ValueError(
            f"Image must be smaller than "
            f"{settings.max_image_size_mb} MB"
        )

    try:
        image = Image.open(BytesIO(image_bytes))
        image.verify()

    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise ValueError("Uploaded file is not a valid image")

    image = Image.open(BytesIO(image_bytes))

    if image.format not in ALLOWED_FORMATS:
        raise ValueError("Only JPEG, PNG and WEBP images are allowed")

    return image.format


def save_image(image_bytes: bytes, image_format: str):

    upload_directory = Path(settings.upload_dir)
    upload_directory.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{ALLOWED_FORMATS[image_format]}"

    file_path = upload_directory / filename

    file_path.write_bytes(image_bytes)

    return str(file_path)