from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websocket import notify
from app.celery_app.tasks import log_reply, send_email
from app.core.deps import get_current_user
from app.core.rate_limit import limiter
from app.db.database import get_db
from app.models.reply import Reply
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import (
    ReplyCreate,
    ReplyResponse,
    TicketCreate,
    TicketResponse,
    TicketStatusUpdate,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse)
@limiter.limit("20/minute")
async def create_ticket(
    request: Request,
    data: TicketCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ticket = Ticket(
        title=data.title,
        description=data.description,
        user_id=user.id,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.get("", response_model=list[TicketResponse])
async def list_tickets(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Ticket)
    if user.role != "agent":
        query = query.where(Ticket.user_id == user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if user.role != "agent" and ticket.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return ticket


@router.post("/{ticket_id}/replies", response_model=ReplyResponse)
async def add_reply(
    ticket_id: int,
    data: ReplyCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role != "agent":
        raise HTTPException(status_code=403, detail="Agents only")

    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    reply = Reply(message=data.message, ticket_id=ticket.id, user_id=user.id)
    db.add(reply)
    await db.commit()
    await db.refresh(reply)
    await notify(ticket_id, {"type": "reply", "message": reply.message})
    log_reply.delay(ticket_id, reply.message)
    send_email.delay(ticket_id, reply.message)
    return reply


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def update_status(
    ticket_id: int,
    data: TicketStatusUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.role != "agent":
        raise HTTPException(status_code=403, detail="Agents only")

    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = data.status
    await db.commit()
    await db.refresh(ticket)
    await notify(ticket_id, {"type": "status", "status": ticket.status})
    return ticket
