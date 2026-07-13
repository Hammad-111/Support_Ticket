from pydantic import BaseModel, Field


class UserSignup(BaseModel):
    email: str
    password: str = Field(min_length=6)
    role: str = "user"


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
