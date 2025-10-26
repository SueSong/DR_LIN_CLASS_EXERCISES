"""
Seed database with fake customer data

Usage:
    python -m data.seed_data
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from faker import Faker
from sqlalchemy import select
from datetime import datetime, timedelta
import random

from app.database import async_session_maker, init_db
from app.models import Customer, Order, Ticket, User
from app.auth import get_password_hash

fake = Faker()

async def seed_users():
    """Create default users"""
    async with async_session_maker() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalar_one_or_none():
            print("👤 Users already exist, skipping...")
            return
        
        users = [
            User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role="admin",
                is_active=True
            ),
            User(
                username="supervisor",
                email="supervisor@example.com",
                hashed_password=get_password_hash("super123"),
                full_name="Supervisor User",
                role="supervisor",
                is_active=True
            ),
            User(
                username="agent1",
                email="agent1@example.com",
                hashed_password=get_password_hash("agent123"),
                full_name="Agent One",
                role="agent",
                is_active=True
            ),
            User(
                username="agent2",
                email="agent2@example.com",
                hashed_password=get_password_hash("agent123"),
                full_name="Agent Two",
                role="agent",
                is_active=True
            ),
        ]
        
        session.add_all(users)
        await session.commit()
        print(f"✅ Created {len(users)} users")

async def seed_customers():
    """Create fake customers"""
    async with async_session_maker() as session:
        # Check if customers exist
        result = await session.execute(select(Customer))
        if result.scalar_one_or_none():
            print("📊 Customers already exist, skipping...")
            return
        
        customers = []
        for i in range(50):
            customer = Customer(
                name=fake.name(),
                email=fake.email(),
                phone=fake.phone_number(),
                account_number=f"ACC{str(i+1).zfill(5)}",
                tier=random.choice(["standard", "standard", "gold", "platinum"]),
                status=random.choice(["active", "active", "active", "inactive"]),
                lifetime_value=round(random.uniform(100, 10000), 2),
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 730))
            )
            customers.append(customer)
        
        session.add_all(customers)
        await session.commit()
        print(f"✅ Created {len(customers)} customers")
        
        return customers

async def seed_orders(customers):
    """Create fake orders"""
    async with async_session_maker() as session:
        # Check if orders exist
        result = await session.execute(select(Order))
        if result.scalar_one_or_none():
            print("🛒 Orders already exist, skipping...")
            return
        
        orders = []
        products = [
            "Premium Plan", "Basic Plan", "Enterprise Suite", "Pro Package",
            "Starter Kit", "Advanced Module", "Support Package", "Training Course",
            "Custom Solution", "Developer Tools", "Analytics Dashboard", "API Access"
        ]
        
        for customer in customers:
            num_orders = random.randint(1, 8)
            for j in range(num_orders):
                order = Order(
                    customer_id=customer.id,
                    order_number=f"ORD{fake.uuid4()[:8].upper()}",
                    product_name=random.choice(products),
                    amount=round(random.uniform(10, 500), 2),
                    status=random.choice(["completed", "completed", "shipped", "pending", "delivered"]),
                    order_date=datetime.utcnow() - timedelta(days=random.randint(1, 365))
                )
                orders.append(order)
        
        session.add_all(orders)
        await session.commit()
        print(f"✅ Created {len(orders)} orders")

async def seed_tickets(customers):
    """Create fake support tickets"""
    async with async_session_maker() as session:
        # Check if tickets exist
        result = await session.execute(select(Ticket))
        if result.scalar_one_or_none():
            print("🎫 Tickets already exist, skipping...")
            return
        
        tickets = []
        subjects = [
            "Billing inquiry",
            "Technical support needed",
            "Refund request",
            "Product question",
            "Account access issue",
            "Feature request",
            "Bug report",
            "Upgrade assistance",
            "Password reset",
            "Payment failed"
        ]
        
        # Create tickets for random customers
        for customer in random.sample(customers, min(30, len(customers))):
            num_tickets = random.randint(1, 3)
            for k in range(num_tickets):
                created_date = datetime.utcnow() - timedelta(days=random.randint(1, 180))
                is_resolved = random.choice([True, True, False])
                
                ticket = Ticket(
                    customer_id=customer.id,
                    ticket_number=f"TKT{str(random.randint(10000, 99999))}",
                    subject=random.choice(subjects),
                    description=fake.paragraph(),
                    status=random.choice(["resolved", "closed"]) if is_resolved else random.choice(["open", "in_progress"]),
                    priority=random.choice(["low", "low", "medium", "high"]),
                    created_at=created_date,
                    resolved_at=created_date + timedelta(days=random.randint(1, 7)) if is_resolved else None
                )
                tickets.append(ticket)
        
        session.add_all(tickets)
        await session.commit()
        print(f"✅ Created {len(tickets)} tickets")

async def main():
    """Main seeding function"""
    print("🌱 Seeding database with fake data...")
    print("-" * 50)
    
    # Initialize database
    await init_db()
    
    # Seed data
    await seed_users()
    customers = await seed_customers()
    
    if customers:
        # Get customers from DB for foreign keys
        async with async_session_maker() as session:
            result = await session.execute(select(Customer))
            customers = result.scalars().all()
        
        await seed_orders(customers)
        await seed_tickets(customers)
    
    print("-" * 50)
    print("✅ Database seeding complete!")
    print("\nDefault users created:")
    print("  - admin / admin123 (Admin)")
    print("  - supervisor / super123 (Supervisor)")
    print("  - agent1 / agent123 (Agent)")
    print("  - agent2 / agent123 (Agent)")

if __name__ == "__main__":
    asyncio.run(main())

