"""
Modelado del Autómata para el Sistema de Control de Grúa Viga
Representa los estados y transiciones del sistema automatizado
"""

from enum import Enum
from typing import Set, Dict, Callable, Optional
from datetime import datetime


class EstadoGrua(Enum):
    """
    Estados del autómata según el proceso de cromado
    """
    REPOSO = "REPOSO"
    CARGA = "CARGA"
    ASCENSO_INICIAL = "ASCENSO_INICIAL"
    DESPLAZAMIENTO_CENTRO = "DESPLAZAMIENTO_CENTRO"
    DESCENSO_CROMADO = "DESCENSO_CROMADO"
    PROCESO_CROMADO = "PROCESO_CROMADO"
    ASCENSO_POST_CROMADO = "ASCENSO_POST_CROMADO"
    DESPLAZAMIENTO_DESCARGA = "DESPLAZAMIENTO_DESCARGA"
    DESCENSO_DESCARGA = "DESCENSO_DESCARGA"
    LIBERACION_PIEZA = "LIBERACION_PIEZA"
    RETORNO_HOME = "RETORNO_HOME"
    EMERGENCIA = "EMERGENCIA"


class EventoAutomata(Enum):
    """
    Alfabeto de entrada - Eventos que provocan transiciones
    """
    INICIAR_CICLO = "iniciar_ciclo"
    PIEZA_CARGADA = "pieza_cargada"
    POSICION_ALCANZADA = "posicion_alcanzada"
    TOPE_SUPERIOR_ALCANZADO = "tope_superior_alcanzado"
    CENTRO_ALCANZADO = "centro_alcanzado"
    INMERSION_COMPLETA = "inmersion_completa"
    TIEMPO_CROMADO_COMPLETO = "tiempo_cromado_completo"
    PIEZA_ELEVADA = "pieza_elevada"
    DESCARGA_ALCANZADA = "descarga_alcanzada"
    PIEZA_DEPOSITADA = "pieza_depositada"
    HOME_ALCANZADO = "home_alcanzado"
    PARADA_EMERGENCIA = "parada_emergencia"
    RESET_SISTEMA = "reset_sistema"


class AutomataGrua:
    """
    Autómata finito determinista para el control de la grúa viga
    
    Definición formal del autómata:
    A = (Q, Σ, δ, q0, F)
    
    Donde:
    - Q: Conjunto de estados (EstadoGrua)
    - Σ: Alfabeto de entrada (EventoAutomata)
    - δ: Función de transición
    - q0: Estado inicial (REPOSO)
    - F: Conjunto de estados finales (REPOSO - ciclo completado)
    """
    
    def __init__(self):
        # Estado actual del autómata
        self.estado_actual: EstadoGrua = EstadoGrua.REPOSO
        
        # Estado inicial
        self.estado_inicial: EstadoGrua = EstadoGrua.REPOSO
        
        # Estados finales (estados de aceptación)
        self.estados_finales: Set[EstadoGrua] = {EstadoGrua.REPOSO}
        
        # Función de transición: Dict[Estado][Evento] -> Estado
        self.transiciones: Dict[EstadoGrua, Dict[EventoAutomata, EstadoGrua]] = {
            EstadoGrua.REPOSO: {
                EventoAutomata.INICIAR_CICLO: EstadoGrua.CARGA,
            },
            EstadoGrua.CARGA: {
                EventoAutomata.PIEZA_CARGADA: EstadoGrua.ASCENSO_INICIAL,
            },
            EstadoGrua.ASCENSO_INICIAL: {
                EventoAutomata.TOPE_SUPERIOR_ALCANZADO: EstadoGrua.DESPLAZAMIENTO_CENTRO,
            },
            EstadoGrua.DESPLAZAMIENTO_CENTRO: {
                EventoAutomata.CENTRO_ALCANZADO: EstadoGrua.DESCENSO_CROMADO,
            },
            EstadoGrua.DESCENSO_CROMADO: {
                EventoAutomata.INMERSION_COMPLETA: EstadoGrua.PROCESO_CROMADO,
            },
            EstadoGrua.PROCESO_CROMADO: {
                EventoAutomata.TIEMPO_CROMADO_COMPLETO: EstadoGrua.ASCENSO_POST_CROMADO,
            },
            EstadoGrua.ASCENSO_POST_CROMADO: {
                EventoAutomata.TOPE_SUPERIOR_ALCANZADO: EstadoGrua.DESPLAZAMIENTO_DESCARGA,
            },
            EstadoGrua.DESPLAZAMIENTO_DESCARGA: {
                EventoAutomata.DESCARGA_ALCANZADA: EstadoGrua.DESCENSO_DESCARGA,
            },
            EstadoGrua.DESCENSO_DESCARGA: {
                EventoAutomata.POSICION_ALCANZADA: EstadoGrua.LIBERACION_PIEZA,
            },
            EstadoGrua.LIBERACION_PIEZA: {
                EventoAutomata.PIEZA_DEPOSITADA: EstadoGrua.RETORNO_HOME,
            },
            EstadoGrua.RETORNO_HOME: {
                EventoAutomata.HOME_ALCANZADO: EstadoGrua.REPOSO,
            },
        }
        
        # Transiciones de emergencia desde cualquier estado
        self._agregar_transiciones_emergencia()
        
        # Callbacks para observadores
        self.callbacks_transicion: list[Callable] = []
        
        # Historial de transiciones
        self.historial: list[Dict] = []
    
    def _agregar_transiciones_emergencia(self):
        """
        Agrega transiciones de parada de emergencia desde todos los estados
        """
        for estado in EstadoGrua:
            if estado != EstadoGrua.EMERGENCIA:
                if estado not in self.transiciones:
                    self.transiciones[estado] = {}
                self.transiciones[estado][EventoAutomata.PARADA_EMERGENCIA] = EstadoGrua.EMERGENCIA
        
        # Desde emergencia solo se puede resetear
        self.transiciones[EstadoGrua.EMERGENCIA] = {
            EventoAutomata.RESET_SISTEMA: EstadoGrua.REPOSO,
        }
    
    def procesar_evento(self, evento: EventoAutomata) -> bool:
        """
        Función de transición δ: Q × Σ → Q
        
        Args:
            evento: Evento de entrada del alfabeto
            
        Returns:
            True si la transición fue exitosa, False en caso contrario
        """
        if self.estado_actual not in self.transiciones:
            return False
        
        if evento not in self.transiciones[self.estado_actual]:
            return False
        
        # Guardar estado anterior
        estado_anterior = self.estado_actual
        
        # Realizar transición
        self.estado_actual = self.transiciones[self.estado_actual][evento]
        
        # Registrar transición en historial
        self._registrar_transicion(estado_anterior, evento, self.estado_actual)
        
        # Notificar a observadores
        self._notificar_transicion(estado_anterior, evento, self.estado_actual)
        
        return True
    
    def _registrar_transicion(self, estado_anterior: EstadoGrua, 
                            evento: EventoAutomata, 
                            estado_nuevo: EstadoGrua):
        """
        Registra una transición en el historial
        """
        registro = {
            'timestamp': datetime.now(),
            'estado_anterior': estado_anterior.value,
            'evento': evento.value,
            'estado_nuevo': estado_nuevo.value,
        }
        self.historial.append(registro)
    
    def _notificar_transicion(self, estado_anterior: EstadoGrua, 
                             evento: EventoAutomata, 
                             estado_nuevo: EstadoGrua):
        """
        Notifica a los observadores sobre una transición
        """
        for callback in self.callbacks_transicion:
            callback(estado_anterior, evento, estado_nuevo)
    
    def registrar_callback(self, callback: Callable):
        """
        Registra un callback para notificaciones de transición
        """
        self.callbacks_transicion.append(callback)
    
    def resetear(self):
        """
        Reinicia el autómata al estado inicial
        """
        estado_anterior = self.estado_actual
        self.estado_actual = self.estado_inicial
        self._registrar_transicion(estado_anterior, EventoAutomata.RESET_SISTEMA, self.estado_actual)
    
    def es_estado_final(self) -> bool:
        """
        Verifica si el estado actual es un estado de aceptación
        """
        return self.estado_actual in self.estados_finales
    
    def obtener_eventos_validos(self) -> Set[EventoAutomata]:
        """
        Retorna los eventos válidos desde el estado actual
        """
        if self.estado_actual in self.transiciones:
            return set(self.transiciones[self.estado_actual].keys())
        return set()
    
    def puede_procesar_evento(self, evento: EventoAutomata) -> bool:
        """
        Verifica si un evento puede ser procesado desde el estado actual
        """
        return evento in self.obtener_eventos_validos()
    
    def obtener_historial(self) -> list[Dict]:
        """
        Retorna el historial completo de transiciones
        """
        return self.historial.copy()
    
    def limpiar_historial(self):
        """
        Limpia el historial de transiciones
        """
        self.historial.clear()
    
    def __str__(self) -> str:
        return f"Autómata[Estado: {self.estado_actual.value}]"
    
    def __repr__(self) -> str:
        return f"AutomataGrua(estado={self.estado_actual.value})"
