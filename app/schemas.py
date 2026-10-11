from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict

# -----------------------------------------------------------------------------
# CLIENTE SCHEMAS
# -----------------------------------------------------------------------------
class ClienteBase(BaseModel):
    identificacion: str = Field(..., min_length=5, max_length=20, description="Cédula, DNI o pasaporte")
    nombres: str = Field(..., min_length=2, max_length=100)
    apellidos: str = Field(..., min_length=2, max_length=100)
    telefono: str = Field(..., min_length=7, max_length=20)
    email: EmailStr

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    fecha_registro: datetime
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# TRAJE SCHEMAS
# -----------------------------------------------------------------------------
class TrajeBase(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=30)
    tipo: str = Field(..., description="Esmoquin, Frac, Clásico, Chaqué")
    talla: str = Field(..., max_length=10)
    color: str = Field(..., max_length=30)
    precio_venta: float = Field(..., ge=0.0)
    precio_alquiler: float = Field(..., ge=0.0)
    estado: str = Field(default="DISPONIBLE", description="DISPONIBLE, ALQUILADO, VENDIDO, MANTENIMIENTO")

class TrajeCreate(TrajeBase):
    pass

class TrajeResponse(TrajeBase):
    id: int
    fecha_creacion: datetime
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# VENTA SCHEMAS
# -----------------------------------------------------------------------------
class DetalleVentaResponse(BaseModel):
    traje_id: int
    precio_unitario: float
    model_config = ConfigDict(from_attributes=True)

class VentaCreate(BaseModel):
    cliente_id: int
    traje_ids: List[int] = Field(..., min_length=1, description="Lista de identificadores de trajes")
    empleado_responsable: Optional[str] = "Empleado General"

class VentaResponse(BaseModel):
    id: int
    cliente_id: int
    fecha_venta: datetime
    total: float
    empleado_responsable: str
    estado: str
    detalles: List[DetalleVentaResponse] = []
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# ALQUILER SCHEMAS
# -----------------------------------------------------------------------------
class AlquilerCreate(BaseModel):
    cliente_id: int
    traje_id: int
    fecha_alquiler: date
    fecha_devolucion_prevista: date
    deposito_garantia: Optional[float] = 0.0

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_devolucion_prevista < self.fecha_alquiler:
            raise ValueError("La fecha prevista de devolución no puede ser anterior a la fecha de alquiler.")
        return self

class AlquilerResponse(BaseModel):
    id: int
    cliente_id: int
    traje_id: int
    fecha_alquiler: date
    fecha_devolucion_prevista: date
    valor_alquiler: float
    deposito_garantia: float
    estado: str
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# DEVOLUCIÓN SCHEMAS
# -----------------------------------------------------------------------------
class DevolucionCreate(BaseModel):
    alquiler_id: int
    estado_traje_devuelto: str = Field(..., description="BUENO, CON_DETALLES, DANIADO, INSERVIBLE")
    costo_adicional_multa: Optional[float] = Field(default=0.0, ge=0.0)
    observaciones: Optional[str] = None

class DevolucionResponse(BaseModel):
    id: int
    alquiler_id: int
    fecha_devolucion_real: datetime
    estado_traje_devuelto: str
    costo_adicional_multa: float
    observaciones: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# PAGO SCHEMAS
# -----------------------------------------------------------------------------
class PagoCreate(BaseModel):
    cliente_id: int
    venta_id: Optional[int] = None
    alquiler_id: Optional[int] = None
    monto: float = Field(..., gt=0.0)
    metodo_pago: str = Field(..., description="EFECTIVO, TARJETA_DEBITO, TARJETA_CREDITO, TRANSFERENCIA")

class PagoResponse(BaseModel):
    id: int
    cliente_id: int
    venta_id: Optional[int] = None
    alquiler_id: Optional[int] = None
    monto: float
    fecha_pago: datetime
    metodo_pago: str
    estado: str
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------------------------------------------
# ERROR RESPONSE
# -----------------------------------------------------------------------------
class ErrorResponse(BaseModel):
    detail: str
