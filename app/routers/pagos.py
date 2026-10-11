from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud, models

router = APIRouter(prefix="/pagos", tags=["Pagos"])

@router.post("/", response_model=schemas.PagoResponse, status_code=status.HTTP_201_CREATED)
def registrar_pago(pago_in: schemas.PagoCreate, db: Session = Depends(get_db)):
    """Registra un pago para una venta o alquiler indicando monto y método (RF-08)."""
    return crud.create_pago(db=db, pago_in=pago_in)

@router.get("/{pago_id}", response_model=schemas.PagoResponse)
def obtener_pago(pago_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles de un pago registrado."""
    pago = db.query(models.Pago).filter(models.Pago.id == pago_id).first()
    if not pago:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pago con ID {pago_id} no encontrado."
        )
    return pago
