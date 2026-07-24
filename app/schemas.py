from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    rollno: int
    email: EmailStr
    phone: str