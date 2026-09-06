# Arquitectura y Escalabilidad

Este proyecto fue diseñado siguiendo principios avanzados de ingeniería de software, específicamente el patrón **Functional Core, Imperative Shell (FCIS)** y el principio de **Abierto/Cerrado (Open/Closed Principle)** mediante una **Arquitectura de Plugins dinámicos**.

## Diagrama de Flujo

El ciclo de vida de los datos fluye desde el exterior, se valida en el centro puramente funcional, vuelve a interactuar con el exterior para el enriquecimiento, y finalmente se emite.

```text
+-------------------+       +-----------------------+       +-------------------+
| 1. JSON Alert     | ----> | 2. Functional Core    | ----> | 3. Validated IoCs |
| (Raw Data)        |       |    (IoCExtractor)     |       |    (Pydantic)     |
+-------------------+       +-----------------------+       +-------------------+
                                                                     |
                                                                     v
+-------------------+       +-----------------------+       +-------------------+
| 6. CLI Output     | <---- | 5. Output Formatter   | <---- | 4. Imperative Shell|
| (JSON / Markdown) |       |    (Plugin Pattern)   |       |    (API Providers) |
+-------------------+       +-----------------------+       +-------------------+
```

## El Núcleo Funcional (Functional Core)
Toda la lógica de extracción de indicadores reside en `src/core/ioc_extractor.py`. Utiliza Expresiones Regulares (Regex) complejas para analizar campos de texto desestructurados y devuelve un modelo validado estáticamente con Pydantic.
Esta capa **no hace peticiones a internet** ni lee el disco duro, lo que permite que sea 100% testeable mediante pruebas unitarias en milisegundos y totalmente libre de efectos secundarios.

## La Capa de Red (Imperative Shell)
La interacción con el mundo exterior se realiza a través del paquete `src/providers/`.
Existe una clase abstracta principal `BaseProvider` (Patrón Template Method / Strategy) que estandariza el manejo de errores (como los Timeouts y el Rate Limit HTTP 429). Absolutamente todos los proveedores deben heredar de esta clase, asegurando que ningún proveedor pueda crashear la aplicación principal.

## Extensibilidad: Arquitectura de Plugins

El orquestador (`src/main.py`) **no tiene proveedores ni formateadores "hardcodeados"**. Utiliza las librerías `pkgutil` e `importlib` (nativas de Python) para escanear las carpetas `src/providers/` y `src/formatters/` en tiempo real.

### ¿Cómo agregar un nuevo Proveedor?

Gracias a esta arquitectura, escalar el ecosistema del proyecto no requiere modificar el script principal, cumpliendo el OCP:

1. **Crear el Archivo:** Crea un nuevo archivo en la carpeta correspondiente, ej. `src/providers/shodan.py`.
2. **Crear la Clase:** Define una clase `ShodanProvider` que herede obligatoriamente de `BaseProvider`.
3. **Llave API:** Agrega la variable `SHODAN_API_KEY` a tu archivo `.env`.
4. **Magia de Autodescubrimiento:** ¡Listo! Al ejecutar `python src/main.py --help`, el orquestador descubrirá automáticamente tu clase, extraerá el nombre y generará la bandera `--shodan` en la interfaz de comandos. El comportamiento es idéntico al agregar un nuevo Formato en `src/formatters/`.
