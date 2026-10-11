-- =============================================================================
-- SISTEMA DE GESTIÓN PARA LA VENTA Y ALQUILER DE TRAJES FORMALES
-- SCRIPT DDL DE BASE DE DATOS RELACIONAL (POSTGRESQL / SQLITE COMPATIBLE)
-- NORMALIZACIÓN FORMAL: 1FN, 2FN Y 3FN
-- =============================================================================

-- -----------------------------------------------------------------------------
-- TABLA: clientes
-- Cumple 1FN (atributos atómicos), 2FN y 3FN (dependencia total de la PK id)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identificacion VARCHAR(20) NOT NULL UNIQUE,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_clientes_identificacion ON clientes(identificacion);
CREATE INDEX IF NOT EXISTS idx_clientes_email ON clientes(email);

-- -----------------------------------------------------------------------------
-- TABLA: trajes
-- Almacena el inventario de trajes formales y su estado de ciclo de vida
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS trajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    tipo VARCHAR(50) NOT NULL,
    talla VARCHAR(10) NOT NULL,
    color VARCHAR(30) NOT NULL,
    precio_venta DECIMAL(10, 2) NOT NULL CHECK (precio_venta >= 0),
    precio_alquiler DECIMAL(10, 2) NOT NULL CHECK (precio_alquiler >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'DISPONIBLE' 
        CHECK (estado IN ('DISPONIBLE', 'ALQUILADO', 'VENDIDO', 'MANTENIMIENTO')),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_trajes_filtros ON trajes(tipo, talla, color, estado);
CREATE INDEX IF NOT EXISTS idx_trajes_estado ON trajes(estado);

-- -----------------------------------------------------------------------------
-- TABLA: ventas
-- Cabecera de la transacción de venta de trajes
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ventas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
    empleado_responsable VARCHAR(100) NOT NULL DEFAULT 'Empleado General',
    estado VARCHAR(20) NOT NULL DEFAULT 'COMPLETADA'
        CHECK (estado IN ('PENDIENTE', 'COMPLETADA', 'CANCELADA')),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_ventas_cliente ON ventas(cliente_id);
CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha_venta);

-- -----------------------------------------------------------------------------
-- TABLA: detalles_venta
-- Detalle de los trajes asociados a una venta (cumple 2FN al separar ítems)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS detalles_venta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    venta_id INTEGER NOT NULL,
    traje_id INTEGER NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL CHECK (precio_unitario >= 0),
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (traje_id) REFERENCES trajes(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_detalles_venta ON detalles_venta(venta_id);

-- -----------------------------------------------------------------------------
-- TABLA: alquileres
-- Control de alquileres de trajes con fechas previstas y estados
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alquileres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    traje_id INTEGER NOT NULL,
    fecha_alquiler DATE NOT NULL,
    fecha_devolucion_prevista DATE NOT NULL,
    valor_alquiler DECIMAL(10, 2) NOT NULL CHECK (valor_alquiler >= 0),
    deposito_garantia DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (deposito_garantia >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO'
        CHECK (estado IN ('ACTIVO', 'DEVUELTO', 'VENCIDO', 'CANCELADO')),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    FOREIGN KEY (traje_id) REFERENCES trajes(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_alquileres_fechas ON alquileres(fecha_alquiler, fecha_devolucion_prevista);
CREATE INDEX IF NOT EXISTS idx_alquileres_estado ON alquileres(estado);

-- -----------------------------------------------------------------------------
-- TABLA: devoluciones
-- Registro de devolución que cierra el ciclo de un alquiler (Relación 1:1)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS devoluciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alquiler_id INTEGER NOT NULL UNIQUE,
    fecha_devolucion_real TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado_traje_devuelto VARCHAR(30) NOT NULL 
        CHECK (estado_traje_devuelto IN ('BUENO', 'CON_DETALLES', 'DANIADO', 'INSERVIBLE')),
    costo_adicional_multa DECIMAL(10, 2) NOT NULL DEFAULT 0.00 CHECK (costo_adicional_multa >= 0),
    observaciones TEXT,
    FOREIGN KEY (alquiler_id) REFERENCES alquileres(id) ON DELETE RESTRICT
);

-- -----------------------------------------------------------------------------
-- TABLA: pagos
-- Gestión de transacciones monetarias asociadas a ventas o alquileres
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER NOT NULL,
    venta_id INTEGER NULL,
    alquiler_id INTEGER NULL,
    monto DECIMAL(10, 2) NOT NULL CHECK (monto > 0),
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metodo_pago VARCHAR(30) NOT NULL 
        CHECK (metodo_pago IN ('EFECTIVO', 'TARJETA_DEBITO', 'TARJETA_CREDITO', 'TRANSFERENCIA')),
    estado VARCHAR(20) NOT NULL DEFAULT 'COMPLETADO'
        CHECK (estado IN ('PENDIENTE', 'COMPLETADO', 'RECHAZADO')),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE RESTRICT,
    FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE RESTRICT,
    FOREIGN KEY (alquiler_id) REFERENCES alquileres(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_pagos_cliente ON pagos(cliente_id);
