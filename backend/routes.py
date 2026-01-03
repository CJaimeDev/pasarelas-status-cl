from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Gateway, Check, StatusEnum
from typing import List
from pydantic import BaseModel
from datetime import datetime, timedelta
from checker import check_all_gateways
from sqlalchemy import func

router = APIRouter(prefix="/api", tags=["gateways"])

# Schemas de respuesta
class GatewayResponse(BaseModel):
    id: int
    name: str
    display_name: str
    url: str
    
    class Config:
        from_attributes = True

class CheckResponse(BaseModel):
    id: int
    gateway_id: int
    timestamp: datetime
    status: StatusEnum
    response_time: int | None
    
    class Config:
        from_attributes = True

class GatewayStatusResponse(BaseModel):
    gateway: GatewayResponse
    last_check: CheckResponse | None
    uptime_24h: float | None
    
@router.get("/gateways", response_model=List[GatewayResponse])
def get_gateways(db: Session = Depends(get_db)):
    """Obtiene todas las pasarelas registradas"""
    gateways = db.query(Gateway).all()
    return gateways

@router.get("/gateways/{gateway_name}/checks", response_model=List[CheckResponse])
def get_gateway_checks(gateway_name: str, limit: int = 100, db: Session = Depends(get_db)):
    """Obtiene el histórico de checks de una pasarela"""
    gateway = db.query(Gateway).filter(Gateway.name == gateway_name).first()
    
    if not gateway:
        return {"error": "Gateway not found"}
    
    checks = db.query(Check).filter(
        Check.gateway_id == gateway.id
    ).order_by(Check.timestamp.desc()).limit(limit).all()
    
    return checks

@router.get("/status", response_model=List[GatewayStatusResponse])
def get_current_status(db: Session = Depends(get_db)):
    """Obtiene el status actual de todas las pasarelas con uptime 24h"""
    gateways = db.query(Gateway).all()
    result = []
    
    for gateway in gateways:
        # Obtener último check
        last_check = db.query(Check).filter(
            Check.gateway_id == gateway.id
        ).order_by(Check.timestamp.desc()).first()
        
        # Calcular uptime últimas 24h
        time_24h_ago = datetime.utcnow() - timedelta(hours=24)
        
        # Contar checks totales y OPERATIONAL en las últimas 24h
        total_checks = db.query(func.count(Check.id)).filter(
            Check.gateway_id == gateway.id,
            Check.timestamp >= time_24h_ago
        ).scalar()
        
        operational_checks = db.query(func.count(Check.id)).filter(
            Check.gateway_id == gateway.id,
            Check.timestamp >= time_24h_ago,
            Check.status == StatusEnum.OPERATIONAL
        ).scalar()
        
        # Calcular porcentaje
        if total_checks > 0:
            uptime_24h = round((operational_checks / total_checks) * 100, 2)
        else:
            uptime_24h = None
        
        result.append({
            "gateway": gateway,
            "last_check": last_check,
            "uptime_24h": uptime_24h
        })
    
    return result

@router.get("/gateways/{gateway_name}/uptime/days")
def get_uptime_by_days(gateway_name: str, days: int = 7, db: Session = Depends(get_db)):
    """
    Calcula el uptime por día para los últimos N días
    """
    from collections import defaultdict
    
    gateway = db.query(Gateway).filter(Gateway.name == gateway_name).first()
    
    if not gateway:
        return {"error": "Gateway not found"}
    
    # Fecha de inicio (hace N días)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Obtener todos los checks desde esa fecha
    checks = db.query(Check).filter(
        Check.gateway_id == gateway.id,
        Check.timestamp >= start_date
    ).order_by(Check.timestamp.asc()).all()
    
    # Agrupar por día
    checks_by_day = defaultdict(lambda: {"total": 0, "operational": 0})
    
    for check in checks:
        # Obtener fecha en formato YYYY-MM-DD
        day_key = check.timestamp.strftime('%Y-%m-%d')
        checks_by_day[day_key]["total"] += 1
        if check.status == StatusEnum.OPERATIONAL:
            checks_by_day[day_key]["operational"] += 1
    
    # Crear lista de resultados para los últimos N días
    result = []
    day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - 1 - i)
        day_key = date.strftime('%Y-%m-%d')
        day_name = day_names[date.weekday()]
        
        if day_key in checks_by_day:
            day_data = checks_by_day[day_key]
            uptime = round((day_data["operational"] / day_data["total"]) * 100, 2)
        else:
            uptime = None  # Sin datos para ese día
        
        result.append({
            "date": day_key,
            "day": day_name[:3],  # Lun, Mar, Mié...
            "uptime": uptime,
            "checks": checks_by_day[day_key]["total"] if day_key in checks_by_day else 0
        })
    
    return result



@router.post("/check")
def run_check(db: Session = Depends(get_db)):
    """Ejecuta una verificación manual de todas las pasarelas"""
    results = check_all_gateways(db)
    return {
        "message": "Verificación completada",
        "results": results
    }
    
@router.delete("/test/clear-checks/{gateway_name}")
def clear_gateway_checks(gateway_name: str, db: Session = Depends(get_db)):
    """
    TEMPORAL - Borra todos los checks de una pasarela
    """
    gateway = db.query(Gateway).filter(Gateway.name == gateway_name).first()
    
    if not gateway:
        return {"error": "Gateway not found"}
    
    # Contar checks antes
    count = db.query(Check).filter(Check.gateway_id == gateway.id).count()
    
    # Borrar todos los checks
    db.query(Check).filter(Check.gateway_id == gateway.id).delete()
    db.commit()
    
    return {
        "message": f"Checks borrados para {gateway.display_name}",
        "deleted": count
    }