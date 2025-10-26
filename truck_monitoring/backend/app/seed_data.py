"""
Seed database with fake data for demonstration
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from faker import Faker

from .database import SessionLocal, engine
from .models import User, Truck, DailyStatistics, Base
from .auth import get_password_hash

fake = Faker()

# Truck image URLs (placeholder images)
TRUCK_IMAGES = [
    "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?w=800",
    "https://images.unsplash.com/photo-1519003722824-194d4455a60c?w=800",
    "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800",
    "https://images.unsplash.com/photo-1566564332803-9290c0e0fdf8?w=800",
    "https://images.unsplash.com/photo-1581824283135-0666cf353f35?w=800",
]

# Video URLs (placeholder videos)
VIDEO_URLS = [
    "https://www.youtube.com/watch?v=sample1",
    "https://www.youtube.com/watch?v=sample2",
    "https://www.youtube.com/watch?v=sample3",
]

TRUCK_TYPES = ["Container", "Flatbed", "Tanker", "Refrigerated", "Box Truck", "Dump Truck"]
LOCATIONS = ["Highway 101 North", "Highway 101 South", "Interstate 5 North", "Interstate 5 South"]
DIRECTIONS = ["Northbound", "Southbound", "Eastbound", "Westbound"]
COMPANY_NAMES = [
    "Swift Transportation", "J.B. Hunt", "Schneider National",
    "Werner Enterprises", "FedEx Freight", "UPS Freight",
    "Old Dominion", "XPO Logistics", "YRC Worldwide"
]


def seed_database():
    """Seed the database with fake data"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("📊 Database already seeded, skipping...")
            return
        
        print("🌱 Seeding database with fake data...")
        
        # Create admin user with truncated password for bcrypt
        password_admin = "admin123"[:72]  # Bcrypt max 72 bytes
        admin_user = User(
            username="admin",
            email="admin@truckmonitor.com",
            hashed_password=get_password_hash(password_admin),
            full_name="System Administrator",
            is_active=True,
            is_admin=True
        )
        db.add(admin_user)
        
        # Create regular user with truncated password for bcrypt
        password_user = "user123"[:72]  # Bcrypt max 72 bytes
        regular_user = User(
            username="user",
            email="user@truckmonitor.com",
            hashed_password=get_password_hash(password_user),
            full_name="John Doe",
            is_active=True,
            is_admin=False
        )
        db.add(regular_user)
        
        print("✅ Created users: admin/admin123 and user/user123")
        
        # Create truck data for the last 30 days
        trucks_created = 0
        daily_stats = {}
        
        for days_ago in range(30, -1, -1):
            date = datetime.now() - timedelta(days=days_ago)
            date_str = date.strftime("%Y-%m-%d")
            
            # Random number of trucks per day (20-80)
            num_trucks = random.randint(20, 80)
            
            # Track daily statistics
            daily_counts = {
                "Container": 0,
                "Flatbed": 0,
                "Tanker": 0,
                "other": 0
            }
            total_length = 0
            total_speed = 0
            hourly_counts = [0] * 24
            
            for _ in range(num_trucks):
                # Random time during the day
                hour = random.randint(0, 23)
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                pass_time = date.replace(hour=hour, minute=minute, second=second)
                
                # Random truck data
                truck_type = random.choice(TRUCK_TYPES)
                length = round(random.uniform(8.0, 18.0), 1)
                speed = round(random.uniform(50.0, 90.0), 1)
                
                truck = Truck(
                    truck_number=f"TRK{fake.unique.random_number(digits=6)}",
                    license_plate=fake.license_plate(),
                    truck_type=truck_type,
                    length_meters=length,
                    weight_tons=round(random.uniform(5.0, 40.0), 1),
                    speed_kmh=speed,
                    location=random.choice(LOCATIONS),
                    direction=random.choice(DIRECTIONS),
                    pass_time=pass_time,
                    date=date_str,
                    image_url=random.choice(TRUCK_IMAGES),
                    video_url=random.choice(VIDEO_URLS),
                    thumbnail_url=random.choice(TRUCK_IMAGES),
                    company_name=random.choice(COMPANY_NAMES),
                    driver_name=fake.name(),
                    cargo_description=fake.sentence(nb_words=6),
                    notes=fake.sentence(nb_words=10) if random.random() > 0.7 else None
                )
                db.add(truck)
                
                # Update statistics
                if truck_type in daily_counts:
                    daily_counts[truck_type] += 1
                else:
                    daily_counts["other"] += 1
                total_length += length
                total_speed += speed
                hourly_counts[hour] += 1
                
                trucks_created += 1
            
            # Create daily statistics
            peak_hour = hourly_counts.index(max(hourly_counts))
            daily_stat = DailyStatistics(
                date=date_str,
                total_trucks=num_trucks,
                avg_length=round(total_length / num_trucks, 2),
                avg_speed=round(total_speed / num_trucks, 2),
                peak_hour=peak_hour,
                peak_hour_count=hourly_counts[peak_hour],
                container_count=daily_counts.get("Container", 0),
                flatbed_count=daily_counts.get("Flatbed", 0),
                tanker_count=daily_counts.get("Tanker", 0),
                other_count=daily_counts["other"]
            )
            db.add(daily_stat)
        
        db.commit()
        print(f"✅ Created {trucks_created} truck records across 31 days")
        print(f"✅ Created 31 daily statistics records")
        print("🎉 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # Run this script directly to seed the database
    seed_database()

