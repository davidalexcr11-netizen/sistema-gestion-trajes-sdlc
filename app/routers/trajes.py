from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud

router = APIRouter(prefix="/trajes", tags=["Trajes e Inventario"])

@router.post("/", response_model=schemas.TrajeResponse, status_code=status.HTTP_201_CREATED)
def registrar_traje(traje: schemas.TrajeCreate, db: Session = Depends(get_db)):
    """Registra un nuevo traje formal en el inventario (RF-02, US-02)."""
    return crud.create_traje(db=db, traje=traje)

@router.get("/disponibilidad", response_model=List[schemas.TrajeResponse])
def consultar_disponibilidad(
    tipo: Optional[str] = Query(None, description="Tipo de traje (Esmoquin, Frac, etc.)"),
    talla: Optional[str] = Query(None, description="Talla (S, M, L, XL)"),
    color: Optional[str] = Query(None, description="Color del traje"),
    solo_disponibles: bool = Query(True, description="Filtrar solo trajes con estado DISPONIBLE"),
    db: Session = Depends(get_db)
):
    """Consulta y filtra trajes formales por características y disponibilidad (RF-03, RF-06, US-03)."""
    return crud.get_trajes_filtrados(
        db=db,
        tipo=tipo,
        talla=talla,
        color=color,
        solo_disponibles=solo_disponibles
    )

@router.get("/{traje_id}", response_model=schemas.TrajeResponse)
def obtener_traje(traje_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles de un traje por su ID."""
    traje = crud.get_traje(db=db, traje_id=traje_id)
    if not traje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Traje con ID {traje_id} no encontrado."
        )
    return traje
