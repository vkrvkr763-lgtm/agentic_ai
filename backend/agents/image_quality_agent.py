from backend.agents.state import GAARDState
from backend.services.image_quality_service import check_image_quality


def image_quality_agent(state: GAARDState) -> dict:

    print("Image Quality Agent started")

    try:
        result = check_image_quality(state["image_path"])

        print("Image Quality Result:", result)

        if result["quality_status"] == "retake_required":
            return {
                "quality_status": "retake_required",
                "quality_report": result,
                "retake_reason": ", ".join(result["issues"])
            }

        return {
            "quality_status": "good",
            "quality_report": result,
            "retake_reason": ""
        }

    except Exception as error:

        print("Image quality check failed:", error)

        return {
            "quality_status": "error",
            "quality_report": {},
            "retake_reason": "Unable to process the image. Please upload another image.",
            "error": str(error)
        }