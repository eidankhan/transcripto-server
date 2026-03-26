from sqlalchemy.orm import Session
from app.models.usage import AnonymousUsage
from datetime import date

class LimitService:
    @staticmethod
    def check_anonymous_limit(db: Session, ip: str) -> bool:
        today = date.today()
        record = db.query(AnonymousUsage).filter(AnonymousUsage.ip_address == ip).first()

        if not record:
            # First time ever for this IP
            new_record = AnonymousUsage(ip_address=ip, request_count=1, last_request_date=today)
            db.add(new_record)
            db.commit()
            return True

        # Reset count if it's a new day
        if record.last_request_date < today:
            record.request_count = 1
            record.last_request_date = today
            db.commit()
            return True

        # Check if under the 5-request limit
        if record.request_count < 5:
            record.request_count += 1
            db.commit()
            return True

        return False # Limit reached
    
    @staticmethod
    def get_anonymous_stats(db: Session):
        """
        Calculates distinct anonymous users and those who hit the limit.
        """
        # 1. Total distinct IPs in our tracking table
        total_anon = db.query(AnonymousUsage).count()
        
        # 2. Users who have reached 5 (or more) requests
        power_guests = db.query(AnonymousUsage).filter(AnonymousUsage.request_count >= 5).count()
        
        return {
            "total_anonymous": total_anon,
            "power_guests": power_guests
        }