from backend.agents.state import GAARDState
from backend.services.email_service import send_complaint_email


def notification_agent(state: GAARDState) -> dict:
    print("Notification Agent started")

    try:
        recipient = state.get("department_email")

        if not recipient:
            raise ValueError("Department email is missing")

        send_complaint_email(
            recipient=recipient,
            complaint_id=state["complaint_id"],
            category=state["category"],
            description=state["description"],
            severity=state["severity"],
            address=state.get("address") or "Not provided"
        )

        print(f"Email submitted to: {recipient}")

        return {
            "notification_status": "accepted_by_smtp",
            "error": None
        }

    except Exception as exc:
        print(f"Notification failed: {exc}")

        return {
            "notification_status": "failed",
            "error": str(exc)
        }