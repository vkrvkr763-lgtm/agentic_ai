from sqlalchemy.orm import Session

from backend.agents.state import GAARDState
from backend.services.vision_service import analyze_civic_image


def vision_agent(state: GAARDState) -> dict:
    """
    Analyze a complaint image using Gemini Vision AI.
    """

    print("Vision Agent started")

    image_path = state["image_path"]

    # Create a separate database session for this agent
    from backend.database.session import SessionLocal

    db: Session = SessionLocal()

    try:
        result = analyze_civic_image(
            image_path=image_path,
            db=db
        )

        print("Vision Agent completed")

        return {
            "category": result["category"],
            "description": result["description"],
            "severity": result["severity"],
            "issue_detected": result["issue_detected"],
            "needs_human_review": result["needs_human_review"],
            "error": None
        }

    except Exception as error:

        print(f"Vision Agent failed: {error}")

        return {
            "error": "Vision analysis failed",
            "needs_human_review": True,
            "issue_detected": False,

        }

    finally:
        db.close()