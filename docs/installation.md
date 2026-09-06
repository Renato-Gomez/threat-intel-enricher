# Guía de Instalación y Configuración

## 1. Requisitos Previos

- Python 3.11 o superior.
- Un gestor de entornos virtuales (se recomienda `micromamba`, `conda` o el clásico `venv`).

## 2. Instalación

Clona el repositorio e instala las dependencias utilizando tu gestor de paquetes favorito:

```bash
git clone <tu-repositorio>
cd threat-intel-enricher
pip install -r requirements.txt
```

*(Nota: Si utilizas el entorno provisto por defecto en el repositorio, puedes crearlo directamente ejecutando `micromamba create -f environment.yml`)*

## 3. Configuración de Variables de Entorno (API Keys)

Este proyecto fue diseñado bajo la metodología **Fail-Fast**. Si las llaves de las APIs no están configuradas correctamente, el programa se detendrá de inmediato al iniciar para evitar fallos de red silenciosos en tiempo de ejecución.

1. Copia el archivo de ejemplo para crear tu configuración local:
```bash
cp .env.example .env
```

2. Edita el archivo `.env` y agrega tus credenciales reales:
```env
ABUSEIPDB_API_KEY="tu_llave_real_aqui"
VIRUSTOTAL_API_KEY="tu_llave_real_aqui"
```

> **Nota de Escalabilidad:** La carga de configuración en este proyecto es dinámica (`src/config.py`). Si un desarrollador agrega un nuevo proveedor en el código fuente (por ejemplo, `ShodanProvider`), el sistema automáticamente buscará una variable de entorno que siga el formato estricto `NOMBREPROVEEDOR_API_KEY` (ej. `SHODAN_API_KEY`).
