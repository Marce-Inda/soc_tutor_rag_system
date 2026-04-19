from mcp.server.fastmcp import FastMCP

# Inicializar FastMCP Server
mcp = FastMCP("edr_containment_server")

# Herramienta MCP para "Isolate Host"
@mcp.tool()
def isolate_host(hostname: str) -> str:
    """Executes a simulated EDR host isolation command on a target hostname. Disconnects the device from the network but keeps the management console port open."""
    if not hostname:
         return "[ERROR] Hostname no especificado."
    
    return f"[SUCCESS] Host '{hostname}' ha sido aislado exitosamente a nivel del OS. Todas las conexiones de red han sido interrumpidas excepto la consola de administración del SOC."

# Herramienta MCP para "Block IP"
@mcp.tool()
def block_ip(ip_address: str) -> str:
    """Executes a simulated Firewall/SOAR block command against an IP address."""
    if not ip_address:
         return "[ERROR] IP address no especificada."
    
    return f"[SUCCESS] La dirección IP '{ip_address}' ha sido añadida a la lista_negra (blocklist) del Firewall Perimetral de forma exitosa."

if __name__ == "__main__":
    mcp.run()
