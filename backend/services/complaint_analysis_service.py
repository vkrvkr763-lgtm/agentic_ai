from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.agents.graph import gaard_graph
from backend.database.models import Complaint, IssueCategory


def analyze_complaint(complaint_id: int, db: Session):

    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id
    ).first()

    if not complaint:
        raise ValueError("Complaint not found")

    if complaint.ai_status == "completed":
        return {
            "message": "Complaint already analyzed",
            "complaint_id": complaint.id,
            "ai_status": complaint.ai_status
        }

    try:
        complaint.ai_status = "processing"
        complaint.ai_error = None
        db.commit()

        # Prepare initial LangGraph state
        initial_state = {
            "complaint_id": complaint.id,
            "image_path": complaint.image_path,
            "address": complaint.address or "",
            "retry_count": 0
        }

        if complaint.latitude is not None:
            initial_state["latitude"] = complaint.latitude

        if complaint.longitude is not None:
            initial_state["longitude"] = complaint.longitude

        # Execute complete agent workflow
        result = gaard_graph.invoke(initial_state)

        # Save AI classification
        category_name = result.get("category")

        category = None

        if category_name:
            category = db.query(IssueCategory).filter(
                IssueCategory.name.ilike(category_name),
                IssueCategory.is_active.is_(True)
            ).first()

        complaint.category_id = category.id if category else None

        complaint.description = result.get(
            "description",
            complaint.description
        )

        complaint.severity = result.get("severity")

        # Save department routing
        complaint.department_id = result.get("department_id")

        # Save notification status
        notification_status = result.get("notification_status")

        if notification_status:
            complaint.email_status = notification_status
        elif result.get("decision") != "approved":
            complaint.email_status = "not_sent"
        else:
            complaint.email_status = "not_sent"

        # Update complaint and AI statuses
        decision = result.get("decision")

        if decision == "approved":
            complaint.ai_status = "completed"

            if result.get("routing_status") == "routed":
                complaint.status = (
                    "routed"
                    if notification_status == "accepted_by_smtp"
                    else "notification_failed"
                )
            else:
                complaint.status = "routing_failed"

        elif decision == "rejected":
            complaint.ai_status = "completed"
            complaint.status = "rejected"

        elif decision == "human_review":
            complaint.ai_status = "review_required"
            complaint.status = "review_required"

        elif result.get("quality_status") == "retake_required":
            complaint.ai_status = "review_required"
            complaint.status = "retake_required"

        else:
            complaint.ai_status = "failed"
            complaint.status = "processing_failed"
            complaint.ai_error = result.get("error") or "Workflow failed"

        complaint.ai_analyzed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(complaint)

        return {
            "complaint_id": complaint.id,
            "decision": decision,
            "category": category_name,
            "department": result.get("department_name"),
            "ai_status": complaint.ai_status,
            "complaint_status": complaint.status,
            "email_status": complaint.email_status
        }

    except Exception as error:
        db.rollback()

        complaint = db.query(Complaint).filter(
            Complaint.id == complaint_id
        ).first()

        if complaint:
            complaint.ai_status = "failed"
            complaint.ai_error = str(error)[:1000]
            complaint.status = "processing_failed"
            db.commit()

        raise