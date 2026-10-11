from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Date, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from app.database import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    identificacion = Column(String(20), unique=True, nullable=False, index=True)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    telefono = Column(String(20), nullable=False)
    email = Column(String(120), unique=True, nullable=False, index=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    ventas = relationship("Venta", back_populates="cliente")
    alquileres = relationship("Alquiler", back_populates="cliente")
    pagos = relationship("Pago", back_populates="cliente")


class Traje(Base):
    __tablename__ = "trajes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, nullable=False, index=True)
    tipo = Column(String(50), nullable=False, index=True)      # Esmoquin, Frac, Clásico, Chaqué
    talla = Column(String(10), nullable=False, index=True)     # S, M, L, XL
    color = Column(String(30), nullable=False, index=True)     # Negro, Azul Marino, Gris, etc.
    precio_venta = Column(Float, nullable=False)
    precio_alquiler = Column(Float, nullable=False)
    estado = Column(String(20), default="DISPONIBLE", index=True)  # DISPONIBLE, ALQUILADO, VENDIDO, MANTENIMIENTO
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    detalles_venta = relationship("DetalleVenta", back_populates="traje")
    alquileres = relationship("Alquiler", back_populates="traje")


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    fecha_venta = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, nullable=False)
    empleado_responsable = Column(String(100), default="Empleado de Turno")
    estado = Column(String(20), default="COMPLETADA")  # PENDIENTE, COMPLETADA, CANCELADA

    cliente = relationship("Cliente", back_populates="ventas")
    detalles = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")
    pagos = relationship("Pago", back_populates="venta")


class DetalleVenta(Base):
    __tablename__ = "detalles_venta"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False)
    traje_id = Column(Integer, ForeignKey("trajes.id"), nullable=False)
    precio_unitario = Column(Float, nullable=False)

    venta = relationship("Venta", back_populates="detalles")
    traje = relationship("Traje", back_populates="detalles_venta")


class Alquiler(Base):
    __tablename__ = "alquileres"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    traje_id = Column(Integer, ForeignKey("trajes.id"), nullable=False)
    fecha_alquiler = Column(Date, nullable=False)
    fecha_devolucion_prevista = Column(Date, nullable=False)
    valor_alquiler = Column(Float, nullable=False)
    deposito_garantia = Column(Float, default=0.0)
    estado = Column(String(20), default="ACTIVO", index=True)  # ACTIVO, DEVUELTO, VENCIDO, CANCELADO

    cliente = relationship("Cliente", back_populates="alquileres")
    traje = relationship("Traje", back_populates="alquileres")
    devolucion = relationship("Devolucion", back_populates="alquiler", uselist=False)
    pagos = relationship("Pago", back_populates="alquiler")


class Devolucion(Base):
    __tablename__ = "devoluciones"

    id = Column(Integer, primary_key=True, index=True)
    alquiler_id = Column(Integer, ForeignKey("alquileres.id"), unique=True, nullable=False)
    fecha_devolucion_real = Column(DateTime, default=datetime.utcnow)
    estado_traje_devuelto = Column(String(30), nullable=False) # BUENO, CON_DETALLES, DANIADO, INSERVIBLE
    costo_adicional_multa = Column(Float, default=0.0)
    observaciones = Column(Text, nullable=True)

    alquiler = relationship("Alquiler", back_populates="devolucion")


class Pago(Base):
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=True)
    alquiler_id = Column(Integer, ForeignKey("alquileres.id"), nullable=True)
    monto = Column(Float, nullable=False)
    fecha_pago = Column(DateTime, default=datetime.utcnow)
    metodo_pago = Column(String(30), nullable=False) # EFECTIVO, TARJETA_DEBITO, TARJETA_CREDITO, TRANSFERENCIA
    estado = Column(String(20), default="COMPLETADO") # PENDIENTE, COMPLETADO, RECHAZADO

    cliente = relationship("Cliente", back_populates="pagos")
    venta = relationship("Venta", back_populates="pagos")
    alquiler = relationship("Alquiler", back_populates="pagos")
