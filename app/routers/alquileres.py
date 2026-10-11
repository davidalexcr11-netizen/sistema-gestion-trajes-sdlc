from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud, models

router = APIRouter(tags=["Alquileres y Devoluciones"])

@router.post("/alquileres", response_model=schemas.AlquilerResponse, status_code=status.HTTP_201_CREATED)
def registrar_alquiler(alquiler_in: schemas.AlquilerCreate, db: Session = Depends(get_db)):
    """Registra el alquiler de un traje con control de fechas y disponibilidad (RF-05, RF-06, US-05)."""
    return crud.create_alquiler(db=db, alquiler_in=alquiler_in)

@router.get("/alquileres/{alquiler_id}", response_model=schemas.AlquilerResponse)
def obtener_alquiler(alquiler_id: int, db: Session = Depends(get_db)):
    """Obtiene el registro de un alquiler por ID."""
    alquiler = db.query(models.Alquiler).filter(models.Alquiler.id == alquiler_id).first()
    if not alquiler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alquiler con ID {alquiler_id} no encontrado."
        )
    return alquiler

@router.post("/devoluciones", response_model=schemas.DevolucionResponse, status_code=status.HTTP_201_CREATED)
def registrar_devolucion(dev_in: schemas.DevolucionCreate, db: Session = Depends(get_db)):
    """Registra la devolución del traje, calcula penalidades y actualiza su estado (RF-07, US-06)."""
    return crud.create_devolucion(db=db, dev_in=dev_in)
