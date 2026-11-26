from backend.database.session import SessionLocal
from backend.database.models import (
    IssueCategory,
    Department,
    CategoryRouting
)


DEFAULT_CATEGORIES = [
    ("Pothole", "Road surface damage"),
    ("Garbage", "Garbage accumulation"),
    ("Broken Streetlight", "Streetlight not working"),
    ("Drainage Overflow", "Overflowing drainage"),
    ("Damaged Signage", "Damaged or missing road signage"),
    ("Water Leakage", "Water pipeline leakage"),
    ("Fallen Tree", "Fallen trees blocking public areas"),
    ("Road Damage", "Other road infrastructure damage"),
]

DEFAULT_DEPARTMENTS = [
    ("Roads and Engineering", "roads@example.com", "Demo Municipality"),
    ("Sanitation", "sanitation@example.com", "Demo Municipality"),
    ("Electrical", "electrical@example.com", "Demo Municipality"),
    ("Drainage", "drainage@example.com", "Demo Municipality"),
    ("Water Supply", "water@example.com", "Demo Municipality"),
    ("Parks and Emergency", "parks@example.com", "Demo Municipality"),
]


def seed_database():
    db = SessionLocal()

    try:
        for name, description in DEFAULT_CATEGORIES:
            exists = db.query(IssueCategory).filter_by(name=name).first()

            if not exists:
                db.add(
                    IssueCategory(
                        name=name,
                        description=description
                    )
                )

        for name, email, jurisdiction in DEFAULT_DEPARTMENTS:
            exists = db.query(Department).filter_by(name=name).first()

            if not exists:
                db.add(
                    Department(
                        name=name,
                        email=email,
                        jurisdiction=jurisdiction
                    )
                )

        db.commit()

        routing_defaults = {
            "Pothole": "Roads and Engineering",
            "Garbage": "Sanitation",
            "Broken Streetlight": "Electrical",
            "Drainage Overflow": "Drainage",
            "Damaged Signage": "Roads and Engineering",
            "Water Leakage": "Water Supply",
            "Fallen Tree": "Parks and Emergency",
            "Road Damage": "Roads and Engineering",
        }

        for category_name, department_name in routing_defaults.items():
            category = db.query(IssueCategory).filter_by(
                name=category_name
            ).first()

            department = db.query(Department).filter_by(
                name=department_name
            ).first()

            exists = db.query(CategoryRouting).filter_by(
                category_id=category.id,
                department_id=department.id
            ).first()

            if not exists:
                db.add(
                    CategoryRouting(
                        category_id=category.id,
                        department_id=department.id
                    )
                )

        db.commit()
        print("Default GAARD data inserted successfully!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()