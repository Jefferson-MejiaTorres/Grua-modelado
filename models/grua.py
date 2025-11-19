"""
Modelo de la Grúa Viga
Representa el sistema físico con posición, velocidad y estado
"""

from typing import Tuple, Optional
from datetime import datetime
import math


class Grua:
    """
    Modelo de la grúa viga que representa el sistema físico
    
    Atributos:
        posicion_x: Posición horizontal de la grúa
        posicion_y: Posición vertical del gancho
        velocidad_x: Velocidad horizontal actual
        velocidad_y: Velocidad vertical actual
        estado_gancho: Estado del gancho (abierto/cerrado)
        tiene_pieza: Indica si hay una pieza cargada
    """
    
    def __init__(self, pos_inicial: Tuple[float, float] = (100, 500)):
        # Posición actual
        self.posicion_x: float = pos_inicial[0]
        self.posicion_y: float = pos_inicial[1]
        
        # Posición objetivo
        self.objetivo_x: Optional[float] = None
        self.objetivo_y: Optional[float] = None
        
        # Velocidad actual
        self.velocidad_x: float = 0.0
        self.velocidad_y: float = 0.0
        
        # Velocidades configurables
        self.vel_horizontal: float = 150.0
        self.vel_vertical: float = 100.0
        
        # Estado del gancho y carga
        self.gancho_cerrado: bool = False
        self.tiene_pieza: bool = False
        
        # Límites físicos
        self.limite_x_min: float = 50
        self.limite_x_max: float = 950
        self.limite_y_min: float = 50
        self.limite_y_max: float = 550
        
        # Tolerancia para alcanzar objetivo
        self.tolerancia: float = 5.0
        
        # Estado de movimiento
        self.en_movimiento: bool = False
        
        # Timestamp último movimiento
        self.ultima_actualizacion: datetime = datetime.now()
    
    def establecer_objetivo(self, x: float, y: float):
        """
        Establece la posición objetivo para el movimiento
        """
        self.objetivo_x = max(self.limite_x_min, min(x, self.limite_x_max))
        self.objetivo_y = max(self.limite_y_min, min(y, self.limite_y_max))
        self.en_movimiento = True
    
    def actualizar_posicion(self, delta_tiempo: float) -> bool:
        """
        Actualiza la posición de la grúa según el tiempo transcurrido
        
        Args:
            delta_tiempo: Tiempo en segundos desde última actualización
            
        Returns:
            True si alcanzó el objetivo, False si aún está en movimiento
        """
        if not self.en_movimiento or self.objetivo_x is None:
            return True
        
        # Calcular distancia al objetivo
        dist_x = self.objetivo_x - self.posicion_x
        dist_y = self.objetivo_y - self.posicion_y
        
        # Verificar si alcanzó el objetivo
        if abs(dist_x) < self.tolerancia and abs(dist_y) < self.tolerancia:
            self.posicion_x = self.objetivo_x
            self.posicion_y = self.objetivo_y
            self.velocidad_x = 0.0
            self.velocidad_y = 0.0
            self.en_movimiento = False
            return True
        
        # Calcular movimiento horizontal
        if abs(dist_x) >= self.tolerancia:
            movimiento_x = self.vel_horizontal * delta_tiempo
            if abs(dist_x) < movimiento_x:
                self.posicion_x = self.objetivo_x
                self.velocidad_x = 0.0
            else:
                direccion_x = 1 if dist_x > 0 else -1
                self.posicion_x += movimiento_x * direccion_x
                self.velocidad_x = self.vel_horizontal * direccion_x
        
        # Calcular movimiento vertical
        if abs(dist_y) >= self.tolerancia:
            movimiento_y = self.vel_vertical * delta_tiempo
            if abs(dist_y) < movimiento_y:
                self.posicion_y = self.objetivo_y
                self.velocidad_y = 0.0
            else:
                direccion_y = 1 if dist_y > 0 else -1
                self.posicion_y += movimiento_y * direccion_y
                self.velocidad_y = self.vel_vertical * direccion_y
        
        # Aplicar límites de seguridad
        self.posicion_x = max(self.limite_x_min, min(self.posicion_x, self.limite_x_max))
        self.posicion_y = max(self.limite_y_min, min(self.posicion_y, self.limite_y_max))
        
        self.ultima_actualizacion = datetime.now()
        return False
    
    def mover_horizontal(self, x_destino: float):
        """
        Mueve la grúa horizontalmente manteniendo Y constante
        """
        self.establecer_objetivo(x_destino, self.posicion_y)
    
    def mover_vertical(self, y_destino: float):
        """
        Mueve el gancho verticalmente manteniendo X constante
        """
        self.establecer_objetivo(self.posicion_x, y_destino)
    
    def mover_a_posicion(self, x: float, y: float):
        """
        Mueve la grúa a una posición específica (X, Y)
        """
        self.establecer_objetivo(x, y)
    
    def cerrar_gancho(self):
        """
        Cierra el gancho para agarrar una pieza
        """
        self.gancho_cerrado = True
    
    def abrir_gancho(self):
        """
        Abre el gancho para soltar una pieza
        """
        self.gancho_cerrado = False
        self.tiene_pieza = False
    
    def cargar_pieza(self):
        """
        Carga una pieza en el gancho
        """
        if self.gancho_cerrado:
            self.tiene_pieza = True
    
    def soltar_pieza(self):
        """
        Suelta la pieza del gancho
        """
        self.tiene_pieza = False
        self.abrir_gancho()
    
    def detener(self):
        """
        Detiene todo movimiento de la grúa
        """
        self.en_movimiento = False
        self.velocidad_x = 0.0
        self.velocidad_y = 0.0
        self.objetivo_x = None
        self.objetivo_y = None
    
    def obtener_posicion(self) -> Tuple[float, float]:
        """
        Retorna la posición actual (x, y)
        """
        return (self.posicion_x, self.posicion_y)
    
    def obtener_velocidad(self) -> Tuple[float, float]:
        """
        Retorna la velocidad actual (vx, vy)
        """
        return (self.velocidad_x, self.velocidad_y)
    
    def distancia_a_objetivo(self) -> float:
        """
        Calcula la distancia euclidiana al objetivo
        """
        if self.objetivo_x is None or self.objetivo_y is None:
            return 0.0
        
        dx = self.objetivo_x - self.posicion_x
        dy = self.objetivo_y - self.posicion_y
        return math.sqrt(dx**2 + dy**2)
    
    def esta_en_posicion(self, x: float, y: float, tolerancia: Optional[float] = None) -> bool:
        """
        Verifica si la grúa está en una posición específica
        """
        tol = tolerancia if tolerancia is not None else self.tolerancia
        dist_x = abs(self.posicion_x - x)
        dist_y = abs(self.posicion_y - y)
        return dist_x < tol and dist_y < tol
    
    def resetear(self, pos_inicial: Tuple[float, float] = (100, 500)):
        """
        Reinicia la grúa a su posición inicial
        """
        self.posicion_x = pos_inicial[0]
        self.posicion_y = pos_inicial[1]
        self.detener()
        self.abrir_gancho()
        self.tiene_pieza = False
    
    def obtener_estado(self) -> dict:
        """
        Retorna el estado completo de la grúa como diccionario
        """
        return {
            'posicion_x': self.posicion_x,
            'posicion_y': self.posicion_y,
            'velocidad_x': self.velocidad_x,
            'velocidad_y': self.velocidad_y,
            'objetivo_x': self.objetivo_x,
            'objetivo_y': self.objetivo_y,
            'gancho_cerrado': self.gancho_cerrado,
            'tiene_pieza': self.tiene_pieza,
            'en_movimiento': self.en_movimiento,
            'distancia_objetivo': self.distancia_a_objetivo(),
            'ultima_actualizacion': self.ultima_actualizacion.isoformat(),
        }
    
    def __str__(self) -> str:
        return f"Grúa[Pos:({self.posicion_x:.1f}, {self.posicion_y:.1f}) Pieza:{self.tiene_pieza}]"
    
    def __repr__(self) -> str:
        return f"Grua(x={self.posicion_x}, y={self.posicion_y}, pieza={self.tiene_pieza})"
