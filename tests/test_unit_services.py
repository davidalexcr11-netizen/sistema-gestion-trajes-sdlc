from datetime import date, timedelta
import pytest
from fastapi import HTTPException
from app import crud, schemas

def test_crear_cliente_exitoso(db):
    """Verifica el registro exitoso de un cliente con datos válidos (RF-01)."""
    cliente_in = schemas.ClienteCreate(
        identificacion="1712345678",
        nombres="Juan Carlos",
        apellidos="Pérez Gómez",
        telefono="0991234567",
        email="juan.perez@test.com"
    )
    cliente = crud.create_cliente(db, cliente_in)
    assert cliente.id is not None
    assert cliente.identificacion == "1712345678"
    assert cliente.email == "juan.perez@test.com"

def test_edge_case_crear_cliente_duplicado_falla(db):
    """Edge Case: El sistema debe rechazar el registro con cédula o email duplicado."""
    cliente_in = schemas.ClienteCreate(
        identificacion="1712345678",
        nombres="Juan Carlos",
        apellidos="Pérez Gómez",
        telefono="0991234567",
        email="juan.perez@test.com"
    )
    crud.create_cliente(db, cliente_in)

    with pytest.raises(HTTPException) as exc_info:
        crud.create_cliente(db, cliente_in)
    assert exc_info.value.status_code == 409
    assert "Ya existe un cliente" in exc_info.value.detail

def test_crear_traje_y_filtrar_disponibilidad(db):
    """Verifica el alta de trajes y el filtro por disponibilidad y características (RF-02, RF-03)."""
    traje1 = crud.create_traje(db, schemas.TrajeCreate(
        codigo="TRJ-001", tipo="Esmoquin", talla="M", color="Negro", precio_venta=250.0, precio_alquiler=50.0
    ))
    traje2 = crud.create_traje(db, schemas.TrajeCreate(
        codigo="TRJ-002", tipo="Frac", talla="L", color="Azul Marino", precio_venta=300.0, precio_alquiler=60.0
    ))

    # Filtrar solo negros
    resultados = crud.get_trajes_filtrados(db, color="Negro")
    assert len(resultados) == 1
    assert resultados[0].codigo == "TRJ-001"

    # Filtrar por talla
    resultados_l = crud.get_trajes_filtrados(db, talla="L")
    assert len(resultados_l) == 1
    assert resultados_l[0].codigo == "TRJ-002"

def test_alquiler_cambia_estado_a_alquilado(db):
    """Verifica que el alquiler de un traje cambie su estado a ALQUILADO (RF-05, RF-06)."""
    cliente = crud.create_cliente(db, schemas.ClienteCreate(
        identificacion="0911223344", nombres="María", apellidos="López", telefono="0987654321", email="maria@test.com"
    ))
    traje = crud.create_traje(db, schemas.TrajeCreate(
        codigo="TRJ-ALQ-1", tipo="Chaqué", talla="S", color="Gris", precio_venta=200.0, precio_alquiler=40.0
    ))

    alquiler_in = schemas.AlquilerCreate(
        cliente_id=cliente.id,
        traje_id=traje.id,
        fecha_alquiler=date.today(),
        fecha_devolucion_prevista=date.today() + timedelta(days=3),
        deposito_garantia=25.0
    )
    alquiler = crud.create_alquiler(db, alquiler_in)
    assert alquiler.id is not None
    assert alquiler.estado == "ACTIVO"
    assert traje.estado == "ALQUILADO"

def test_edge_case_alquilar_traje_no_disponible_lanza_error(db):
    """Edge Case: Impedir alquilar un traje que ya se encuentra ALQUILADO o VENDIDO."""
    cliente = crud.create_cliente(db, schemas.ClienteCreate(
        identificacion="0911223344", nombres="María", apellidos="López", telefono="0987654321", email="maria@test.com"
    ))
    traje = crud.create_traje(db, schemas.TrajeCreate(
        codigo="TRJ-NO-DISP", tipo="Clásico", talla="M", color="Negro", precio_venta=180.0, precio_alquiler=35.0
    ))
    traje.estado = "ALQUILADO"
    db.commit()

    alquiler_in = schemas.AlquilerCreate(
        cliente_id=cliente.id,
        traje_id=traje.id,
        fecha_alquiler=date.today(),
        fecha_devolucion_prevista=date.today() + timedelta(days=2)
    )

    with pytest.raises(HTTPException) as exc_info:
        crud.create_alquiler(db, alquiler_in)
    assert exc_info.value.status_code == 400
    assert "no está disponible" in exc_info.value.detail

def test_edge_case_fechas_alquiler_inversas_falla_validacion():
    """Edge Case: Validación de esquema Pydantic para fechas incongruentes."""
    with pytest.raises(ValueError) as exc_info:
        schemas.AlquilerCreate(
            cliente_id=1,
            traje_id=1,
            fecha_alquiler=date(2026, 10, 15),
            fecha_devolucion_prevista=date(2026, 10, 10)  # Fecha anterior
        )
    assert "no puede ser anterior" in str(exc_info.value)

def test_devolucion_traje_buen_estado_retorna_a_disponible(db):
    """Verifica que la devolución en buen estado restablezca el traje a DISPONIBLE (RF-07)."""
    cliente = crud.create_cliente(db, schemas.ClienteCreate(
        identificacion="1102938475", nombres="Andrés", apellidos="Paz", telefono="0998877665", email="andres@test.com"
    ))
    traje = crud.create_traje(db, schemas.TrajeCreate(
        codigo="TRJ-DEV-1", tipo="Esmoquin", talla="L", color="Blanco", precio_venta=280.0, precio_alquiler=55.0
    ))
    alquiler = crud.create_alquiler(db, schemas.AlquilerCreate(
        cliente_id=cliente.id,
        traje_id=traje.id,
        fecha_alquiler=date.today(),
        fecha_devolucion_prevista=date.today() + timedelta(days=2)
    ))

    dev_in = schemas.DevolucionCreate(
        alquiler_id=alquiler.id,
        estado_traje_devuelto="BUENO",
        costo_adicional_multa=0.0,
        observaciones="Sin manchas ni roturas"
    )
    devolucion = crud.create_devolucion(db, dev_in)
    assert devolucion.id is not None
    assert alquiler.estado == "DEVUELTO"
    assert traje.estado == "DISPONIBLE"

def test_devolucion_traje_daniado_cambia_a_mantenimiento(db):
    """Verifica que la devolución de un traje dañado actualice su estado a MANTENIMIENTO."""
    cliente = crud.create_cliente(db, schemas.ClienteCreate(
        identificacion="1102938479", nombres="Lucía", apellidos="Ramos", telefono="0998877661", email="lucia@test.com"
    ))
    traje = crud.create_traje(db, schemas.TrajeCreate(
        codigo="TRJ-DEV-DAN", tipo="Esmoquin", talla="M", color="Negro", precio_venta=280.0, precio_alquiler=55.0
    ))
    alquiler = crud.create_alquiler(db, schemas.AlquilerCreate(
        cliente_id=cliente.id,
        traje_id=traje.id,
        fecha_alquiler=date.today(),
        fecha_devolucion_prevista=date.today() + timedelta(days=2)
    ))

    dev_in = schemas.DevolucionCreate(
        alquiler_id=alquiler.id,
        estado_traje_devuelto="DANIADO",
        costo_adicional_multa=35.0,
        observaciones="Rotura de botón y tela rasgada"
    )
    crud.create_devolucion(db, dev_in)
    assert traje.estado == "MANTENIMIENTO"

def test_edge_case_devolucion_duplicada_falla(db):
    """Edge Case: No permitir registrar dos devoluciones para el mismo alquiler."""
    cliente = crud.create_cliente(db, schemas.ClienteCreate(
        identificacion="1102938499", nombres="Pedro", apellidos="Díaz", telefono="0998877600", email="pedro@test.com"
    ))
    traje = crud.create_traje(db, schemas.TrajeCreate(
        codigo="TRJ-DEV-DUP", tipo="Clásico", talla="S", color="Negro", precio_venta=210.0, precio_alquiler=45.0
    ))
    alquiler = crud.create_alquiler(db, schemas.AlquilerCreate(
        cliente_id=cliente.id,
        traje_id=traje.id,
        fecha_alquiler=date.today(),
        fecha_devolucion_prevista=date.today() + timedelta(days=1)
    ))

    dev_in = schemas.DevolucionCreate(alquiler_id=alquiler.id, estado_traje_devuelto="BUENO")
    crud.create_devolucion(db, dev_in)

    with pytest.raises(HTTPException) as exc_info:
        crud.create_devolucion(db, dev_in)
    assert exc_info.value.status_code == 400
    assert "ya fue devuelto" in exc_info.value.detail
