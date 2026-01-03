from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from seed import seed_gateways
from routes import router
from scheduler import start_scheduler

app = FastAPI(
    title="Pasarelas Status CL",
    description="Monitor de pasarelas de pago chilenas",
    version="1.0.0"
)

# Configurar CORS - DEBE IR ANTES DE INCLUIR ROUTERS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas
app.include_router(router)

@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Base de datos inicializada")
    seed_gateways()
    print("✅ Datos iniciales cargados")
    start_scheduler()

@app.get("/")
def read_root():
    return {
        "app": "Pasarelas Status CL",
        "status": "running",
        "message": "API funcionando correctamente"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

