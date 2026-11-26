from pydantic import BaseModel, Field, EmailStr


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    jurisdiction: str = Field(min_length=2, max_length=150)


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    email: EmailStr | None = None
    jurisdiction: str | None = None