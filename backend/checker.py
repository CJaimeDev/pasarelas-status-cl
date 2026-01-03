import requests
from datetime import datetime
from sqlalchemy.orm import Session
from models import Gateway, Check, StatusEnum

def check_gateway_status(gateway: Gateway, db: Session):
    """
    Verifica el status de una pasarela consultando su API
    y guarda el resultado en la base de datos
    """
    try:
        # Hacer request a la API de status
        start_time = datetime.now()
        response = requests.get(gateway.url, timeout=5)
        end_time = datetime.now()
        
        # Calcular tiempo de respuesta en milisegundos
        response_time = int((end_time - start_time).total_seconds() * 1000)
        
        # Parsear la respuesta JSON
        data = response.json()
        
        # Verificar el campo "status.indicator"
        status_indicator = data.get("status", {}).get("indicator", "unknown")
        
        # Mapear el indicator al estado
        status_map = {
            "none": StatusEnum.OPERATIONAL,
            "minor": StatusEnum.DEGRADED,
            "major": StatusEnum.PARTIAL_OUTAGE,
            "critical": StatusEnum.MAJOR_OUTAGE
        }
        
        status = status_map.get(status_indicator, StatusEnum.DOWN)
        
        # Guardar el check en la base de datos
        new_check = Check(
            gateway_id=gateway.id,
            timestamp=datetime.utcnow(),
            status=status,
            response_time=response_time
        )
        db.add(new_check)
        db.commit()
        
        # Emoji según el estado
        emoji_map = {
            StatusEnum.OPERATIONAL: "✅",
            StatusEnum.DEGRADED: "⚠️",
            StatusEnum.PARTIAL_OUTAGE: "🟠",
            StatusEnum.MAJOR_OUTAGE: "🔴",
            StatusEnum.DOWN: "❌"
        }
        emoji = emoji_map.get(status, "❓")
        
        print(f"{emoji} {gateway.display_name}: {status.value} ({response_time}ms)")
        
        return {
            "gateway": gateway.name,
            "status": status.value,
            "response_time": response_time
        }
        
    except requests.exceptions.Timeout:
        # Timeout = DOWN
        new_check = Check(
            gateway_id=gateway.id,
            timestamp=datetime.utcnow(),
            status=StatusEnum.DOWN,
            response_time=None
        )
        db.add(new_check)
        db.commit()
        
        print(f"❌ {gateway.display_name}: DOWN (Timeout)")
        
        return {
            "gateway": gateway.name,
            "status": "DOWN",
            "response_time": None,
            "error": "timeout"
        }
        
    except Exception as e:
        # Cualquier otro error = DOWN
        new_check = Check(
            gateway_id=gateway.id,
            timestamp=datetime.utcnow(),
            status=StatusEnum.DOWN,
            response_time=None
        )
        db.add(new_check)
        db.commit()
        
        print(f"❌ {gateway.display_name}: DOWN ({str(e)})")
        
        return {
            "gateway": gateway.name,
            "status": "DOWN",
            "response_time": None,
            "error": str(e)
        }

def check_all_gateways(db: Session):
    """
    Verifica el status de todas las pasarelas
    """
    gateways = db.query(Gateway).all()
    results = []
    
    print(f"\n🔍 Verificando {len(gateways)} pasarelas...")
    
    for gateway in gateways:
        result = check_gateway_status(gateway, db)
        results.append(result)
    
    print(f"✅ Verificación completada\n")
    
    return results