from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud, models

router = APIRouter(prefix="/ventas", tags=["Ventas"])

@router.post("/", response_model=schemas.VentaResponse, status_code=status.HTTP_201_CREATED)
def registrar_venta(venta_in: schemas.VentaCreate, db: Session = Depends(get_db)):
    """Registra una venta, asocia trajes, actualiza estados y calcula total (RF-04, RF-06, US-04)."""
    return crud.create_venta(db=db, venta_in=venta_in)

@router.get("/{venta_id}", response_model=schemas.VentaResponse)
def obtener_venta(venta_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles de una venta con sus trajes asociados."""
    venta = db.query(models.Venta).filter(models.Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Venta con ID {venta_id} no encontrada."
        )
    return venta
