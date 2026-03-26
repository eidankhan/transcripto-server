from http.client import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.user import User, UserRole
from app.models.audit import TranscriptAudit # The new model

class AdminService:
    @staticmethod
    def get_users_by_role(db: Session, role: UserRole):
        # SQLAlchemy returns the full object; 
        # the Pydantic schema in the router handles the "filtering"
        return db.query(User).filter(User.role == role).all()

    @staticmethod
    def update_user_verification(db: Session, user_id: int, is_verified: bool):
        user = db.query(User).filter(User.id == user_id, User.role == UserRole.USER).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_verified = is_verified
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def remove_user(db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id, User.role == UserRole.USER).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(user)
        db.commit()
        return True

    @staticmethod
    def get_analytics_data(db: Session):
        """
        New method for your Dashboard Stats!
        We'll expand this later with the SQL queries for DAU/MAU.
        """
        total_users = db.query(User).count()
        # Mocking for now, will add complex SQL here next
        return {
            "totals": {"users": total_users, "transcripts": 0}, 
            "engagement": {"stickiness": 0}
        }
        
    @staticmethod
    def get_dashboard_stats(db: Session, timeframe: str = "monthly"):
        now = datetime.utcnow()
        
        # Mapping timeframe to PostgreSQL intervals
        intervals = {
            "daily": ("hour", timedelta(days=1)),
            "weekly": ("day", timedelta(weeks=1)),
            "monthly": ("day", timedelta(days=30)),
            "yearly": ("month", timedelta(days=365))
        }
        
        trunc_unit, delta = intervals.get(timeframe, intervals["monthly"])
        start_date = now - delta

        # 1. Basic Totals (Always total)
        total_users = db.query(User).filter(User.role == UserRole.USER).count()
        total_transcripts = db.query(TranscriptAudit).count()

        # 2. Stickiness (DAU/MAU) - This remains a static high-level KPI
        dau = db.query(User).filter(User.last_login >= now - timedelta(days=1)).count()
        mau = db.query(User).filter(User.last_login >= now - timedelta(days=30)).count()
        stickiness = round((dau / mau * 100), 2) if mau > 0 else 0

        # 3. Dynamic Trend Query
        # Uses DATE_TRUNC to group by hour, day, or month based on selection
        trend_data = db.query(
            func.date_trunc(trunc_unit, TranscriptAudit.created_at).label('period'),
            (func.count(TranscriptAudit.id) / func.nullif(func.count(TranscriptAudit.user_id.distinct()), 0)).label('avg_usage')
        ).filter(TranscriptAudit.created_at >= start_date)\
         .group_by('period')\
         .order_by('period')\
         .all()

        return {
            "totals": {
                "users": total_users,
                "transcripts": total_transcripts,
                "sessions": dau
            },
            "engagement": {
                "stickiness": stickiness,
                "usageTrend": {
                    "labels": [row.period.strftime("%b %d" if timeframe != "yearly" else "%b %Y") for row in trend_data] or ["No Data"],
                    "values": [float(row.avg_usage) for row in trend_data] or [0]
                }
            }
        }