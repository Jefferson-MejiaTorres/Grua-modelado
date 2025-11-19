"""
Modelo del Proceso de Cromado por Electrólisis
Gestiona los parámetros y estado del proceso de cromado
"""

from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class EstadoProceso(Enum):
    """Estados del proceso de cromado"""
    INACTIVO = "INACTIVO"
    PREPARANDO = "PREPARANDO"
    EN_PROCESO = "EN_PROCESO"
    COMPLETADO = "COMPLETADO"
    ERROR = "ERROR"


class ProcesoChromado:
    """
    Modelo del proceso de cromado por electrólisis
    
    Atributos:
        tiempo_inmersion: Tiempo configurado para inmersión (segundos)
        corriente_electrolisis: Corriente aplicada (Amperios)
        voltaje_electrolisis: Voltaje aplicado (Voltios)
        temperatura_bano: Temperatura del baño electrolítico (°C)
    """
    
    def __init__(self, tiempo_default: int = 120):
        # Parámetros del proceso
        self.tiempo_inmersion: int = tiempo_default  # Segundos
        self.tiempo_min: int = 30
        self.tiempo_max: int = 600
        
        # Parámetros eléctricos
        self.corriente_electrolisis: float = 2.5  # Amperios
        self.voltaje_electrolisis: float = 12.0   # Voltios
        
        # Parámetros químicos/físicos
        self.temperatura_bano: float = 25.0  # °C
        self.concentracion_cromo: float = 250.0  # g/L
        self.ph_bano: float = 2.5
        
        # Control del proceso
        self.estado: EstadoProceso = EstadoProceso.INACTIVO
        self.tiempo_inicio: Optional[datetime] = None
        self.tiempo_transcurrido: float = 0.0
        self.progreso_porcentaje: float = 0.0
        
        # Calidad del proceso
        self.pieza_id: Optional[str] = None
        self.espesor_deposito: float = 0.0  # Micras
        self.calidad_estimada: float = 100.0  # Porcentaje
        
        # Estadísticas
        self.piezas_procesadas: int = 0
        self.piezas_exitosas: int = 0
        self.piezas_fallidas: int = 0
        
        # Alarmas
        self.alarmas_activas: list[str] = []
    
    def configurar_tiempo(self, tiempo_segundos: int) -> bool:
        """
        Configura el tiempo de inmersión para el proceso
        
        Args:
            tiempo_segundos: Tiempo en segundos
            
        Returns:
            True si el tiempo es válido, False en caso contrario
        """
        if self.tiempo_min <= tiempo_segundos <= self.tiempo_max:
            self.tiempo_inmersion = tiempo_segundos
            return True
        return False
    
    def configurar_parametros_electricos(self, corriente: float, voltaje: float):
        """
        Configura los parámetros eléctricos del proceso
        """
        self.corriente_electrolisis = corriente
        self.voltaje_electrolisis = voltaje
    
    def iniciar_proceso(self, pieza_id: str):
        """
        Inicia el proceso de cromado
        """
        self.estado = EstadoProceso.EN_PROCESO
        self.tiempo_inicio = datetime.now()
        self.tiempo_transcurrido = 0.0
        self.progreso_porcentaje = 0.0
        self.pieza_id = pieza_id
        self.espesor_deposito = 0.0
        self.alarmas_activas.clear()
    
    def actualizar_proceso(self, delta_tiempo: float) -> bool:
        """
        Actualiza el estado del proceso de cromado
        
        Args:
            delta_tiempo: Tiempo transcurrido en segundos
            
        Returns:
            True si el proceso ha completado, False si aún está en curso
        """
        if self.estado != EstadoProceso.EN_PROCESO:
            return False
        
        # Actualizar tiempo transcurrido
        self.tiempo_transcurrido += delta_tiempo
        
        # Calcular progreso
        self.progreso_porcentaje = min(100.0, (self.tiempo_transcurrido / self.tiempo_inmersion) * 100)
        
        # Calcular espesor del depósito (simulación simplificada)
        # Ley de Faraday: m = (I * t * M) / (n * F)
        self.espesor_deposito = (self.tiempo_transcurrido / self.tiempo_inmersion) * 25.0  # Hasta 25 micras
        
        # Verificar condiciones del proceso
        self._verificar_condiciones()
        
        # Verificar si completó el tiempo
        if self.tiempo_transcurrido >= self.tiempo_inmersion:
            self.completar_proceso()
            return True
        
        return False
    
    def _verificar_condiciones(self):
        """
        Verifica las condiciones del proceso y genera alarmas si es necesario
        """
        self.alarmas_activas.clear()
        
        # Verificar temperatura
        if self.temperatura_bano < 20 or self.temperatura_bano > 30:
            self.alarmas_activas.append("TEMPERATURA_FUERA_RANGO")
            self.calidad_estimada -= 5
        
        # Verificar pH
        if self.ph_bano < 2.0 or self.ph_bano > 3.0:
            self.alarmas_activas.append("PH_FUERA_RANGO")
            self.calidad_estimada -= 10
        
        # Verificar corriente
        if self.corriente_electrolisis < 2.0 or self.corriente_electrolisis > 3.0:
            self.alarmas_activas.append("CORRIENTE_ANORMAL")
            self.calidad_estimada -= 8
    
    def completar_proceso(self):
        """
        Marca el proceso como completado
        """
        self.estado = EstadoProceso.COMPLETADO
        self.progreso_porcentaje = 100.0
        self.piezas_procesadas += 1
        
        # Determinar si fue exitoso
        if self.calidad_estimada >= 80:
            self.piezas_exitosas += 1
        else:
            self.piezas_fallidas += 1
    
    def detener_proceso(self):
        """
        Detiene el proceso antes de completarse
        """
        self.estado = EstadoProceso.INACTIVO
        self.tiempo_transcurrido = 0.0
        self.progreso_porcentaje = 0.0
    
    def abortar_proceso(self, razon: str = "ABORTADO_MANUALMENTE"):
        """
        Aborta el proceso por error o intervención manual
        """
        self.estado = EstadoProceso.ERROR
        self.alarmas_activas.append(razon)
        self.piezas_fallidas += 1
    
    def resetear(self):
        """
        Reinicia el proceso a estado inicial
        """
        self.estado = EstadoProceso.INACTIVO
        self.tiempo_inicio = None
        self.tiempo_transcurrido = 0.0
        self.progreso_porcentaje = 0.0
        self.pieza_id = None
        self.espesor_deposito = 0.0
        self.calidad_estimada = 100.0
        self.alarmas_activas.clear()
    
    def obtener_tiempo_restante(self) -> float:
        """
        Retorna el tiempo restante del proceso en segundos
        """
        if self.estado != EstadoProceso.EN_PROCESO:
            return 0.0
        return max(0.0, self.tiempo_inmersion - self.tiempo_transcurrido)
    
    def obtener_estadisticas(self) -> dict:
        """
        Retorna estadísticas del proceso
        """
        tasa_exito = 0.0
        if self.piezas_procesadas > 0:
            tasa_exito = (self.piezas_exitosas / self.piezas_procesadas) * 100
        
        return {
            'piezas_procesadas': self.piezas_procesadas,
            'piezas_exitosas': self.piezas_exitosas,
            'piezas_fallidas': self.piezas_fallidas,
            'tasa_exito': tasa_exito,
        }
    
    def obtener_estado(self) -> dict:
        """
        Retorna el estado completo del proceso
        """
        return {
            'estado': self.estado.value,
            'tiempo_inmersion_config': self.tiempo_inmersion,
            'tiempo_transcurrido': self.tiempo_transcurrido,
            'tiempo_restante': self.obtener_tiempo_restante(),
            'progreso': self.progreso_porcentaje,
            'pieza_id': self.pieza_id,
            'corriente': self.corriente_electrolisis,
            'voltaje': self.voltaje_electrolisis,
            'temperatura': self.temperatura_bano,
            'espesor_deposito': self.espesor_deposito,
            'calidad_estimada': self.calidad_estimada,
            'alarmas': self.alarmas_activas.copy(),
        }
    
    def __str__(self) -> str:
        return f"Proceso[{self.estado.value} - {self.progreso_porcentaje:.1f}%]"
    
    def __repr__(self) -> str:
        return f"ProcesoChromado(estado={self.estado.value}, progreso={self.progreso_porcentaje})"
