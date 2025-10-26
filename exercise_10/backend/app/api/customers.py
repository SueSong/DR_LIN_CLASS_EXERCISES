from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel
from typing import List, Optional

from ..database import get_db
from ..models import Customer, Order, Ticket
from ..api.auth_routes import get_current_user, User

router = APIRouter(prefix="/api/customers", tags=["Customers"])

# Pydantic schemas
class OrderResponse(BaseModel):
    id: int
    order_number: str
    product_name: str
    amount: float
    status: str
    order_date: str
    
    class Config:
        from_attributes = True

class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    subject: str
    status: str
    priority: str
    created_at: str
    
    class Config:
        from_attributes = True

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    account_number: str
    tier: str
    status: str
    lifetime_value: float
    
    class Config:
        from_attributes = True

class CustomerDetailResponse(CustomerResponse):
    orders: List[OrderResponse] = []
    tickets: List[TicketResponse] = []

# Routes
@router.get("/search", response_model=Optional[CustomerDetailResponse])
async def search_customer(
    q: str = Query(..., description="Search query (name, email, phone, or account number)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search for a customer by name, email, phone, or account number"""
    
    result = await db.execute(
        select(Customer).where(
            or_(
                Customer.name.ilike(f"%{q}%"),
                Customer.email.ilike(f"%{q}%"),
                Customer.phone.ilike(f"%{q}%"),
                Customer.account_number.ilike(f"%{q}%")
            )
        )
    )
    
    customer = result.scalar_one_or_none()
    
    if not customer:
        return None
    
    # Get related data
    orders_result = await db.execute(
        select(Order)
        .where(Order.customer_id == customer.id)
        .order_by(Order.order_date.desc())
        .limit(10)
    )
    orders = orders_result.scalars().all()
    
    tickets_result = await db.execute(
        select(Ticket)
        .where(Ticket.customer_id == customer.id)
        .order_by(Ticket.created_at.desc())
        .limit(5)
    )
    tickets = tickets_result.scalars().all()
    
    return CustomerDetailResponse(
        **customer.__dict__,
        orders=[OrderResponse(**{
            **order.__dict__,
            'order_date': order.order_date.isoformat() if order.order_date else ''
        }) for order in orders],
        tickets=[TicketResponse(**{
            **ticket.__dict__,
            'created_at': ticket.created_at.isoformat() if ticket.created_at else ''
        }) for ticket in tickets]
    )

@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get customer by ID with full details"""
    
    customer = await db.get(Customer, customer_id)
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Get related data
    orders_result = await db.execute(
        select(Order)
        .where(Order.customer_id == customer.id)
        .order_by(Order.order_date.desc())
        .limit(10)
    )
    orders = orders_result.scalars().all()
    
    tickets_result = await db.execute(
        select(Ticket)
        .where(Ticket.customer_id == customer.id)
        .order_by(Ticket.created_at.desc())
        .limit(5)
    )
    tickets = tickets_result.scalars().all()
    
    return CustomerDetailResponse(
        **customer.__dict__,
        orders=[OrderResponse(**{
            **order.__dict__,
            'order_date': order.order_date.isoformat() if order.order_date else ''
        }) for order in orders],
        tickets=[TicketResponse(**{
            **ticket.__dict__,
            'created_at': ticket.created_at.isoformat() if ticket.created_at else ''
        }) for ticket in tickets]
    )

