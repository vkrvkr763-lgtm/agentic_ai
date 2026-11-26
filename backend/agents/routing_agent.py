from sqlalchemy.orm import Session

from backend.agents.state import GAARDState
from backend.database.session import SessionLocal
from backend.database.models import (
    IssueCategory,
    CategoryRouting,
    Department
)


def routing_agent(state: GAARDState) -> dict:

    print("Routing Agent started")

    category_name = state.get("category")

    if not category_name:
        return {
            "routing_status": "failed",
            "error": "Complaint category is missing"
        }

    db: Session = SessionLocal()

    try:
        category = db.query(IssueCategory).filter(
            IssueCategory.name.ilike(category_name),
            IssueCategory.is_active.is_(True)
        ).first()

        if not category:
            return {
                "routing_status": "failed",
                "error": "Active category not found"
            }

        routing = (
            db.query(CategoryRouting, Department)
            .join(
                Department,
                CategoryRouting.department_id == Department.id
            )
            .filter(
                CategoryRouting.category_id == category.id,
                Department.is_active.is_(True)
            )
            .order_by(CategoryRouting.priority.asc())
            .first()
        )

        if not routing:
            return {
                "routing_status": "failed",
                "error": "No active department routing rule found"
            }

        routing_rule, department = routing

        print(f"Complaint routed to: {department.name}")

        return {
            "department_id": department.id,
            "department_name": department.name,
            "department_email": department.email,
            "routing_status": "routed",
            "error": None
        }

    except Exception as error:

        print(f"Routing Agent failed: {error}")

        return {
            "routing_status": "failed",
            "error": str(error)
        }

    finally:
        db.close()