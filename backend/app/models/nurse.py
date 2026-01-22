from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from ..database import Base


class ShiftType(str, enum.Enum):
    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"


class Nurse(Base):
    __tablename__ = "nurses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    ward_assigned = Column(String(100))
    shift = Column(Enum(ShiftType))

    # Relationships
    user = relationship("User", back_populates="nurse")

    def __repr__(self):
        return f"<Nurse(id={self.id}, ward={self.ward_assigned}, shift={self.shift})>"
