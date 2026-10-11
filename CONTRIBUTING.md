# Guía de Contribución y Estándares del Equipo (CONTRIBUTING.md)

## 1. Introducción y Propósito
Este repositorio aloja el **Sistema de Gestión para la Venta y Alquiler de Trajes Formales**, desarrollado bajo el ciclo de vida del software (SDLC) con apoyo de herramientas de Inteligencia Artificial Generativa (GitHub Copilot, ChatGPT, Claude).

El propósito de esta guía es establecer directrices claras de colaboración, control de versiones, revisión de código y uso ético/responsable de asistentes de IA.

---

## 2. Estrategia de Ramificación (Git Branching)
Adoptamos un flujo basado en **GitHub Flow adaptado para entornos académicos/colaborativos**:

- `main`: Rama de producción. Contiene código estable, probado y listo para despliegue. Protegida contra pushes directos.
- `develop`: Rama de integración donde convergen las nuevas funcionalidades antes de pasar a `main`.
- Ramas temáticas (`feature/*`): Creadas a partir de `develop` para implementar una User Story específica.
  - Ejemplo: `feature/US-01-registro-clientes`
  - Ejemplo: `feature/US-03-disponibilidad-trajes`
  - Ejemplo: `feature/US-05-alquiler-trajes`
- Ramas de corrección (`fix/*` o `hotfix/*`): Para solucionar defectos detectados en pruebas o revisión.
  - Ejemplo: `fix/conflictos-fechas-alquiler`

---

## 3. Convención de Mensajes de Commit (Conventional Commits)
Todos los commits deben ser atómicos y seguir el estándar internacional:

```
<tipo>(<alcance>): <descripción concisa en imperativo>

[cuerpo opcional detallando el motivo del cambio]
[referencia a issue o User Story opcional, ej: Ref: #US-04]
```

### Tipos admitidos:
- `feat`: Nueva funcionalidad o endpoint.
- `fix`: Corrección de un defecto o bug.
- `docs`: Modificaciones en documentación (Markdown, OpenAPI, diagramas).
- `style`: Formateo de código sin alteración lógica (PEP 8, espacios, indentación).
- `refactor`: Reestructuración de código sin cambiar comportamiento funcional.
- `test`: Incorporación o mejora de pruebas unitarias y de integración.
- `chore`: Tareas de mantenimiento, dependencias o configuración CI/CD.

---

## 4. Estándares de Código y Naming Conventions
- **Lenguaje principal:** Python 3.10+ con FastAPI y SQLAlchemy.
- **Estilo:** Adherencia estricta a PEP 8.
- **Tipado estático:** Uso obligatorio de Type Annotations (`typing`) y esquemas Pydantic para validación de entrada/salida.
- **Convenciones de nombres:**
  - Clases / Modelos / Esquemas: `PascalCase` (ej. `ClienteModel`, `AlquilerCreate`).
  - Funciones, métodos y variables: `snake_case` (ej. `verificar_disponibilidad_traje`, `fecha_devolucion_prevista`).
  - Constantes: `UPPER_SNAKE_CASE` (ej. `ESTADO_DISPONIBLE`, `TIEMPO_MAXIMO_RESPUESTA_MS`).
- **Manejo de Errores:** Lanzar siempre excepciones HTTP estándar de FastAPI (`HTTPException(status_code=..., detail=...)`) con mensajes descriptivos.

---

## 5. Política de Uso de Inteligencia Artificial Generativa (GitHub Copilot / ChatGPT)
1. **Revisión Humana Obligatoria:** Ningún bloque de código generado o completado por IA puede ser integrado directamente sin haber sido leído, analizado y comprendido por el autor del commit.
2. **Protección de Datos y Privacidad:** Queda estrictamente prohibido incluir credenciales, contraseñas, secretos o datos personales reales en los prompts de IA.
3. **Validación de Edge Cases:** Toda función asistida por IA debe acompañarse de pruebas unitarias que cubran casos borde no considerados por el modelo (ej. fechas inválidas, transacciones concurrentes).
4. **Declaración en Pull Requests:** Todo Pull Request debe indicar si se utilizó IA en la generación y detallar las correcciones humanas efectuadas.

---

## 6. Proceso de Pull Request (PR) y Code Review
1. Crear el PR hacia la rama `develop`.
2. Completar la plantilla de PR (resumen, User Story asociada, prompts de IA utilizados, evidencia de pruebas).
3. Asegurar que el pipeline de Integración Continua (GitHub Actions) finalice exitosamente (pruebas en verde).
4. Obtener la aprobación de al menos un revisor humano del equipo antes de realizar el merge.
