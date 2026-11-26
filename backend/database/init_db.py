from backend.database.base import Base
from backend.database.session import engine
from backend.database import models

Base.metadata.create_all(bind=engine)

print("GAARD database tables created successfully!")