def test_flujo_integral_cliente_alquiler_devolucion_venta_pago(client):
    """
    Prueba de Integración End-to-End:
    1. Registro de cliente.
    2. Creación de traje en catálogo.
    3. Consulta de disponibilidad por filtros.
    4. Registro de alquiler y verificación de indisponibilidad concurrente.
    5. Registro de devolución física y restablecimiento a disponible.
    6. Venta del traje y verificación de estado final VENDIDO.
    7. Registro del pago correspondiente.
    """
    # 1. Registrar Cliente
    resp_cli = client.post("/api/v1/clientes/", json={
        "identificacion": "1720304050",
        "nombres": "Roberto",
        "apellidos": "Santillán",
        "telefono": "0987654321",
        "email": "roberto.santillan@test.com"
    })
    assert resp_cli.status_code == 201
    cliente_id = resp_cli.json()["id"]

    # 2. Registrar Traje
    resp_traje = client.post("/api/v1/trajes/", json={
        "codigo": "TRJ-INT-100",
        "tipo": "Esmoquin",
        "talla": "M",
        "color": "Azul Noche",
        "precio_venta": 320.0,
        "precio_alquiler": 65.0,
        "estado": "DISPONIBLE"
    })
    assert resp_traje.status_code == 201
    traje_id = resp_traje.json()["id"]

    # 3. Consultar Disponibilidad
    resp_disp = client.get("/api/v1/trajes/disponibilidad?color=Azul&solo_disponibles=true")
    assert resp_disp.status_code == 200
    trajes_disp = resp_disp.json()
    assert len(trajes_disp) == 1
    assert trajes_disp[0]["id"] == traje_id

    # 4. Registrar Alquiler
    resp_alq = client.post("/api/v1/alquileres", json={
        "cliente_id": cliente_id,
        "traje_id": traje_id,
        "fecha_alquiler": "2026-10-12",
        "fecha_devolucion_prevista": "2026-10-15",
        "deposito_garantia": 30.0
    })
    assert resp_alq.status_code == 201
    alquiler_id = resp_alq.json()["id"]
    assert resp_alq.json()["estado"] == "ACTIVO"

    # Verificar que ya NO aparece en disponibles
    resp_disp_post = client.get("/api/v1/trajes/disponibilidad?color=Azul&solo_disponibles=true")
    assert len(resp_disp_post.json()) == 0

    # Intento de segundo alquiler sobre el mismo traje (debe fallar 400)
    resp_alq_fallo = client.post("/api/v1/alquileres", json={
        "cliente_id": cliente_id,
        "traje_id": traje_id,
        "fecha_alquiler": "2026-10-13",
        "fecha_devolucion_prevista": "2026-10-16"
    })
    assert resp_alq_fallo.status_code == 400

    # 5. Registrar Devolución
    resp_dev = client.post("/api/v1/devoluciones", json={
        "alquiler_id": alquiler_id,
        "estado_traje_devuelto": "BUENO",
        "costo_adicional_multa": 0.0,
        "observaciones": "Entrega en perfecto estado"
    })
    assert resp_dev.status_code == 201
    assert resp_dev.json()["estado_traje_devuelto"] == "BUENO"

    # Ahora el traje vuelve a estar disponible
    resp_disp_restablecido = client.get("/api/v1/trajes/disponibilidad?color=Azul&solo_disponibles=true")
    assert len(resp_disp_restablecido.json()) == 1

    # 6. Registrar Venta del Traje
    resp_venta = client.post("/api/v1/ventas/", json={
        "cliente_id": cliente_id,
        "traje_ids": [traje_id],
        "empleado_responsable": "Vendedor Estrella"
    })
    assert resp_venta.status_code == 201
    venta_id = resp_venta.json()["id"]
    assert resp_venta.json()["total"] == 320.0

    # Ya no debe estar disponible tras ser vendido
    resp_disp_vendido = client.get("/api/v1/trajes/disponibilidad?color=Azul&solo_disponibles=true")
    assert len(resp_disp_vendido.json()) == 0

    # 7. Registrar Pago de la Venta
    resp_pago = client.post("/api/v1/pagos/", json={
        "cliente_id": cliente_id,
        "venta_id": venta_id,
        "monto": 320.0,
        "metodo_pago": "TARJETA_CREDITO"
    })
    assert resp_pago.status_code == 201
    assert resp_pago.json()["estado"] == "COMPLETADO"

def test_endpoints_generales(client):
    """Verifica endpoints de salud y raíz."""
    resp_root = client.get("/")
    assert resp_root.status_code == 200
    assert resp_root.json()["estado"] == "Operativo"

    resp_health = client.get("/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "healthy"
