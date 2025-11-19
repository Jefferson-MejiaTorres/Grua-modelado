# Guía de Respuestas al Proyecto
## Sistema de Control de Grúa Viga

---

## 3.2. Análisis del Programa Generado

### 3.2.1. Identificación del Lenguaje de Programación

**Lenguaje identificado: Python 3.8+**

**Justificación basada en características sintácticas:**

1. **Sintaxis de importación:**
```python
import tkinter as tk
from datetime import datetime
from enum import Enum
```

2. **Type hints (anotaciones de tipo):**
```python
def actualizar_posicion(self, delta_tiempo: float) -> bool:
    return True
```

3. **Decoradores y docstrings:**
```python
def __init__(self):
    """Constructor de la clase"""
    pass
```

4. **Paradigma:** Orientado a objetos con soporte funcional

**Bibliotecas específicas:**
- `tkinter`: GUI multiplataforma
- `matplotlib`: Visualización de gráficas
- `sqlite3`: Base de datos (incluida en Python)
- `threading`: Concurrencia

---

### 3.2.2. Funciones y Componentes Principales

#### **Sistema de Control de Movimiento**

**Ubicación:** `models/grua.py`

```python
def actualizar_posicion(self, delta_tiempo: float) -> bool:
    """
    Control cinemático de la grúa
    - Calcula movimiento basado en velocidad y tiempo
    - Aplica límites de seguridad
    - Retorna True cuando alcanza objetivo
    """
```

**Características:**
- Control de motor horizontal (velocidad configurable)
- Control de motor vertical (velocidad independiente)
- Detección de límites por software
- Tolerancia de posicionamiento (±5 unidades)

#### **Gestión del Proceso de Cromado**

**Ubicación:** `models/proceso_cromado.py`

```python
def actualizar_proceso(self, delta_tiempo: float) -> bool:
    """
    Temporizador de inmersión
    - Acumula tiempo transcurrido
    - Calcula progreso porcentual
    - Simula espesor de depósito (Ley de Faraday)
    - Monitorea condiciones (temperatura, pH, corriente)
    """
```

**Parámetros monitoreados:**
- Tiempo de inmersión (30-600 segundos)
- Corriente de electrólisis (2.5 A nominal)
- Voltaje (12.0 V nominal)
- Temperatura del baño (20-30°C)
- pH del baño (2.0-3.0)

#### **Actualización de la Interfaz Gráfica**

**Ubicación:** `views/interfaz_hmi.py`

```python
def _actualizar_periodicamente(self):
    """
    Bucle principal de actualización (20 Hz)
    1. Actualizar modelo (controlador)
    2. Redibujar grúa en canvas
    3. Actualizar labels de estado
    4. Actualizar gráficas matplotlib
    5. Programar siguiente actualización (50ms)
    """
```

**Componentes de animación:**
- Canvas Tkinter para grúa
- Actualización a 20 FPS
- Gráficas matplotlib embebidas

#### **Manejo de Eventos**

**Ubicación:** `controllers/controlador_plc.py`

```python
# Pulsador de marcha
def _iniciar_ciclo(self):
    if self.controlador.iniciar_ciclo_automatico():
        messagebox.showinfo("Ciclo Iniciado", "...")

# Parada de emergencia
def _parada_emergencia(self):
    self.controlador.activar_parada_emergencia()
    # Detiene TODOS los movimientos inmediatamente
    # Transiciona autómata a estado EMERGENCIA

# Cambio modo manual/automático
def _cambiar_modo(self):
    modo = self.var_modo.get()
    self.controlador.cambiar_modo(modo)
```

**Eventos manejados:**
- Click en botones (binding de Tkinter)
- Cambio de radiobutton (modo operación)
- Spinbox para setpoint de tiempo
- Callbacks del controlador (patrón Observer)

#### **Inicialización del Sistema**

**Ubicación:** `views/interfaz_hmi.py` → `__init__()`

```python
def __init__(self, controlador: ControladorPLC):
    # 1. Crear ventana principal Tk
    self.root = tk.Tk()
    self.root.title(cfg.VENTANA['titulo'])
    
    # 2. Configurar posiciones de referencia
    cfg.POSICIONES = {
        'HOME': (100, 500),
        'CROMADO': (500, 200),
        'DESCARGA': (900, 500),
    }
    
    # 3. Calibración de sensores (límites)
    self.grua.limite_x_min = 50
    self.grua.limite_x_max = 950
    
    # 4. Establecer loop principal
    self._actualizar_periodicamente()  # Inicia bucle
    self.root.mainloop()  # Loop de eventos Tkinter
```

---

### 3.2.3. Arquitectura de Software Utilizada

**Patrón identificado: MVC (Modelo-Vista-Controlador)**

#### **MODELO** (`models/`)

**Archivos:**
- `automata.py` - Lógica de estados y transiciones
- `grua.py` - Posición, velocidad, estado del gancho
- `proceso_cromado.py` - Parámetros de electrólisis

**Responsabilidades:**
```python
class Grua:
    # Estado del sistema físico
    def actualizar_posicion(self): ...
    def obtener_estado(self) -> dict: ...
    
class ProcesoChromado:
    # Lógica del proceso
    def iniciar_proceso(self): ...
    def validar_parametros(self): ...
```

#### **VISTA** (`views/`)

**Archivo:** `interfaz_hmi.py`

**Responsabilidades:**
```python
class InterfazHMI:
    # Representación visual
    def _construir_panel_control(self): ...
    def _dibujar_escenario_base(self): ...
    
    # Panel de control ISA 5.1
    def _construir_instrumentacion(self): ...
    
    # Gráficas y displays
    def _actualizar_graficas(self): ...
```

#### **CONTROLADOR** (`controllers/`)

**Archivo:** `controlador_plc.py`

**Responsabilidades:**
```python
class ControladorPLC:
    # Coordinación de movimientos
    def _ejecutar_ciclo_automatico(self): ...
    
    # Gestión de transiciones
    def _on_transicion_automata(self): ...
    
    # Interfaz entre hardware simulado y GUI
    def actualizar(self): ...
    def registrar_callback_actualizacion(self): ...
```

**Flujo de datos:**
```
Usuario → VISTA (eventos) → CONTROLADOR (lógica) → MODELO (estado)
                              ↑                         ↓
                              └──── callbacks ──────────┘
```

---

### 3.2.4. Propuesta de Modificación Específica

#### **Modificación 1: Campo de texto en Estación de Cromado (TI-001)**

**Archivo a modificar:** `views/interfaz_hmi.py`

**Líneas específicas:** Alrededor de la línea 230, en función `_dibujar_estacion()`

**Código a AGREGAR:**

```python
# DESPUÉS de dibujar la estación de cromado (línea ~240)
def _dibujar_estacion(self, x, y, texto, color):
    # ... código existente ...
    
    # AGREGAR ESTE BLOQUE para estación de cromado:
    if "CROMADO" in texto:
        # Entry para tiempo de proceso (ISA TI-001)
        self.entry_tiempo_cromado = tk.Entry(
            self.canvas, width=8, 
            font=('Arial', 10, 'bold'),
            bg='white', fg='black',
            justify='center'
        )
        # Posicionar debajo de la estación
        self.canvas.create_window(
            x, y + cfg.TAMANHOS['estacion_alto'] + 30,
            window=self.entry_tiempo_cromado
        )
        self.entry_tiempo_cromado.insert(0, "120 s")
        
        # Label de identificación ISA 5.1
        self.canvas.create_text(
            x, y + cfg.TAMANHOS['estacion_alto'] + 50,
            text="TI-001",  # Time Indicator según ISA 5.1
            fill='#00FFFF',  # Color cian (proceso activo)
            font=('Arial', 9, 'bold')
        )
```

**Parámetros ISA 5.1:**
- `TI-001`: Time Indicator (Indicador de Tiempo)
- Color: `#00FFFF` (Cian) - Instrumentación de proceso
- Fuente: Arial Bold 9pt según estándar industrial

#### **Modificación 2: Campo de tamaño máximo en Estación de Descarga**

**Archivo a modificar:** `views/interfaz_hmi.py`

**Código a AGREGAR en la misma función:**

```python
    # Para estación de descarga
    if "DESCARGA" in texto:
        # Entry para tamaño máximo (ISA SI-003)
        self.entry_tamano_max = tk.Entry(
            self.canvas, width=10,
            font=('Arial', 10, 'bold'),
            bg='white', fg='black',
            justify='center'
        )
        self.canvas.create_window(
            x, y + cfg.TAMANHOS['estacion_alto'] + 30,
            window=self.entry_tamano_max
        )
        self.entry_tamano_max.insert(0, "500 mm")
        
        # Label ISA 5.1
        self.canvas.create_text(
            x, y + cfg.TAMANHOS['estacion_alto'] + 50,
            text="SI-003",  # Size Indicator
            fill='#FFA500',  # Color naranja (advertencia/límite)
            font=('Arial', 9, 'bold')
        )
```

**Identificación ISA 5.1:**
- `SI-003`: Size Indicator (Indicador de Tamaño)
- Color: `#FFA500` (Naranja) - Límite/Advertencia

---

### 3.2.5. Artefactos de Diseño

#### **Diagrama de Flujo Principal**

```
[INICIO]
   ↓
[Verificar sistema encendido] → NO → [FIN]
   ↓ SÍ
[Verificar modo automático] → NO → [Modo Manual]
   ↓ SÍ
[Esperar pulsador MARCHA]
   ↓
┌──[CICLO AUTOMÁTICO]──────────────────┐
│                                      │
│  [Estado: CARGA]                     │
│     ↓                                │
│  [Cerrar gancho]                     │
│     ↓                                │
│  [Estado: ASCENSO_INICIAL]           │
│     ↓                                │
│  [Mover a tope superior]             │
│     ↓                                │
│  [Estado: DESPLAZAMIENTO_CENTRO]     │
│     ↓                                │
│  [Mover horizontalmente a cromado]   │
│     ↓                                │
│  [Estado: DESCENSO_CROMADO]          │
│     ↓                                │
│  [Sumergir en estación]              │
│     ↓                                │
│  [Estado: PROCESO_CROMADO]           │
│     ↓                                │
│  [Esperar tiempo configurado]        │
│     ↓                                │
│  [Verificar calidad] → FALLO → [Alarma]
│     ↓ OK                             │
│  [Estado: ASCENSO_POST_CROMADO]      │
│     ↓                                │
│  [Elevar pieza]                      │
│     ↓                                │
│  [Estado: DESPLAZAMIENTO_DESCARGA]   │
│     ↓                                │
│  [Mover a estación descarga]         │
│     ↓                                │
│  [Estado: DESCENSO_DESCARGA]         │
│     ↓                                │
│  [Bajar a posición descarga]         │
│     ↓                                │
│  [Estado: LIBERACION_PIEZA]          │
│     ↓                                │
│  [Abrir gancho]                      │
│     ↓                                │
│  [Estado: RETORNO_HOME]              │
│     ↓                                │
│  [Regresar a posición inicial]       │
│     ↓                                │
│  [Estado: REPOSO]                    │
│     ↓                                │
│  [Incrementar contador]              │
│     ↓                                │
└──────────────────────────────────────┘
   ↓
[Registrar ciclo en BD]
   ↓
[FIN]

** En cualquier momento: **
[PARADA EMERGENCIA] → [Estado: EMERGENCIA]
                          ↓
                     [Detener TODO]
                          ↓
                     [Esperar RESET]
```

#### **Diagrama de Clases**

```
┌─────────────────────────────────────┐
│          ControladorPLC             │
├─────────────────────────────────────┤
│ - automata: AutomataGrua            │
│ - grua: Grua                        │
│ - proceso: ProcesoChromado          │
│ - sistema_encendido: bool           │
│ - modo_operacion: str               │
│ - ciclo_en_ejecucion: bool          │
│ - parada_emergencia: bool           │
├─────────────────────────────────────┤
│ + encender_sistema()                │
│ + apagar_sistema()                  │
│ + activar_parada_emergencia()       │
│ + iniciar_ciclo_automatico()        │
│ + detener_ciclo()                   │
│ + actualizar()                      │
│ + obtener_estado_completo(): dict   │
└──────────┬──────────────────────────┘
           │ controla
           ├─────────────────────────────┐
           │                             │
           ▼                             ▼
┌──────────────────────┐    ┌─────────────────────┐
│   AutomataGrua       │    │       Grua          │
├──────────────────────┤    ├─────────────────────┤
│ - estado_actual      │    │ - posicion_x: float │
│ - transiciones: dict │    │ - posicion_y: float │
│ - historial: list    │    │ - velocidad_x       │
├──────────────────────┤    │ - velocidad_y       │
│ + procesar_evento()  │    │ - tiene_pieza: bool │
│ + resetear()         │    │ - gancho_cerrado    │
│ + es_estado_final()  │    ├─────────────────────┤
└──────────────────────┘    │ + actualizar_pos()  │
                            │ + mover_horizontal()│
           ┌────────────────┤ + mover_vertical()  │
           │                │ + cerrar_gancho()   │
           │                │ + soltar_pieza()    │
           │                │ + detener()         │
           │                └─────────────────────┘
           │
           ▼
┌──────────────────────────┐
│   ProcesoChromado        │
├──────────────────────────┤
│ - tiempo_inmersion: int  │
│ - corriente: float       │
│ - voltaje: float         │
│ - estado: EstadoProceso  │
│ - progreso: float        │
│ - calidad_estimada       │
├──────────────────────────┤
│ + configurar_tiempo()    │
│ + iniciar_proceso()      │
│ + actualizar_proceso()   │
│ + completar_proceso()    │
│ + obtener_estadisticas() │
└──────────────────────────┘

┌──────────────────────────┐
│     InterfazHMI          │
├──────────────────────────┤
│ - controlador            │
│ - root: Tk               │
│ - canvas: Canvas         │
│ - labels_estado: dict    │
├──────────────────────────┤
│ + _construir_interfaz()  │
│ + _actualizar_dibujo()   │
│ + _actualizar_graficas() │
│ + ejecutar()             │
└──────────────────────────┘
     │
     │ usa
     ▼
┌──────────────────────────┐
│       BaseDatos          │
├──────────────────────────┤
│ - db_path: str           │
├──────────────────────────┤
│ + insertar_estado_grua() │
│ + iniciar_ciclo()        │
│ + finalizar_ciclo()      │
│ + insertar_log()         │
│ + obtener_estadisticas() │
└──────────────────────────┘
```

---

### 3.2.6. Preguntas Adicionales

#### **Sobre Bibliotecas y Dependencias**

**Bibliotecas utilizadas:**

1. **`tkinter`** (GUI)
   - Widgets: Button, Label, Entry, Canvas, Radiobutton
   - Animación mediante `root.after()`
   - Canvas para dibujo 2D de la grúa

2. **`matplotlib`** (Gráficas)
   - `Figure` y `FigureCanvasTkAgg` para integración con Tkinter
   - `subplot()` para múltiples gráficas
   - Actualización en tiempo real

3. **`threading`** (Concurrencia)
   - `Thread` para ejecutar ciclo automático sin bloquear UI
   - `Event` para sincronización y parada

4. **`sqlite3`** (Base de datos)
   - Incluido en Python, no requiere instalación
   - Context manager para manejo seguro de conexiones

**Integración:**
```python
# En InterfazHMI.__init__()
self.fig = Figure(figsize=(12, 3))
self.canvas_graf = FigureCanvasTkAgg(self.fig, parent)
self.canvas_graf.get_tk_widget().pack()

# Actualización periódica
self.root.after(50, self._actualizar_periodicamente)
```

#### **Manejo de Datos en Tiempo Real**

**Método: Polling con actualización periódica (50ms)**

```python
def _actualizar_periodicamente(self):
    # 1. Calcular delta tiempo
    ahora = datetime.now()
    delta = (ahora - self.ultima_actualizacion).total_seconds()
    
    # 2. Actualizar modelo
    self.controlador.actualizar()
    
    # 3. Actualizar sensores (simulados)
    posicion_actual = self.grua.obtener_posicion()
    
    # 4. Redibujar UI
    self._actualizar_dibujo_grua()
    
    # 5. Programar siguiente actualización
    self.root.after(50, self._actualizar_periodicamente)
```

**No usa:** Interrupciones reales (es simulación), pero el patrón es similar a polling de sensores industriales.

#### **Sobre Seguridad Industrial**

##### **Interlocks de Seguridad**

```python
# En Grua.establecer_objetivo()
def establecer_objetivo(self, x: float, y: float):
    # Interlock: límites físicos
    self.objetivo_x = max(self.limite_x_min, 
                         min(x, self.limite_x_max))
    self.objetivo_y = max(self.limite_y_min, 
                         min(y, self.limite_y_max))

# En ControladorPLC.mover_grua_manual()
def mover_grua_manual(self, x, y):
    # Interlock: solo en modo manual
    if self.modo_operacion != ModoOperacion.MANUAL:
        return False
    
    # Interlock: sistema encendido
    if not self.sistema_encendido:
        return False
    
    # Interlock: no en emergencia
    if self.parada_emergencia:
        return False
    
    self.grua.establecer_objetivo(x, y)
```

**Interlocks implementados:**
- ✅ Verificación de modo operación
- ✅ Sistema encendido
- ✅ No parada de emergencia
- ✅ Límites físicos por software
- ✅ No mover si pieza no asegurada (gancho abierto)

##### **Parada de Emergencia**

```python
def activar_parada_emergencia(self):
    """
    Garantiza parada segura en CUALQUIER estado
    """
    # 1. Marcar bandera global
    self.parada_emergencia = True
    
    # 2. Detener ciclo automático (thread)
    self.evento_parar.set()
    self.ciclo_en_ejecucion = False
    
    # 3. Detener movimiento físico
    self.grua.detener()  # velocidad = 0
    
    # 4. Abortar proceso
    self.proceso.abortar_proceso("PARADA_EMERGENCIA")
    
    # 5. Transición del autómata
    self.automata.procesar_evento(
        EventoAutomata.PARADA_EMERGENCIA
    )
    
    # 6. Registrar evento crítico
    self._log_evento("EMERGENCIA", "...", nivel="ERROR")
```

**Características:**
- Prioridad máxima (no puede ser bloqueada)
- Detención inmediata de todos los subsistemas
- Estado del autómata queda en EMERGENCIA
- Solo se sale con RESET explícito

#### **Buenas Prácticas para Sistemas Industriales**

##### **Redundancia de Sensores Críticos**

**Implementación sugerida:**

```python
class SensorPosicion:
    def __init__(self):
        self.sensor_principal = None
        self.sensor_redundante = None
        self.tolerancia_discrepancia = 5.0
    
    def leer_posicion(self) -> Optional[float]:
        """
        Lee dos sensores y valida consistencia
        """
        pos_a = self.sensor_principal.leer()
        pos_b = self.sensor_redundante.leer()
        
        # Verificar discrepancia
        if abs(pos_a - pos_b) > self.tolerancia_discrepancia:
            self._generar_alarma("SENSOR_DISCREPANCIA")
            return None  # Posición no confiable
        
        # Retornar promedio
        return (pos_a + pos_b) / 2.0
```

##### **Registro de Eventos (Logging)**

**Ya implementado:**

```python
# En ControladorPLC
def _log_evento(self, tipo: str, mensaje: str, nivel: str):
    log_entry = {
        'timestamp': datetime.now(),
        'tipo': tipo,
        'nivel': nivel,
        'mensaje': mensaje,
    }
    
    # 1. Memoria RAM (rápido)
    self.logs.append(log_entry)
    
    # 2. Base de datos (persistente)
    self.db.insertar_log(tipo, nivel, mensaje)
    
    # 3. Callbacks para UI
    for callback in self.callbacks_log:
        callback(log_entry)
```

**Niveles implementados:**
- `INFO`: Eventos normales
- `WARNING`: Advertencias
- `ERROR`: Errores críticos

##### **Manejo de Fallas de Comunicación PLC**

**Estrategia sugerida:**

```python
class ComunicacionPLC:
    def __init__(self):
        self.timeout = 5.0  # segundos
        self.intentos_max = 3
        self.modo_degradado = False
    
    def enviar_comando(self, comando):
        for intento in range(self.intentos_max):
            try:
                respuesta = self._enviar(comando, 
                                        timeout=self.timeout)
                return respuesta
            
            except TimeoutError:
                if intento < self.intentos_max - 1:
                    time.sleep(1)  # Esperar antes de reintentar
                    continue
                else:
                    # Activar modo degradado
                    self._activar_modo_degradado()
                    raise ComunicacionError("PLC no responde")
    
    def _activar_modo_degradado(self):
        """
        Modo seguro: solo control manual
        """
        self.modo_degradado = True
        self.controlador.cambiar_modo(ModoOperacion.MANUAL)
        self._log("Modo degradado activado", "WARNING")
```

#### **Escalabilidad del Sistema**

**Modificaciones para múltiples grúas:**

```python
class SistemaMultiGrua:
    def __init__(self, n_gruas: int):
        self.gruas = [Grua() for _ in range(n_gruas)]
        self.coordinador_trafico = CoordinadorTrafico()
    
    def asignar_tarea(self, tarea):
        """
        Asigna tarea a grúa disponible más cercana
        """
        grua_libre = self._buscar_grua_libre()
        
        # Verificar colisiones potenciales
        if self.coordinador_trafico.ruta_libre(
            grua_libre, tarea.destino
        ):
            grua_libre.asignar_tarea(tarea)
        else:
            # Encolar tarea
            self.cola_tareas.append(tarea)

class CoordinadorTrafico:
    def verificar_colision(self, grua_a, grua_b) -> bool:
        """
        Evita colisiones entre grúas
        """
        dist = self._distancia(grua_a.posicion, 
                              grua_b.posicion)
        return dist < DISTANCIA_SEGURIDAD
    
    def optimizar_throughput(self):
        """
        Algoritmo de optimización:
        - Minimizar tiempos muertos
        - Balancear carga entre grúas
        - Evitar cuellos de botella
        """
```

---

## 📦 Estructura Final del Proyecto

```
Grua-modelado/
├── config/
│   ├── __init__.py
│   └── config.py
├── models/
│   ├── __init__.py
│   ├── automata.py
│   ├── grua.py
│   └── proceso_cromado.py
├── controllers/
│   ├── __init__.py
│   └── controlador_plc.py
├── views/
│   ├── __init__.py
│   └── interfaz_hmi.py
├── utils/
│   ├── __init__.py
│   └── base_datos.py
├── data/
│   ├── grua_sistema.db
│   └── logs/
├── docs/
│   ├── DOCUMENTACION.md
│   └── RESPUESTAS_PROYECTO.md
├── main.py
├── iniciar.bat
├── iniciar.sh
├── requirements.txt
└── README.md
```

---

**Universidad de Pamplona**  
*Modelado y Simulación de Sistemas de Eventos Discretos*  
*Noviembre 2025*
