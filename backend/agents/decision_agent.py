from backend.agents.state import GAARDState
from backend.agents.state import GAARDState


def decision_agent(state: GAARDState) -> dict:

    print("Decision Agent started")

    # Check for processing errors
    if state.get("error"):
        return {"decision": "human_review"}

    # Check whether human review is required
    if state.get("needs_human_review"):
        return {"decision": "human_review"}

    # Check whether a civic issue was detected
    if not state.get("issue_detected", False):
        return {"decision": "rejected"}

    # Accept valid civic complaint
    return {"decision": "approved"}


def decide_after_quality_check(state: GAARDState) -> str:

    quality_status = state.get("quality_status")

    if quality_status == "good":
        return "analyze"

    if quality_status == "retake_required":
        return "retake"

    return "error"