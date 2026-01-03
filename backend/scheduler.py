from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import SessionLocal
from checker import check_all_gateways
import atexit

# Crear scheduler
scheduler = BackgroundScheduler()

def scheduled_check():
    """
    Función que se ejecuta cada 2 minutos
    """
    print("\n⏰ Ejecutando check programado...")
    db = SessionLocal()
    try:
        check_all_gateways(db)
    finally:
        db.close()

def start_scheduler():
    """
    Inicia el scheduler
    """
    # Agregar job que se ejecuta cada 2 minutos
    scheduler.add_job(
        func=scheduled_check,
        trigger=IntervalTrigger(minutes=2),
        id='gateway_check',
        name='Check gateway status every 2 minutes',
        replace_existing=True
    )

    scheduler.start()
    print("✅ Scheduler iniciado - Checks cada 2 minutos")

    # Ejecutar un check inicial inmediatamente
    print("\n🚀 Ejecutando check inicial...")
    db = SessionLocal()
    try:
        check_all_gateways(db)
    finally:
        db.close()

    # Shutdown cuando la app termine
    atexit.register(lambda: scheduler.shutdown())