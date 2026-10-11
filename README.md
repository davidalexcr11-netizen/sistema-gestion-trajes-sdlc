# Sistema de Gestión para la Venta y Alquiler de Trajes Formales
### Práctica N.° 3: Desarrollo Colaborativo con Herramientas de IA (SDLC)

Este repositorio contiene la solución técnica y académica completa para la **Práctica 3**, aplicando las fases clásicas del SDLC (Requisitos, Diseño, Implementación, Pruebas y Despliegue) con asistencia de herramientas de Inteligencia Artificial Generativa.

---

## 📁 Estructura del Repositorio

```
sistema-trajes-sdlc/
├── .github/
│   └── workflows/
│       └── ci.yml               # Pipeline de Integración Continua (GitHub Actions)
├── app/
│   ├── main.py                  # API FastAPI y configuración de CORS
│   ├── database.py              # Sesión y motor SQLAlchemy
│   ├── models.py                # Modelos ORM relacionales
│   ├── schemas.py               # DTOs y validaciones Pydantic v2
│   ├── crud.py                  # Lógica de negocio, estados y transacciones
│   └── routers/                 # Enrutadores modulares por entidad
│       ├── clientes.py
│       ├── trajes.py
│       ├── ventas.py
│       ├── alquileres.py
│       └── pagos.py
├── tests/
│   ├── conftest.py              # Base de datos en memoria para testing
│   ├── test_unit_services.py    # Pruebas unitarias de servicios y edge cases
│   └── test_integration_flow.py # Pruebas de integración End-to-End
├── database_schema.sql          # Script DDL SQL normalizado (1FN, 2FN, 3FN)
├── openapi.yaml                 # Contrato formal de API REST (OpenAPI 3.0)
├── Dockerfile                   # Imagen Docker multi-stage (usuario no-root)
├── docker-compose.yml           # Orquestación con persistencia y healthcheck
├── CONTRIBUTING.md              # Estándares GitFlow, Conventional Commits y política de IA
├── requirements.txt             # Dependencias del proyecto
└── PRACTICA_3_INFORME_FINAL.md  # 📄 INFORME COMPLETO DE ENTREGA (10/10 pts)
```

---

## 🚀 Puesta en Marcha Local

### 1. Requisitos Previos
- Python 3.10+ instalado.
- Entorno virtual recomendado (`venv`).

### 2. Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecución del Servidor de Desarrollo
```bash
uvicorn app.main:app --reload --port 8000
```
- **Documentación Interactiva Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Documentación ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Healthcheck:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Ejecución de Pruebas Automatizadas

Para correr toda la suite de pruebas unitarias y de integración:

```bash
pytest tests/ -v
```

---

## 🐳 Ejecución con Docker

### Construir y levantar con Docker Compose:
```bash
docker-compose up --build
```

---

## 📋 Entregables de la Práctica
Todos los entregables exigidos por la rúbrica (Partes 1, 2, 3, 4 y 5, más el guion de exposición de 5 minutos) se encuentran detallados y consolidados en:
👉 **[`PRACTICA_3_INFORME_FINAL.md`](file:///C:/Users/LEGION/.gemini/antigravity/scratch/sistema-trajes-sdlc/PRACTICA_3_INFORME_FINAL.md)**
