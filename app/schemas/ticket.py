from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    user_id: int

    model_config = {"from_attributes": True}


class ReplyCreate(BaseModel):
    message: str = Field(min_length=1)


class ReplyResponse(BaseModel):
    id: int
    message: str
    ticket_id: int
    user_id: int

    model_config = {"from_attributes": True}


class TicketStatusUpdate(BaseModel):
    status: str = Field(pattern="^(open|in_progress|closed)$")
