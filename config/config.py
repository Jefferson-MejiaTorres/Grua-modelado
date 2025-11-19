"""
Configuración del Sistema de Control de Grúa Viga
Norma ISA 5.1 para instrumentación industrial
"""

# ==================== CONFIGURACIÓN FÍSICA ====================

# Dimensiones del área de trabajo (en unidades arbitrarias)
AREA_TRABAJO = {
    'ancho': 1000,  # Ancho total del área
    'alto': 600,    # Alto total del área
}

# Posiciones de las estaciones (coordenadas X, Y)
POSICIONES = {
    'HOME': (100, 500),           # Posición inicial (inferior izquierda)
    'CARGA': (100, 500),          # Misma que HOME
    'CROMADO': (500, 200),        # Centro, zona de inmersión
    'DESCARGA': (900, 500),       # Extremo derecho
    'TOPE_SUPERIOR': 50,          # Límite superior Y
    'TOPE_INFERIOR': 500,         # Límite inferior Y
}

# Velocidades de movimiento (unidades/segundo)
VELOCIDADES = {
    'horizontal_rapido': 150,     # Movimiento horizontal rápido
    'horizontal_lento': 80,       # Movimiento horizontal lento
    'vertical_rapido': 100,       # Movimiento vertical rápido
    'vertical_lento': 50,         # Movimiento vertical lento
}

# ==================== CONFIGURACIÓN DEL PROCESO ====================

# Parámetros del proceso de cromado
PROCESO_CROMADO = {
    'tiempo_default': 120,        # Tiempo de inmersión en segundos
    'tiempo_min': 30,             # Tiempo mínimo permitido
    'tiempo_max': 600,            # Tiempo máximo permitido
    'corriente_electrolisis': 2.5, # Amperios
    'voltaje_electrolisis': 12.0,  # Voltios
}

# Tiempos de seguridad
TIEMPOS_SEGURIDAD = {
    'pausa_inicio': 2,            # Pausa antes de iniciar movimiento
    'pausa_transicion': 1,        # Pausa entre movimientos
    'timeout_operacion': 30,      # Timeout para operaciones
}

# ==================== CONFIGURACIÓN ISA 5.1 ====================

# Colores según norma ISA 5.1
COLORES_ISA = {
    'normal': '#00FF00',          # Verde - Operación normal
    'alarma': '#FF0000',          # Rojo - Alarma
    'advertencia': '#FFFF00',     # Amarillo - Advertencia
    'inactivo': '#808080',        # Gris - Inactivo
    'proceso': '#00FFFF',         # Cian - En proceso
    'manual': '#FFA500',          # Naranja - Modo manual
}

# Símbolos de instrumentación ISA 5.1
INSTRUMENTACION = {
    'indicador_posicion': 'PI',   # Position Indicator
    'controlador_velocidad': 'SC', # Speed Controller
    'indicador_tiempo': 'TI',     # Time Indicator
    'sensor_posicion': 'PS',      # Position Switch
    'controlador_proceso': 'PC',  # Process Controller
}

# ==================== CONFIGURACIÓN DE LA INTERFAZ ====================

# Dimensiones de ventana
VENTANA = {
    'ancho': 1400,
    'alto': 900,
    'titulo': 'Control de Grúa Viga - Proceso de Cromado ISA 5.1',
}

# Colores de interfaz
COLORES_UI = {
    'fondo': '#1e1e1e',
    'panel': '#2d2d2d',
    'texto': '#ffffff',
    'boton_activo': '#4CAF50',
    'boton_inactivo': '#757575',
    'emergencia': '#F44336',
    'linea_grua': '#FFD700',
    'gancho': '#FF6B6B',
    'pieza': '#4ECDC4',
    'estacion': '#95E1D3',
    'liquido_cromado': '#3498db',
}

# Tamaños de elementos gráficos
TAMANHOS = {
    'grua_ancho': 60,
    'grua_alto': 40,
    'gancho_ancho': 10,
    'gancho_largo': 30,
    'pieza_ancho': 40,
    'pieza_alto': 30,
    'estacion_ancho': 120,
    'estacion_alto': 150,
}

# ==================== CONFIGURACIÓN DE BASE DE DATOS ====================

DATABASE = {
    'path': 'data/grua_sistema.db',
    'backup_enabled': True,
    'log_level': 'INFO',
}

# ==================== CONFIGURACIÓN DE SEGURIDAD ====================

SEGURIDAD = {
    'limites_x': (50, 950),       # Límites horizontales
    'limites_y': (50, 550),       # Límites verticales
    'distancia_seguridad': 20,    # Distancia mínima a obstáculos
    'interlock_enabled': True,    # Enclavamientos de seguridad
    'parada_emergencia': True,    # Parada de emergencia disponible
}

# ==================== CONFIGURACIÓN DE LOGGING ====================

LOGGING = {
    'archivo': 'data/logs/sistema.log',
    'nivel': 'INFO',
    'formato': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'guardar_eventos': True,
}
