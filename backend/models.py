from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class StatusEnum(str, enum.Enum):
    OPERATIONAL = "OPERATIONAL"           # Indicator: none
    DEGRADED = "DEGRADED"                 # Indicator: minor
    PARTIAL_OUTAGE = "PARTIAL_OUTAGE"     # Indicator: major
    MAJOR_OUTAGE = "MAJOR_OUTAGE"         # Indicator: critical
    DOWN = "DOWN"                          # Timeout/Error

class Gateway(Base):
    __tablename__ = "gateways"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Check(Base):
    __tablename__ = "checks"
    
    id = Column(Integer, primary_key=True, index=True)
    gateway_id = Column(Integer, ForeignKey("gateways.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(Enum(StatusEnum), nullable=False)
    response_time = Column(Integer, nullable=True)  # milisegundos