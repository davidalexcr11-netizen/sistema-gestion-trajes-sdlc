from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import clientes, trajes, ventas, alquileres, pagos

# Crear las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestión para la Venta y Alquiler de Trajes Formales",
    description=(
        "API REST desarrollada siguiendo las fases del SDLC con asistencia de IA. "
        "Permite la administración de clientes, inventario de trajes, disponibilidad, "
        "ventas, alquileres, devoluciones y pagos."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración de CORS para integración con clientes frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de enrutadores organizados bajo el prefijo /api/v1
app.include_router(clientes.router, prefix="/api/v1")
app.include_router(trajes.router, prefix="/api/v1")
app.include_router(ventas.router, prefix="/api/v1")
app.include_router(alquileres.router, prefix="/api/v1")
app.include_router(pagos.router, prefix="/api/v1")

@app.get("/", tags=["General"])
def root():
    return {
        "sistema": "Sistema de Gestión para la Venta y Alquiler de Trajes Formales",
        "estado": "Operativo",
        "documentacion": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["General"])
def health_check():
    """Endpoint de salud para verificaciones de Docker y orquestadores."""
    return {"status": "healthy"}
