"""
Controlador Principal del Sistema de Grúa Viga
Implementa el patrón MVC - Controlador
Coordina el autómata, la grúa y el proceso de cromado
"""

import time
from datetime import datetime
from typing import Optional, Callable
from threading import Thread, Event
import config.config as cfg
from models.automata import AutomataGrua, EstadoGrua, EventoAutomata
from models.grua import Grua
from models.proceso_cromado import ProcesoChromado, EstadoProceso


class ModoOperacion:
    """Modos de operación del sistema"""
    MANUAL = "MANUAL"
    AUTOMATICO = "AUTOMATICO"


class ControladorPLC:
    """
    Controlador tipo PLC para el sistema de grúa viga
    Coordina todos los subsistemas y ejecuta la lógica de control
    
    Responsabilidades:
    - Coordinar movimientos de la grúa
    - Gestionar transiciones del autómata
    - Controlar el proceso de cromado
    - Manejar la seguridad del sistema
    - Registrar eventos y alarmas
    """
    
    def __init__(self):
        # Subsistemas
        self.automata = AutomataGrua()
        self.grua = Grua(pos_inicial=cfg.POSICIONES['HOME'])
        self.proceso = ProcesoChromado(tiempo_default=cfg.PROCESO_CROMADO['tiempo_default'])
        
        # Estado del sistema
        self.sistema_encendido: bool = False
        self.modo_operacion: str = ModoOperacion.AUTOMATICO
        self.ciclo_en_ejecucion: bool = False
        self.parada_emergencia: bool = False
        
        # Control de ciclo automático
        self.thread_ciclo: Optional[Thread] = None
        self.evento_parar: Event = Event()
        
        # Estadísticas
        self.ciclos_completados: int = 0
        self.tiempo_inicio_ciclo: Optional[datetime] = None
        self.tiempo_ciclo_actual: float = 0.0
        
        # Callbacks para UI
        self.callbacks_actualizacion: list[Callable] = []
        self.callbacks_log: list[Callable] = []
        
        # Registro de eventos
        self.logs: list[dict] = []
        
        # Configurar callbacks del autómata
        self.automata.registrar_callback(self._on_transicion_automata)
        
        # Última actualización
        self.ultima_actualizacion: datetime = datetime.now()
    
    # ==================== CONTROL DEL SISTEMA ====================
    
    def encender_sistema(self):
        """Enciende el sistema de control"""
        if not self.sistema_encendido:
            self.sistema_encendido = True
            self.parada_emergencia = False
            self.automata.resetear()
            self.grua.resetear(cfg.POSICIONES['HOME'])
            self.proceso.resetear()
            self._log_evento("SISTEMA_ENCENDIDO", "Sistema iniciado correctamente")
    
    def apagar_sistema(self):
        """Apaga el sistema de control"""
        if self.sistema_encendido:
            self.detener_ciclo()
            self.sistema_encendido = False
            self._log_evento("SISTEMA_APAGADO", "Sistema apagado")
    
    def activar_parada_emergencia(self):
        """Activa la parada de emergencia"""
        self.parada_emergencia = True
        self.detener_ciclo()
        self.grua.detener()
        self.proceso.abortar_proceso("PARADA_EMERGENCIA")
        self.automata.procesar_evento(EventoAutomata.PARADA_EMERGENCIA)
        self._log_evento("EMERGENCIA", "Parada de emergencia activada", nivel="ERROR")
    
    def resetear_emergencia(self):
        """Resetea la parada de emergencia"""
        if self.parada_emergencia:
            self.parada_emergencia = False
            self.automata.procesar_evento(EventoAutomata.RESET_SISTEMA)
            self.grua.resetear(cfg.POSICIONES['HOME'])
            self.proceso.resetear()
            self._log_evento("RESET", "Sistema reseteado después de emergencia")
    
    def cambiar_modo(self, modo: str):
        """Cambia el modo de operación (MANUAL/AUTOMATICO)"""
        if modo in [ModoOperacion.MANUAL, ModoOperacion.AUTOMATICO]:
            self.modo_operacion = modo
            self._log_evento("MODO_CAMBIO", f"Modo cambiado a {modo}")
    
    # ==================== CONTROL DE CICLO AUTOMÁTICO ====================
    
    def iniciar_ciclo_automatico(self):
        """Inicia un ciclo automático de cromado"""
        if not self.sistema_encendido:
            self._log_evento("ERROR", "Sistema apagado", nivel="ERROR")
            return False
        
        if self.parada_emergencia:
            self._log_evento("ERROR", "Parada de emergencia activa", nivel="ERROR")
            return False
        
        if self.ciclo_en_ejecucion:
            self._log_evento("ERROR", "Ciclo ya en ejecución", nivel="WARNING")
            return False
        
        if self.modo_operacion != ModoOperacion.AUTOMATICO:
            self._log_evento("ERROR", "Sistema no está en modo automático", nivel="WARNING")
            return False
        
        # Iniciar ciclo en thread separado
        self.ciclo_en_ejecucion = True
        self.tiempo_inicio_ciclo = datetime.now()
        self.evento_parar.clear()
        
        self.thread_ciclo = Thread(target=self._ejecutar_ciclo_automatico, daemon=True)
        self.thread_ciclo.start()
        
        self._log_evento("CICLO_INICIADO", "Ciclo automático iniciado")
        return True
    
    def detener_ciclo(self):
        """Detiene el ciclo automático en ejecución"""
        if self.ciclo_en_ejecucion:
            self.evento_parar.set()
            self.ciclo_en_ejecucion = False
            if self.thread_ciclo:
                self.thread_ciclo.join(timeout=2.0)
            self._log_evento("CICLO_DETENIDO", "Ciclo detenido")
    
    def _ejecutar_ciclo_automatico(self):
        """Ejecuta la secuencia completa del ciclo automático"""
        try:
            # ESTADO: CARGA
            self._log_evento("CICLO", "Iniciando carga de pieza")
            self.automata.procesar_evento(EventoAutomata.INICIAR_CICLO)
            time.sleep(cfg.TIEMPOS_SEGURIDAD['pausa_inicio'])
            
            # Simular carga de pieza
            self.grua.cerrar_gancho()
            self.grua.cargar_pieza()
            self.automata.procesar_evento(EventoAutomata.PIEZA_CARGADA)
            time.sleep(cfg.TIEMPOS_SEGURIDAD['pausa_transicion'])
            
            if self.evento_parar.is_set(): return
            
            # ESTADO: ASCENSO_INICIAL
            self._log_evento("CICLO", "Ascenso a tope superior")
            self.grua.establecer_objetivo(
                cfg.POSICIONES['HOME'][0],
                cfg.POSICIONES['TOPE_SUPERIOR']
            )
            self._esperar_objetivo_grua()
            self.automata.procesar_evento(EventoAutomata.TOPE_SUPERIOR_ALCANZADO)
            
            if self.evento_parar.is_set(): return
            
            # ESTADO: DESPLAZAMIENTO_CENTRO
            self._log_evento("CICLO", "Desplazamiento a estación de cromado")
            self.grua.establecer_objetivo(
                cfg.POSICIONES['CROMADO'][0],
                cfg.POSICIONES['TOPE_SUPERIOR']
            )
            self._esperar_objetivo_grua()
            self.automata.procesar_evento(EventoAutomata.CENTRO_ALCANZADO)
            
            if self.evento_parar.is_set(): return
            
            # ESTADO: DESCENSO_CROMADO
            self._log_evento("CICLO", "Descenso a estación de cromado")
            self.grua.establecer_objetivo(
                cfg.POSICIONES['CROMADO'][0],
                cfg.POSICIONES['CROMADO'][1]
            )
            self._esperar_objetivo_grua()
            self.automata.procesar_evento(EventoAutomata.INMERSION_COMPLETA)
            
            if self.evento_parar.is_set(): return
            
            # ESTADO: PROCESO_CROMADO
            self._log_evento("CICLO", f"Iniciando proceso de cromado ({self.proceso.tiempo_inmersion}s)")
            pieza_id = f"PIEZA_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.proceso.iniciar_proceso(pieza_id)
            
            # Esperar que complete el proceso
            while not self.evento_parar.is_set():
                completado = self.proceso.actualizar_proceso(0.1)
                if completado:
                    break
                time.sleep(0.1)
            
            self.automata.procesar_evento(EventoAutomata.TIEMPO_CROMADO_COMPLETO)
            
            if self.evento_parar.is_set(): return
            
            # ESTADO: ASCENSO_POST_CROMADO
            self._log_evento("CICLO", "Elevando pieza cromada")
            self.grua.establecer_objetivo(
                cfg.POSICIONES['CROMADO'][0],
                cfg.POSICIONES['TOPE_SUPERIOR']
            )
            self._esperar_objetivo_grua()
            self.automata.procesar_evento(EventoAutomata.TOPE_SUPERIOR_ALCANZADO)
            
            if self.evento_parar.is_set(): return
            
            # ESTADO: DESPLAZAMIENTO_DESCARGA
            self._log_evento("CICLO", "Desplazamiento a estación de descarga")
            self.grua.establecer_objetivo(
                cfg.POSICIONES['DESCARGA'][0],
                cfg.POSICIONES['TOPE_SUPERIOR']
            )
            self._esperar_objetivo_grua()
            self.automata.procesar_evento(EventoAutomata.DESCARGA_ALCANZADA)
            
            if self.evento_parar.is_set(): return
            
            # ESTADO: DESCENSO_DESCARGA
            self._log_evento("CICLO", "Descenso a estación de descarga")
            self.grua.establecer_objetivo(
                cfg.POSICIONES['DESCARGA'][0],
                cfg.POSICIONES['DESCARGA'][1]
            )
            self._esperar_objetivo_grua()
            self.automata.procesar_evento(EventoAutomata.POSICION_ALCANZADA)
            
            if self.evento_parar.is_set(): return
            
            # ESTADO: LIBERACION_PIEZA
            self._log_evento("CICLO", "Liberando pieza procesada")
            self.grua.soltar_pieza()
            time.sleep(cfg.TIEMPOS_SEGURIDAD['pausa_transicion'])
            self.automata.procesar_evento(EventoAutomata.PIEZA_DEPOSITADA)
            
            if self.evento_parar.is_set(): return
            
            # ESTADO: RETORNO_HOME
            self._log_evento("CICLO", "Retornando a posición inicial")
            self.grua.establecer_objetivo(
                cfg.POSICIONES['DESCARGA'][0],
                cfg.POSICIONES['TOPE_SUPERIOR']
            )
            self._esperar_objetivo_grua()
            
            self.grua.establecer_objetivo(
                cfg.POSICIONES['HOME'][0],
                cfg.POSICIONES['TOPE_SUPERIOR']
            )
            self._esperar_objetivo_grua()
            
            self.grua.establecer_objetivo(
                cfg.POSICIONES['HOME'][0],
                cfg.POSICIONES['HOME'][1]
            )
            self._esperar_objetivo_grua()
            
            self.automata.procesar_evento(EventoAutomata.HOME_ALCANZADO)
            
            # Ciclo completado
            self.ciclos_completados += 1
            tiempo_total = (datetime.now() - self.tiempo_inicio_ciclo).total_seconds()
            self._log_evento("CICLO_COMPLETADO", f"Ciclo completado en {tiempo_total:.1f}s")
            
        except Exception as e:
            self._log_evento("ERROR_CICLO", f"Error en ciclo: {str(e)}", nivel="ERROR")
        finally:
            self.ciclo_en_ejecucion = False
            self.evento_parar.clear()
    
    def _esperar_objetivo_grua(self):
        """Espera a que la grúa alcance su objetivo con timeout"""
        timeout = 30  # 30 segundos máximo
        tiempo_inicio = time.time()
        
        while not self.evento_parar.is_set():
            # Verificar timeout
            if time.time() - tiempo_inicio > timeout:
                self._log_evento("ERROR", "Timeout esperando objetivo de grúa", nivel="ERROR")
                break
            
            alcanzado = self.grua.actualizar_posicion(0.05)
            if alcanzado:
                break
            time.sleep(0.05)
    
    # ==================== CONTROL MANUAL ====================
    
    def mover_grua_manual(self, x: float, y: float):
        """Mueve la grúa manualmente a una posición"""
        if self.modo_operacion != ModoOperacion.MANUAL:
            return False
        
        if not self.sistema_encendido or self.parada_emergencia:
            return False
        
        self.grua.establecer_objetivo(x, y)
        return True
    
    def accionar_gancho_manual(self, cerrar: bool):
        """Controla el gancho manualmente"""
        if self.modo_operacion != ModoOperacion.MANUAL:
            return False
        
        if cerrar:
            self.grua.cerrar_gancho()
            self.grua.cargar_pieza()
        else:
            self.grua.soltar_pieza()
        
        return True
    
    # ==================== ACTUALIZACIÓN Y CALLBACKS ====================
    
    def actualizar(self):
        """Actualiza el estado de todos los subsistemas"""
        ahora = datetime.now()
        delta = (ahora - self.ultima_actualizacion).total_seconds()
        self.ultima_actualizacion = ahora
        
        # Actualizar posición de grúa si está en movimiento
        if self.grua.en_movimiento:
            self.grua.actualizar_posicion(delta)
        
        # Actualizar proceso si está activo
        if self.proceso.estado == EstadoProceso.EN_PROCESO:
            self.proceso.actualizar_proceso(delta)
        
        # Calcular tiempo de ciclo actual
        if self.ciclo_en_ejecucion and self.tiempo_inicio_ciclo:
            self.tiempo_ciclo_actual = (ahora - self.tiempo_inicio_ciclo).total_seconds()
        
        # Notificar a observadores
        self._notificar_actualizacion()
    
    def registrar_callback_actualizacion(self, callback: Callable):
        """Registra un callback para actualizaciones del sistema"""
        self.callbacks_actualizacion.append(callback)
    
    def registrar_callback_log(self, callback: Callable):
        """Registra un callback para eventos de log"""
        self.callbacks_log.append(callback)
    
    def _notificar_actualizacion(self):
        """Notifica a todos los callbacks de actualización"""
        for callback in self.callbacks_actualizacion:
            try:
                callback()
            except Exception as e:
                print(f"Error en callback: {e}")
    
    def _on_transicion_automata(self, estado_anterior, evento, estado_nuevo):
        """Callback para transiciones del autómata"""
        mensaje = f"Transición: {estado_anterior.value} --[{evento.value}]--> {estado_nuevo.value}"
        self._log_evento("TRANSICION", mensaje)
    
    def _log_evento(self, tipo: str, mensaje: str, nivel: str = "INFO"):
        """Registra un evento en el log del sistema"""
        log_entry = {
            'timestamp': datetime.now(),
            'tipo': tipo,
            'nivel': nivel,
            'mensaje': mensaje,
        }
        self.logs.append(log_entry)
        
        # Notificar callbacks de log
        for callback in self.callbacks_log:
            try:
                callback(log_entry)
            except Exception as e:
                print(f"Error en callback log: {e}")
    
    # ==================== GETTERS ====================
    
    def obtener_estado_completo(self) -> dict:
        """Retorna el estado completo del sistema"""
        return {
            'sistema_encendido': self.sistema_encendido,
            'modo_operacion': self.modo_operacion,
            'parada_emergencia': self.parada_emergencia,
            'ciclo_en_ejecucion': self.ciclo_en_ejecucion,
            'estado_automata': self.automata.estado_actual.value,
            'grua': self.grua.obtener_estado(),
            'proceso': self.proceso.obtener_estado(),
            'ciclos_completados': self.ciclos_completados,
            'tiempo_ciclo_actual': self.tiempo_ciclo_actual,
        }
    
    def obtener_logs(self, ultimos: int = 50) -> list:
        """Retorna los últimos logs del sistema"""
        return self.logs[-ultimos:]
