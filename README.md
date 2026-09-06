# Threat Intel Enricher

Un orquestador de Inteligencia de Amenazas (Threat Intelligence) altamente escalable, diseñado para extraer automáticamente Indicadores de Compromiso (IoCs) desde alertas de seguridad y enriquecerlos consultando múltiples proveedores externos (como AbuseIPDB y VirusTotal).

## Características Principales

- **Arquitectura de Plugins Dinámica:** El sistema auto-descubre nuevos proveedores y formateadores en tiempo de ejecución. Agregar un nuevo proveedor no requiere modificar el código núcleo de la aplicación (cumplimiento total del Open/Closed Principle).
- **Núcleo Funcional (Functional Core):** La extracción de IoCs (IPs, Dominios, Hashes) se realiza mediante expresiones regulares puras y validación estricta con Pydantic, garantizando un entorno 100% testeable y sin efectos secundarios.
- **Capa de Red Resiliente:** Manejo centralizado de tiempos de espera (timeouts) y límites de peticiones (rate limits HTTP 429) a través de una clase abstracta base.
- **Formatos de Salida Flexibles:** Exportación selectiva de reportes en formato JSON o Markdown.

## Documentación Detallada

Para comprender a fondo el diseño, configuración y las reglas de este proyecto, revisa la siguiente documentación técnica:

- [Guía de Instalación y Configuración](docs/installation.md)
- [Arquitectura y Escalabilidad (Guía para Desarrolladores)](docs/architecture.md)
- [Convenciones y Reglas de Testing](CONVENTIONS.md)

## Uso de la CLI

El orquestador cuenta con una interfaz de línea de comandos (CLI) autogenerada que permite seleccionar qué proveedores ejecutar y en qué formato emitir el reporte.

### Menú de Ayuda
Para ver todas las opciones y módulos auto-descubiertos:
```bash
python src/main.py --help
```

### Ejemplos de Ejecución

**1. Ejecutar todos los proveedores y obtener el reporte en JSON (por defecto):**
```bash
python src/main.py
```

**2. Ejecutar solo VirusTotal y obtener el reporte en Markdown:**
```bash
python src/main.py --virustotal --format markdown
```

**3. Ejecutar AbuseIPDB y VirusTotal explícitamente con salida en JSON:**
```bash
python src/main.py --abuseipdb --virustotal --format json
```

## Ejemplo Práctico (Caso de Uso)

Para entender cómo funciona el orquestador de principio a fin, veamos un escenario real.

### 1. Los Datos de Entrada (Alerta JSON)
Supongamos que nuestro SIEM detecta actividad sospechosa y genera el siguiente archivo (`data/alert_mock.json`):
```json
{
  "alert_id": "ALT-9921",
  "severity": "High",
  "destination_ip": "8.8.8.8",
  "file_hash": "44d88612fea8a8f36de82e1278abb02f",
  "payload_snippet": "GET /malware HTTP/1.1\r\nHost: evil-malware.com\r\n"
}
```

### 2. Ejecución de la Herramienta
El analista de seguridad decide investigar esta alerta consultando únicamente **VirusTotal** y solicita que la salida sea en formato **Markdown** (ideal para copiar y pegar en un ticket de Jira o Notion):
```bash
python src/main.py --virustotal --format markdown
```

### 3. El Resultado (Output)
El orquestador hace su trabajo: extrae automáticamente la IP (`8.8.8.8`), el dominio oculto en el snippet (`evil-malware.com`) y el Hash, consulta la API de VirusTotal, y genera el siguiente reporte estructurado:

```markdown
# Threat Intelligence Report: ALT-9921
**Severity:** High

## IP Addresses
### `8.8.8.8`
- **VirusTotal:**
  - malicious: 0
  - suspicious: 0
  - harmless: 88
  - undetected: 5

## File Hashes
### `44d88612fea8a8f36de82e1278abb02f`
- **VirusTotal:**
  - malicious: 62
  - suspicious: 0
  - harmless: 0
  - undetected: 12
```
