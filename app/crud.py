from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

# -----------------------------------------------------------------------------
# CLIENTES CRUD
# -----------------------------------------------------------------------------
def get_cliente_by_identificacion(db: Session, identificacion: str) -> Optional[models.Cliente]:
    return db.query(models.Cliente).filter(models.Cliente.identificacion == identificacion).first()

def get_cliente_by_email(db: Session, email: str) -> Optional[models.Cliente]:
    return db.query(models.Cliente).filter(models.Cliente.email == email).first()

def get_cliente(db: Session, cliente_id: int) -> Optional[models.Cliente]:
    return db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()

def get_clientes(db: Session, skip: int = 0, limit: int = 100, query: Optional[str] = None) -> List[models.Cliente]:
    q = db.query(models.Cliente)
    if query:
        search = f"%{query}%"
        q = q.filter(
            (models.Cliente.nombres.ilike(search)) |
            (models.Cliente.apellidos.ilike(search)) |
            (models.Cliente.identificacion.ilike(search))
        )
    return q.offset(skip).limit(limit).all()

def create_cliente(db: Session, cliente: schemas.ClienteCreate) -> models.Cliente:
    if get_cliente_by_identificacion(db, cliente.identificacion):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un cliente registrado con la identificación {cliente.identificacion}"
        )
    if get_cliente_by_email(db, cliente.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un cliente registrado con el correo {cliente.email}"
        )
    db_cliente = models.Cliente(
        identificacion=cliente.identificacion,
        nombres=cliente.nombres,
        apellidos=cliente.apellidos,
        telefono=cliente.telefono,
        email=cliente.email
    )
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

# -----------------------------------------------------------------------------
# TRAJES CRUD
# -----------------------------------------------------------------------------
def get_traje_by_codigo(db: Session, codigo: str) -> Optional[models.Traje]:
    return db.query(models.Traje).filter(models.Traje.codigo == codigo).first()

def get_traje(db: Session, traje_id: int) -> Optional[models.Traje]:
    return db.query(models.Traje).filter(models.Traje.id == traje_id).first()

def create_traje(db: Session, traje: schemas.TrajeCreate) -> models.Traje:
    if get_traje_by_codigo(db, traje.codigo):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un traje registrado con el código {traje.codigo}"
        )
    db_traje = models.Traje(
        codigo=traje.codigo,
        tipo=traje.tipo,
        talla=traje.talla,
        color=traje.color,
        precio_venta=traje.precio_venta,
        precio_alquiler=traje.precio_alquiler,
        estado=traje.estado.upper()
    )
    db.add(db_traje)
    db.commit()
    db.refresh(db_traje)
    return db_traje

def get_trajes_filtrados(
    db: Session,
    tipo: Optional[str] = None,
    talla: Optional[str] = None,
    color: Optional[str] = None,
    solo_disponibles: bool = True
) -> List[models.Traje]:
    q = db.query(models.Traje)
    if solo_disponibles:
        q = q.filter(models.Traje.estado == "DISPONIBLE")
    if tipo:
        q = q.filter(models.Traje.tipo.ilike(f"%{tipo}%"))
    if talla:
        q = q.filter(models.Traje.talla == talla)
    if color:
        q = q.filter(models.Traje.color.ilike(f"%{color}%"))
    return q.all()

# -----------------------------------------------------------------------------
# VENTAS CRUD
# -----------------------------------------------------------------------------
def create_venta(db: Session, venta_in: schemas.VentaCreate) -> models.Venta:
    cliente = get_cliente(db, venta_in.cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El cliente con ID {venta_in.cliente_id} no existe."
        )

    trajes_seleccionados: List[models.Traje] = []
    total = 0.0

    for tid in venta_in.traje_ids:
        traje = get_traje(db, tid)
        if not traje:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El traje con ID {tid} no existe en el catálogo."
            )
        if traje.estado != "DISPONIBLE":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El traje '{traje.codigo}' no está DISPONIBLE (estado actual: {traje.estado})."
            )
        trajes_seleccionados.append(traje)
        total += traje.precio_venta

    db_venta = models.Venta(
        cliente_id=cliente.id,
        total=total,
        empleado_responsable=venta_in.empleado_responsable or "Empleado General",
        estado="COMPLETADA"
    )
    db.add(db_venta)
    db.flush()

    for traje in trajes_seleccionados:
        detalle = models.DetalleVenta(
            venta_id=db_venta.id,
            traje_id=traje.id,
            precio_unitario=traje.precio_venta
        )
        db.add(detalle)
        traje.estado = "VENDIDO"

    db.commit()
    db.refresh(db_venta)
    return db_venta

# -----------------------------------------------------------------------------
# ALQUILERES CRUD
# -----------------------------------------------------------------------------
def create_alquiler(db: Session, alquiler_in: schemas.AlquilerCreate) -> models.Alquiler:
    cliente = get_cliente(db, alquiler_in.cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El cliente con ID {alquiler_in.cliente_id} no existe."
        )

    traje = get_traje(db, alquiler_in.traje_id)
    if not traje:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El traje con ID {alquiler_in.traje_id} no existe."
        )

    if traje.estado != "DISPONIBLE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El traje '{traje.codigo}' no está disponible para alquiler (estado: {traje.estado})."
        )

    db_alquiler = models.Alquiler(
        cliente_id=cliente.id,
        traje_id=traje.id,
        fecha_alquiler=alquiler_in.fecha_alquiler,
        fecha_devolucion_prevista=alquiler_in.fecha_devolucion_prevista,
        valor_alquiler=traje.precio_alquiler,
        deposito_garantia=alquiler_in.deposito_garantia or 0.0,
        estado="ACTIVO"
    )
    db.add(db_alquiler)
    traje.estado = "ALQUILADO"

    db.commit()
    db.refresh(db_alquiler)
    return db_alquiler

# -----------------------------------------------------------------------------
# DEVOLUCIONES CRUD
# -----------------------------------------------------------------------------
def create_devolucion(db: Session, dev_in: schemas.DevolucionCreate) -> models.Devolucion:
    alquiler = db.query(models.Alquiler).filter(models.Alquiler.id == dev_in.alquiler_id).first()
    if not alquiler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El alquiler con ID {dev_in.alquiler_id} no existe."
        )

    if alquiler.estado != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El alquiler con ID {dev_in.alquiler_id} ya fue devuelto o no está activo (estado: {alquiler.estado})."
        )

    db_dev = models.Devolucion(
        alquiler_id=alquiler.id,
        estado_traje_devuelto=dev_in.estado_traje_devuelto.upper(),
        costo_adicional_multa=dev_in.costo_adicional_multa or 0.0,
        observaciones=dev_in.observaciones
    )
    db.add(db_dev)

    # Actualizar estado de alquiler
    alquiler.estado = "DEVUELTO"

    # Actualizar estado del traje devuelto
    traje = alquiler.traje
    if dev_in.estado_traje_devuelto.upper() in ["BUENO", "CON_DETALLES"]:
        traje.estado = "DISPONIBLE"
    else:
        # Si fue devuelto dañado o inservible, pasa a mantenimiento
        traje.estado = "MANTENIMIENTO"

    db.commit()
    db.refresh(db_dev)
    return db_dev

# -----------------------------------------------------------------------------
# PAGOS CRUD
# -----------------------------------------------------------------------------
def create_pago(db: Session, pago_in: schemas.PagoCreate) -> models.Pago:
    cliente = get_cliente(db, pago_in.cliente_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El cliente con ID {pago_in.cliente_id} no existe."
        )

    if pago_in.venta_id:
        venta = db.query(models.Venta).filter(models.Venta.id == pago_in.venta_id).first()
        if not venta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La venta con ID {pago_in.venta_id} no existe."
            )

    if pago_in.alquiler_id:
        alquiler = db.query(models.Alquiler).filter(models.Alquiler.id == pago_in.alquiler_id).first()
        if not alquiler:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El alquiler con ID {pago_in.alquiler_id} no existe."
            )

    db_pago = models.Pago(
        cliente_id=cliente.id,
        venta_id=pago_in.venta_id,
        alquiler_id=pago_in.alquiler_id,
        monto=pago_in.monto,
        metodo_pago=pago_in.metodo_pago.upper(),
        estado="COMPLETADO"
    )
    db.add(db_pago)
    db.commit()
    db.refresh(db_pago)
    return db_pago
