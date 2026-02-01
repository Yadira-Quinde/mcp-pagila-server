# Interfaz Inteligente para Base de Datos Pagila (MCP)

Este proyecto representa la convergencia entre la Inteligencia Artificial y la gestión de bases de datos relacionales. Se trata de una implementación técnica de un servidor **MCP (Model Context Protocol)** que permite a un modelo de lenguaje (LLM) actuar como un analista de datos experto sobre la base de datos **Pagila**. 

A diferencia de una conexión directa, este sistema interpone una capa de lógica programada en Python que traduce el lenguaje natural en consultas SQL precisas, garantizando que el acceso a la información sea siempre seguro, auditable y optimizado para la toma de decisiones.

# Pagila MCP Server

Este proyecto es un servidor funcional basado en el **Model Context Protocol (MCP)** para interactuar de forma inteligente y segura con la base de datos de alquiler de películas **Pagila**.

## Características
- **Seguridad:** Filtros preventivos de comandos DML (bloqueo de DELETE, UPDATE, INSERT) y validación de sentencias SELECT.
- **Inteligencia:** Agentes integrados para análisis de marketing, sugerencias de inventario y monitoreo de lealtad de clientes con avatares dinámicos.
- **Auditoría:** Sistema de logs persistente en `alertas_seguridad.log` que registra cada intento de violación de políticas de seguridad.
- **Eficiencia:** Conexiones asíncronas de alto rendimiento mediante la librería `asyncpg`.

## Instalación
1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/mcp-pagila-server.git](https://github.com/TU_USUARIO/mcp-pagila-server.git)
 
2. **Instalar dependencias:**
```bash
    pip install mcp asyncpg python-dotenv
```
3. **Configurar el entorno:**

Crea un archivo .env en la raíz del proyecto y completa tus credenciales:
```bash 
Ini, TOML
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_NAME=pagila
DB_HOST=localhost
DB_PORT=5432

```
4. **Ejecutar el servidor:**
```bash
python server.py
