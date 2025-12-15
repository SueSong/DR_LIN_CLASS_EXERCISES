from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from pydantic import BaseModel
from typing import List, Optional

from ..database import get_db
from ..models import Customer, Order, Ticket

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

# Mock data for when database is not available
def get_mock_customer(query: str) -> Optional[CustomerDetailResponse]:
    """Return mock customer data for testing"""
    mock_customers = {
        "john": {
            "id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1-555-0123",
            "account_number": "ACC00123",
            "tier": "gold",
            "status": "active",
            "lifetime_value": 1250.00,
            "orders": [
                {
                    "id": 1,
                    "order_number": "ORD-12345",
                    "product_name": "Premium Subscription",
                    "amount": 99.99,
                    "status": "delivered",
                    "order_date": "2025-10-15T00:00:00"
                }
            ],
            "tickets": [
                {
                    "id": 1,
                    "ticket_number": "TKT-789",
                    "subject": "Delivery delay",
                    "status": "open",
                    "priority": "medium",
                    "created_at": "2025-10-20T00:00:00"
                }
            ]
        }
    }
    
    query_lower = query.lower()
    for key, customer in mock_customers.items():
        if (key in query_lower or 
            customer["name"].lower() in query_lower or
            customer["email"].lower() in query_lower or
            customer["phone"].replace("-", "").replace("+", "").replace(" ", "") in query_lower.replace("-", "").replace("+", "").replace(" ", "") or
            customer["account_number"].lower() in query_lower):
            return CustomerDetailResponse(**customer)
    
    return None

# Routes
@router.get("/search", response_model=Optional[CustomerDetailResponse])
async def search_customer(
    q: str = Query(..., description="Search query (name, email, phone, or account number)"),
    db: AsyncSession = Depends(get_db)
):
    """Search for a customer by name, email, phone, or account number"""
    
    try:
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
            # Try mock data as fallback
            return get_mock_customer(q)
        
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
    except Exception as e:
        # Database not available - return mock data
        print(f"Database error, using mock data: {e}")
        return get_mock_customer(q)

@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get customer by ID with full details"""
    
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        # Database not available
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

