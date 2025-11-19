# Sistema de Control de Grúa Viga para Proceso de Cromado

## Descripción
Sistema de simulación de control automatizado de una grúa viga utilizada en proceso de cromado por electrólisis, cumpliendo con norma ISA 5.1.

## Características
- ✅ Interfaz gráfica profesional (HMI) con visualización en tiempo real
- ✅ Control automático/manual del proceso
- ✅ Simulación de movimiento de grúa viga
- ✅ Gráficas de desempeño y posición
- ✅ Sistema de logs y registro de ciclos
- ✅ Arquitectura modular MVC
- ✅ Base de datos SQLite local

## Estructura del Proyecto
```
Grua-modelado/
├── config/              # Configuración del sistema
├── models/              # Modelos (Grúa, Proceso, Autómata)
├── controllers/         # Lógica de control
├── views/              # Interfaz gráfica HMI
├── utils/              # Utilidades y helpers
├── data/               # Base de datos SQLite
├── docs/               # Documentación técnica
├── main.py             # Punto de entrada
└── requirements.txt    # Dependencias
```

## Instalación

### Requisitos
- Python 3.8+
- pip

### Pasos
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

## Uso

### Modo Automático
1. Encender el sistema
2. Seleccionar modo AUTOMÁTICO
3. Configurar tiempo de cromado
4. Presionar botón de MARCHA
5. El ciclo se ejecutará automáticamente

### Modo Manual
1. Encender el sistema
2. Seleccionar modo MANUAL
3. Usar controles de movimiento manual
4. Controlar proceso paso a paso

## Arquitectura

### Patrón MVC (Modelo-Vista-Controlador)
- **Modelo**: Lógica del sistema (estados, posiciones, proceso)
- **Vista**: Interfaz gráfica HMI con norma ISA 5.1
- **Controlador**: Coordinación de movimientos y transiciones

### Estados del Autómata
1. REPOSO - Posición inicial
2. CARGA - Colocación de pieza
3. ASCENSO_INICIAL - Subida desde reposo
4. DESPLAZAMIENTO_CENTRO - Movimiento horizontal hacia cromado
5. DESCENSO_CROMADO - Bajada a estación de cromado
6. PROCESO_CROMADO - Inmersión y electrólisis
7. ASCENSO_POST_CROMADO - Subida después de cromado
8. DESPLAZAMIENTO_DESCARGA - Movimiento hacia descarga
9. DESCENSO_DESCARGA - Bajada a estación de descarga
10. LIBERACION_PIEZA - Depositar pieza
11. RETORNO_HOME - Regreso a posición inicial

## Base de Datos

### Tablas
- **ciclos_cromado**: Registro de cada ciclo de producción
- **estado_grua**: Histórico de posiciones y estados
- **logs_sistema**: Eventos y alarmas

## Autores
Universidad de Pamplona - Modelado y Simulación de Sistemas

## Licencia
Proyecto académico - II Corte
