import os
import asyncio
import asyncpg
import datetime  
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 1. Cargar variables de entorno
load_dotenv()

# 2. Inicializar el servidor MCP
mcp = FastMCP("Pagila Server")

# --- CAPA DE SEGURIDAD: CONFIGURACIÓN ---
PALABRAS_PROHIBIDAS = ["DROP", "DELETE", "UPDATE", "TRUNCATE", "ALTER", "GRANT", "INSERT"]

def registrar_alerta_seguridad(query, motivo):
    """Guarda intentos sospechosos en un archivo de log."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("alertas_seguridad.log", "a", encoding="utf-8") as f:
        f.write(f"⚠️ [{timestamp}] [BLOQUEADO] Motivo: {motivo} | Query: {query}\n")

# Función auxiliar para conectar a la BD
async def get_db_connection():
    return await asyncpg.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

@mcp.tool()
async def list_tables() -> str:
    """Lista todas las tablas disponibles en la base de datos pública de Pagila."""
    conn = await get_db_connection()
    try:
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
        """
        rows = await conn.fetch(query)
        tables = [row['table_name'] for row in rows]
        return f"Tablas encontradas en Pagila: {', '.join(tables)}"
    finally:
        # Aquí cerramos la conexión correctamente
        await conn.close()

@mcp.tool()
async def run_select_query(query: str) -> str:
    """Ejecuta una consulta SQL de solo lectura (SELECT) en la base de datos Pagila."""
    query_upper = query.upper().strip()
    
    # --- CAPA DE SEGURIDAD MEJORADA ---
    if not query_upper.startswith("SELECT"):
        registrar_alerta_seguridad(query, "COMANDO NO AUTORIZADO (No empezó con SELECT)")
        return "ERROR DE SEGURIDAD: Solo se permiten consultas SELECT."

    for palabra in PALABRAS_PROHIBIDAS:
        if palabra in query_upper:
            registrar_alerta_seguridad(query, f"PALABRA PROHIBIDA DETECTADA: {palabra}")
            return f"ERROR DE SEGURIDAD: Uso prohibido de '{palabra}'."

    if ";" in query.strip()[:-1]:
        registrar_alerta_seguridad(query, "INTENTO DE MULTI-QUERY (Inyección)")
        return "ERROR DE SEGURIDAD: No se permiten múltiples sentencias."

    # --- EJECUCIÓN ---
    conn = await get_db_connection()
    try:
        # Forzamos la sesión a solo lectura por si acaso
        await conn.execute("SET SESSION CHARACTERISTICS AS TRANSACTION READ ONLY")
        
        rows = await conn.fetch(query)
        if not rows:
            return "La consulta no devolvió resultados."
            
        columns = rows[0].keys()
        result_text = f"Resultados ({len(rows)} filas):\n"
        result_text += " | ".join(columns) + "\n"
        result_text += "-" * 50 + "\n"
        
        for row in rows:
            values = [str(val) for val in row.values()]
            result_text += " | ".join(values) + "\n"
            
        return result_text
        
    except asyncpg.PostgresError as e:
        registrar_alerta_seguridad(query, f"ERROR DB: {str(e)}")
        return f"ERROR DE BASE DE DATOS: {str(e)}"
    except Exception as e:
        return f"ERROR DEL SISTEMA: {str(e)}"
    finally:
        await conn.close()

@mcp.tool()
async def list_creative_customers() -> str:
    """Lista clientes con avatares según su nivel de lealtad."""
    conn = await get_db_connection()
    try:
        query = """
        SELECT c.first_name, c.last_name, 
               (SELECT SUM(amount) FROM payment p WHERE p.customer_id = c.customer_id) as total_spent
        FROM customer c LIMIT 10;
        """
        rows = await conn.fetch(query)
        res = "### 👥 Directorio con Avatares\n| Avatar | Nombre | Nivel |\n| :--- | :--- | :--- |\n"
        for r in rows:
            spent = float(r['total_spent'] or 0)
            avatar = "👑" if spent > 150 else "💎" if spent > 100 else "👤"
            res += f"| {avatar} | {r['first_name']} {r['last_name']} | ${spent:.2f} |\n"
        return res
    finally:
        await conn.close()

@mcp.tool()
async def business_advisor_agent() -> str:
    """Agente inteligente que analiza el inventario y sugiere estrategias de marketing."""
    conn = await get_db_connection()
    try:
        query = """
        SELECT c.name, COUNT(r.rental_id) as total_rentals
        FROM category c
        JOIN film_category fc ON c.category_id = fc.category_id
        JOIN inventory i ON fc.film_id = i.film_id
        JOIN rental r ON i.inventory_id = r.inventory_id
        GROUP BY c.name
        ORDER BY total_rentals ASC
        LIMIT 3;
        """
        rows = await conn.fetch(query)
        low_perf_cats = [r['name'] for r in rows]
        
        advice = f"🤖 **Agente Analista Informa:**\n"
        advice += f"He detectado que las categorías {', '.join(low_perf_cats)} tienen muy poco movimiento.\n"
        advice += "💡 **Sugerencia:** Deberíamos implementar una promoción 2x1 en estas categorías este fin de semana para liberar inventario."
        return advice
    finally:
        await conn.close()

if __name__ == "__main__":
    mcp.run()