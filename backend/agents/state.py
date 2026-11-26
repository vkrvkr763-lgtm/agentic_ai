from typing import TypedDict, Optional


class GAARDState(TypedDict, total=False):

    # Complaint information
    complaint_id: int
    image_path: str
    address: str
    latitude: float
    longitude: float
    decision: str

    # Vision AI results
    category: str
    description: str
    severity: str
    needs_human_review: bool

    # Agent decisions
    decision: str
    department_id: int

    # Notification information
    notification_status: str

    # Error handling
    error: Optional[str]
    retry_count: int
# Image quality results
    quality_status: str
    quality_report: dict
    retake_reason: str
    issue_detected: bool
    # Department routing results
    department_id: int
    department_name: str
    department_email: str
    routing_status: str