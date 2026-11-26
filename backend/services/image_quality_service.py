import cv2
from pathlib import Path


# Initial thresholds – we will tune these using test images.
MIN_WIDTH = 240
MIN_HEIGHT = 140
MIN_BRIGHTNESS = 40
MAX_BRIGHTNESS = 220
BLUR_THRESHOLD = 80


def check_image_quality(image_path: str) -> dict:

    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError("Image not found")

    image = cv2.imread(str(path))

    if image is None:
        raise ValueError("Unable to read image")

    height, width = image.shape[:2]

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # 1. Blur detection
    blur_score = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    # 2. Brightness detection
    brightness = gray.mean()

    # 3. Resolution detection
    resolution_ok = (
        width >= MIN_WIDTH and
        height >= MIN_HEIGHT
    )

    issues = []

    if not resolution_ok:
        quality_status = "retake_required"

    elif blur_score < BLUR_THRESHOLD:
        quality_status = "retake_required"

    elif brightness < MIN_BRIGHTNESS or brightness > MAX_BRIGHTNESS:
        quality_status = "retake_required"

    else:
        quality_status = "good"
    # Determine quality status
    if not resolution_ok or blur_score < BLUR_THRESHOLD * 0.5:
        quality_status = "retake_required"

    elif issues:
        quality_status = "review_required"

    else:
        quality_status = "good"

    return {
        "quality_status": quality_status,
        "width": width,
        "height": height,
        "blur_score": round(float(blur_score), 2),
        "brightness": round(float(brightness), 2),
        "issues": issues
    }