# Automated Threat Intel Enrichment Pipeline

## Descripción del Proyecto

Herramienta de automatización diseñada para reducir la fricción operativa en equipos de respuesta a incidentes (SOC/CSIRT). El pipeline ingesta alertas de seguridad simuladas, extrae Indicadores de Compromiso (IoCs) mediante expresiones regulares y consulta automáticamente plataformas de Threat Intelligence (ej. AbuseIPDB, VirusTotal) para enriquecer el contexto de la amenaza.

El objetivo es minimizar la investigación manual de IPs y Hashes, entregando resultados estructurados que faciliten el triaje.

## Tecnologías y Arquitectura

- **Lenguaje:** Python 3.11
- **Diseño:** Arquitectura modular orientada a objetos (Principios SOLID).
- **Gestión de Entorno:** Micromamba/Conda
- **Calidad de Código y CI:**
  - `pre-commit` hooks (Black, Ruff)
  - GitHub Actions para testing y validación de sintaxis en cada Push/Pull Request.

## Instalación y Configuración

1.  **Clonar el repositorio:**

    ```bash
    git clone [https://github.com/TU-USUARIO/threat-intel-enricher.git](https://github.com/TU-USUARIO/threat-intel-enricher.git)
    cd threat-intel-enricher
    ```

2.  **Crear el ambiente virtual con Micromamba/Conda:**

    ```bash
    micromamba env create -f environment.yml
    micromamba activate threat-intel-enricher
    ```

3.  **Configurar Variables de Entorno:**
    Renombra `.env.example` a `.env` y agrega tus API Keys.

4.  **Instalar pre-commit:**
    ```bash
    pre-commit install
    ```

## Ejecución

(Instrucciones pendientes - En desarrollo)
