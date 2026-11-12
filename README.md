# 🥩 API Multi-Agente Asíncrona - Charcutería La Merced (Módulo 7)

API REST desarrollada con **FastAPI**, persistencia de estado con **Redis**, observabilidad con **LangSmith** y flujo **Human-in-the-Loop (HITL)** para la pre-entrega de Coderhouse.

---

## 🚀 Instrucciones de Configuración y Ejecución

1. **Levantar Redis mediante Docker Compose:**
   ```bash
   docker compose up -d

---

### 🧪 Pruebas y Concurrencia
El proyecto incluye un script de prueba automatizado (`test_concurrent.py`) para verificar el encolado de tareas asíncronas en paralelo bajo Redis Cloud.

Para ejecutar la prueba con el servidor corriendo:
```bash
python test_concurrent.py

---

#### 📸 Evidencias del Sistema (Screenshots)
En la carpeta screenshots/ se adjuntan las capturas de referencia que documentan:

uvicorn.png: Servidor FastAPI en ejecución asincrónica procesando peticiones HTTP 200 OK.

test_concurrent.png: Ejecución exitosa de 5 peticiones concurrentes devolviendo sus respectivos job_id y estados PENDING.
