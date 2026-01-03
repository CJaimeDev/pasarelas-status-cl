from database import SessionLocal
from models import Gateway

def seed_gateways():
    """Inserta las pasarelas iniciales si no existen"""
    db = SessionLocal()
    
    gateways_config = [
        {
            "name": "webpay",
            "display_name": "Webpay (Transbank)",
            "url": "https://status.transbankdevelopers.cl/api/v2/status.json",
        },
        {
            "name": "mercadopago",
            "display_name": "Mercado Pago",
            "url": "https://status.mercadopago.com/api/v2/status.json",
        },
        {
            "name": "khipu",
            "display_name": "Khipu",
            "url": "https://status.khipu.com/api/v2/status.json",
        }
    ]
    
    for gw_config in gateways_config:
        # Verificar si ya existe
        exists = db.query(Gateway).filter(
            Gateway.name == gw_config["name"]
        ).first()
        
        if not exists:
            gateway = Gateway(**gw_config)
            db.add(gateway)
            print(f"✅ Pasarela creada: {gw_config['display_name']}")
        else:
            print(f"⏭️  Pasarela ya existe: {gw_config['display_name']}")
    
    db.commit()
    db.close()