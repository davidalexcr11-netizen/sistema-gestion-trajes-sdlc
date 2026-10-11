from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=schemas.ClienteResponse, status_code=status.HTTP_201_CREATED)
def registrar_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    """Registra un nuevo cliente validando unicidad de cédula/correo (RF-01, US-01)."""
    return crud.create_cliente(db=db, cliente=cliente)

@router.get("/", response_model=List[schemas.ClienteResponse])
def listar_clientes(
    query: Optional[str] = Query(None, description="Búsqueda por nombre o identificación"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Consulta la lista de clientes registrados."""
    return crud.get_clientes(db=db, skip=skip, limit=limit, query=query)

@router.get("/{cliente_id}", response_model=schemas.ClienteResponse)
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtiene los detalles de un cliente por su ID."""
    cliente = crud.get_cliente(db=db, cliente_id=cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente con ID {cliente_id} no encontrado."
        )
    return cliente
