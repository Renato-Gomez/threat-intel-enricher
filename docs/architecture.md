# Arquitectura y Flujo de Alertas de Seguridad

Este documento explica el ciclo de vida de una alerta de seguridad, desde su origen en la red corporativa hasta que es procesada por **Automated Threat Intel Enrichment Pipeline**.

## Diagrama de Flujo del Ecosistema Real

El siguiente diagrama ilustra cómo las distintas herramientas de ciberseguridad interactúan para generar la alerta en formato JSON que la aplicación procesará:

```text
[ Empleado / Endpoint ]
       │
       ├─ (Descarga Archivo) ──────> [ EDR (Ej. CrowdStrike) ]
       │                                     │
       └─ (Conexión Maliciosa) ────> [ Firewall (Ej. Palo Alto) ]
                                             │
                                             ▼
                                     [ SIEM (Ej. Splunk) ]
                                     (Correlaciona y genera JSON)
                                             │
                                             ▼
                             [Threat Intel Enricher (App) ]
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
           [ AbuseIPDB API ]                               [ VirusTotal API ]
          (Analiza IPs sospechosas)                       (Analiza Hashes/Dominios)
                      │                                             │
                      └──────────────────────┬──────────────────────┘
                                             ▼
                                [ Reporte Final Enriquecido ]
                                   (Para Analista de SOC)
```

---

## Anatomía de la Alerta (Mapeo de Datos Reales)

La aplicación recibe datos en formato JSON (`data/alert_mock.json`). Cada uno de estos atributos proviene de herramientas específicas del mercado:

### 1. `alert_id` y `timestamp`

- **Qué son:** Identificadores únicos y la marca de tiempo de cuándo ocurrió el evento.
- **Origen Real:** Plataformas SIEM / XDR como **Splunk**, **Elastic Security (ELK)** o **Microsoft Sentinel**.

### 2. `severity` (Severidad)

- **Qué es:** El nivel de criticidad (HIGH, MEDIUM, LOW).
- **Origen Real:** El motor de reglas de correlación del SIEM asigna este nivel basado en el comportamiento observado.

### 3. `source_ip` (IP de Origen)

- **Qué es:** La dirección IP dentro de la red corporativa que originó la conexión.
- **Origen Real:** **EDR** instalados en las computadoras (ej. **CrowdStrike Falcon**, **SentinelOne**) o logs del Directorio Activo. Identifica a la víctima interna.

### 4. `destination_ip` (IP de Destino)

- **Qué es:** La IP externa (en internet) a la que la víctima intentó conectarse (ej. Servidor de Comando y Control).
- **Origen Real:** Firewalls perimetrales o Proxies (ej. **Palo Alto Networks**, **Fortigate**).

### 5. `payload_snippet` (Fragmento de la Carga Útil)

- **Qué es:** Un fragmento crudo del tráfico de red (ej. los encabezados HTTP). Contiene dominios maliciosos, User-Agents sospechosos, etc.
- **Origen Real:** Herramientas IDS/IPS o analizadores de tráfico (NDR) como **Suricata**, **Zeek** o **Snort** que analizan paquetes a nivel de red.

### 6. `file_hash`

- **Qué es:** La huella digital criptográfica (MD5/SHA256) del binario malicioso.
- **Origen Real:** Generado en tiempo real por el EDR de la máquina o por un entorno de _Sandbox_ dinámico antes de que el archivo logre ejecutarse completamente.
