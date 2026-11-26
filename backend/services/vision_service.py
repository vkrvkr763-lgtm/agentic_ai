import json
import mimetypes
from pathlib import Path

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database.models import IssueCategory
from typing import Literal
from pydantic import BaseModel, Field


class VisionResult(BaseModel):
    issue_detected: bool
    category: str  | None=None
    description: str
    severity: Literal["Low", "Medium", "High"] | None = None
    needs_human_review: bool = False


client = genai.Client(api_key=settings.gemini_api_key)


def analyze_civic_image(image_path: str, db: Session) -> dict:

    categories = db.query(IssueCategory).filter(
        IssueCategory.is_active.is_(True)
    ).all()

    category_names = [category.name for category in categories]

    if not category_names:
        raise ValueError("No active issue categories available")

    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError("Complaint image not found")

    mime_type = mimetypes.guess_type(path.name)[0]

    if mime_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise ValueError("Unsupported image format")

    prompt = f"""
    You are the Vision AI agent for GAARD,
    a civic issue detection system.

    Allowed civic issue categories:
    {json.dumps(category_names)}

    Analyze the uploaded image.

    Rules:

    1. Determine whether the image contains a recognizable
    civic infrastructure or public cleanliness issue.

    2. If a civic issue is present:
    - Set issue_detected to true.
    - Select one category from the allowed categories.
    - Describe only visible evidence.
    - Assess severity as Low, Medium or High.

    3. If the image does not contain a civic issue:
    - Set issue_detected to false.
    - Set category to null.
    - Set severity to null.

    4. If the image is ambiguous or insufficient to classify:
    - Set needs_human_review to true.

    5. Never invent information or infer an issue
    that is not visible.

    Return structured JSON only.
    """

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[
            types.Part.from_text(text=prompt),
            types.Part.from_bytes(
                data=path.read_bytes(),
                mime_type=mime_type
            )
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=VisionResult,
            max_output_tokens=300
        )
    )

    result = VisionResult.model_validate_json(response.text)

    # Validate model output against database categories.
# Check whether a civic issue was detected
    if not result.issue_detected:
        return result.model_dump()

    # Validate category against database categories
    valid_categories = {
        name.casefold(): name
        for name in category_names
    }

    matched_category = valid_categories.get(
        result.category.strip().casefold()
        if result.category else ""
    )

    if matched_category is None:
        result.category = None
        result.needs_human_review = True
    else:
        result.category = matched_category

    return result.model_dump()

    if matched_category is None:
        result.needs_human_review = True
        result.category = "Unclassified"
    else:
        result.category = matched_category

    return result.model_dump()