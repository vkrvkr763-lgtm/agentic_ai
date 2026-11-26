from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from backend.schemas.routing import RoutingCreate

from fastapi import BackgroundTasks
from backend.database.session import SessionLocal
from backend.services.complaint_analysis_service import analyze_complaint

from backend.schemas.category import CategoryCreate, CategoryUpdate

from backend.config import settings
from backend.database.session import get_db
from backend.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate
)
from backend.database.models import (
    IssueCategory,
    Department,
    CategoryRouting,
    Complaint
)
from pathlib import Path

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form
)

from backend.services.image_service import (
    validate_image,
    save_image
)
app = FastAPI(title=settings.app_name)


@app.get("/")
def home():
    return {"message": "Welcome to GAARD"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# Get all active issue categories
@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):

    categories = db.query(IssueCategory).filter(
        IssueCategory.is_active.is_(True)
    ).all()

    return [
        {
            "id": category.id,
            "name": category.name,
            "description": category.description
        }
        for category in categories
    ]
# CREATE CATEGORY
@app.post("/categories", status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(IssueCategory).filter(
        IssueCategory.name == data.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Category already exists"
        )

    category = IssueCategory(
        name=data.name,
        description=data.description
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return {
        "message": "Category created successfully",
        "id": category.id,
        "name": category.name
    }


# UPDATE CATEGORY
@app.patch("/categories/{category_id}")
def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    category = db.query(IssueCategory).filter(
        IssueCategory.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    updates = data.model_dump(exclude_unset=True)

    if "name" in updates and updates["name"] is None:
        raise HTTPException(
            status_code=422,
            detail="Category name cannot be null"
        )

    for field, value in updates.items():
        setattr(category, field, value)

    try:
        db.commit()
        db.refresh(category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category name already exists"
        )

    return {
        "message": "Category updated successfully",
        "id": category.id,
        "name": category.name
    }


# DEACTIVATE CATEGORY
@app.delete("/categories/{category_id}")
def deactivate_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(IssueCategory).filter(
        IssueCategory.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    category.is_active = False
    db.commit()

    return {
        "message": "Category deactivated successfully"
    }

# Get all active departments
@app.get("/departments")
def get_departments(db: Session = Depends(get_db)):

    departments = db.query(Department).filter(
        Department.is_active.is_(True)
    ).all()

    return [
        {
            "id": department.id,
            "name": department.name,
            "email": department.email,
            "jurisdiction": department.jurisdiction
        }
        for department in departments
    ]


@app.get("/routing-rules")
def get_routing_rules(db: Session = Depends(get_db)):

    routes = db.query(CategoryRouting).all()

    return [
        {
            "id": route.id,
            "category_id": route.category_id,
            "department_id": route.department_id,
            "category": route.category.name,
            "department": route.department.name,
            "department_email": route.department.email,
            "priority": route.priority
        }
        for route in routes
        if route.category.is_active and route.department.is_active
    ]
@app.post("/routing-rules", status_code=201)
def create_routing_rule(
    data: RoutingCreate,
    db: Session = Depends(get_db)
):
    category = db.query(IssueCategory).filter(
        IssueCategory.id == data.category_id,
        IssueCategory.is_active.is_(True)
    ).first()

    if not category:
        raise HTTPException(404, "Active category not found")

    department = db.query(Department).filter(
        Department.id == data.department_id,
        Department.is_active.is_(True)
    ).first()

    if not department:
        raise HTTPException(404, "Active department not found")

    existing = db.query(CategoryRouting).filter(
        CategoryRouting.category_id == data.category_id,
        CategoryRouting.department_id == data.department_id
    ).first()

    if existing:
        raise HTTPException(409, "Routing rule already exists")

    route = CategoryRouting(
        category_id=data.category_id,
        department_id=data.department_id,
        priority=data.priority
    )

    db.add(route)
    db.commit()
    db.refresh(route)

    return {
        "message": "Routing rule created successfully",
        "id": route.id
    }
@app.delete("/routing-rules/{routing_id}")
def delete_routing_rule(
    routing_id: int,
    db: Session = Depends(get_db)
):
    route = db.query(CategoryRouting).filter(
        CategoryRouting.id == routing_id
    ).first()

    if not route:
        raise HTTPException(404, "Routing rule not found")

    db.delete(route)
    db.commit()

    return {"message": "Routing rule deleted successfully"}
# Get all complaints
@app.get("/complaints")
def get_complaints(db: Session = Depends(get_db)):

    complaints = db.query(Complaint).order_by(
        Complaint.created_at.desc()
    ).all()

    return [
        {
            "id": complaint.id,
            "description": complaint.description,
            "severity": complaint.severity,
            "status": complaint.status,
            "email_status": complaint.email_status
        }
        for complaint in complaints
    ]
@app.get("/complaints/{complaint_id}")
def get_complaint_details(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(
        Complaint.id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(404, "Complaint not found")

    category = db.query(IssueCategory).filter(
        IssueCategory.id == complaint.category_id
    ).first() if complaint.category_id else None

    department = db.query(Department).filter(
        Department.id == complaint.department_id
    ).first() if complaint.department_id else None

    return {
        "id": complaint.id,
        "tracking_id": f"GAARD-{complaint.id:06d}",
        "address": complaint.address,
        "description": complaint.description,
        "category": category.name if category else None,
        "severity": complaint.severity,
        "department": department.name if department else None,
        "status": complaint.status,
        "ai_status": complaint.ai_status,
        "ai_error": complaint.ai_error,
        "email_status": complaint.email_status
    }
    
# CREATE DEPARTMENT
@app.post("/departments", status_code=201)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Department).filter(
        Department.name == data.name
    ).first()

    if existing:
        raise HTTPException(409, "Department already exists")

    department = Department(
        name=data.name,
        email=str(data.email),
        jurisdiction=data.jurisdiction
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return {
        "message": "Department created successfully",
        "id": department.id
    }


# UPDATE DEPARTMENT
@app.patch("/departments/{department_id}")
def update_department(
    department_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(404, "Department not found")

    updates = data.model_dump(exclude_unset=True)

    if "name" in updates and updates["name"] is None:
        raise HTTPException(422, "Department name cannot be null")

    for field, value in updates.items():
        if field == "email" and value is not None:
            value = str(value)
        setattr(department, field, value)

    try:
        db.commit()
        db.refresh(department)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Duplicate department name")

    return {"message": "Department updated successfully"}


# DEACTIVATE DEPARTMENT
@app.delete("/departments/{department_id}")
def deactivate_department(
    department_id: int,
    db: Session = Depends(get_db)
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(404, "Department not found")

    department.is_active = False
    db.commit()

    return {"message": "Department deactivated successfully"}

@app.post("/complaints", status_code=201)
async def submit_complaint(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    description: str = Form(default=""),
    latitude: float | None = Form(default=None),
    longitude: float | None = Form(default=None),
    address: str | None = Form(default=None),
    db: Session = Depends(get_db)
):

    # Validate location coordinates
    if (latitude is None) != (longitude is None):
        raise HTTPException(
            status_code=422,
            detail="Latitude and longitude must be provided together"
        )

    if latitude is not None and not -90 <= latitude <= 90:
        raise HTTPException(422, "Invalid latitude")

    if longitude is not None and not -180 <= longitude <= 180:
        raise HTTPException(422, "Invalid longitude")

    # Read uploaded image with a size limit
    max_size = settings.max_image_size_mb * 1024 * 1024

    image_bytes = await image.read(max_size + 1)

    try:
        image_format = validate_image(image_bytes)

        image_path = save_image(
            image_bytes,
            image_format
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # Save complaint in PostgreSQL
    try:
        complaint = Complaint(
            description=description.strip() or None,
            image_path=image_path,
            latitude=latitude,
            longitude=longitude,
            address=address.strip() if address else None,
            severity=None,
            category_id=None,
            department_id=None,
            status="received",
            email_status="pending",
            ai_status="pending",
            ai_error=None,
            ai_analyzed_at=None,
        )

        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        background_tasks.add_task(
            run_background_analysis,
            complaint.id
        )

    except Exception:
        db.rollback()
        Path(image_path).unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Unable to save complaint"
        )

    return {
        "message": "Complaint submitted successfully",
        "complaint_id": complaint.id,
        "tracking_id": f"GAARD-{complaint.id:06d}",
        "status": complaint.status
    }
@app.post("/complaints/{complaint_id}/analyze")
def analyze_complaint_endpoint(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = analyze_complaint(complaint_id, db)
        return result

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="AI analysis failed. Check the complaint AI status."
        )
def run_background_analysis(complaint_id: int):
    db = SessionLocal()

    try:
        analyze_complaint(complaint_id, db)

    except Exception as error:
        print(f"AI analysis failed for complaint {complaint_id}: {error}")

    finally:
        db.close()