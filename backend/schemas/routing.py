from pydantic import BaseModel, Field


class RoutingCreate(BaseModel):
    category_id: int = Field(gt=0)
    department_id: int = Field(gt=0)
    priority: int = Field(default=1, ge=1)