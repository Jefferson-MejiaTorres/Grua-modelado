"""
Sistema de Base de Datos para Control de Grúa Viga
Manejo de SQLite para almacenamiento local
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class BaseDatos:
    """
    Gestión de base de datos SQLite para el sistema de grúa
    
    Tablas:
    - estado_grua: Histórico de posiciones y estados
    - ciclos_cromado: Registro de ciclos de producción
    - logs_sistema: Eventos y alarmas del sistema
    """
    
    def __init__(self, db_path: str = "data/grua_sistema.db"):
        self.db_path = db_path
        self._crear_directorio()
        self._inicializar_base_datos()
    
    def _crear_directorio(self):
        """Crea el directorio data si no existe"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def _conectar(self):
        """Context manager para conexiones a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _inicializar_base_datos(self):
        """Crea las tablas si no existen"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            
            # Tabla: estado_grua
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS estado_grua (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    posicion_x REAL NOT NULL,
                    posicion_y REAL NOT NULL,
                    velocidad_x REAL,
                    velocidad_y REAL,
                    estado VARCHAR(50),
                    tiene_pieza BOOLEAN,
                    en_movimiento BOOLEAN
                )
            """)
            
            # Tabla: ciclos_cromado
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ciclos_cromado (
                    ciclo_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp_inicio DATETIME NOT NULL,
                    timestamp_fin DATETIME,
                    pieza_id VARCHAR(100),
                    tiempo_cromado_config INTEGER,
                    tiempo_cromado_real REAL,
                    corriente_electrolisis REAL,
                    voltaje_electrolisis REAL,
                    espesor_deposito REAL,
                    calidad_estimada REAL,
                    resultado VARCHAR(20),
                    observaciones TEXT
                )
            """)
            
            # Tabla: logs_sistema
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs_sistema (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tipo VARCHAR(50),
                    nivel VARCHAR(20),
                    mensaje TEXT
                )
            """)
            
            # Índices para mejorar rendimiento
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_estado_timestamp 
                ON estado_grua(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_ciclos_timestamp 
                ON ciclos_cromado(timestamp_inicio)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_logs_timestamp 
                ON logs_sistema(timestamp)
            """)
    
    # ==================== OPERACIONES ESTADO_GRUA ====================
    
    def insertar_estado_grua(self, estado: Dict[str, Any]) -> int:
        """
        Inserta un registro del estado de la grúa
        
        Args:
            estado: Diccionario con el estado de la grúa
            
        Returns:
            ID del registro insertado
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO estado_grua 
                (posicion_x, posicion_y, velocidad_x, velocidad_y, 
                 estado, tiene_pieza, en_movimiento)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                estado.get('posicion_x'),
                estado.get('posicion_y'),
                estado.get('velocidad_x'),
                estado.get('velocidad_y'),
                estado.get('estado'),
                estado.get('tiene_pieza'),
                estado.get('en_movimiento'),
            ))
            return cursor.lastrowid
    
    def obtener_ultimo_estado_grua(self) -> Optional[Dict]:
        """Obtiene el último estado registrado de la grúa"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM estado_grua 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def obtener_historico_posicion(self, limite: int = 100) -> List[Dict]:
        """Obtiene el histórico de posiciones"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, posicion_x, posicion_y 
                FROM estado_grua 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limite,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== OPERACIONES CICLOS_CROMADO ====================
    
    def iniciar_ciclo(self, pieza_id: str, tiempo_cromado: int, 
                     corriente: float, voltaje: float) -> int:
        """
        Registra el inicio de un ciclo de cromado
        
        Returns:
            ID del ciclo creado
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ciclos_cromado 
                (timestamp_inicio, pieza_id, tiempo_cromado_config, 
                 corriente_electrolisis, voltaje_electrolisis, resultado)
                VALUES (?, ?, ?, ?, ?, 'EN_PROCESO')
            """, (
                datetime.now(),
                pieza_id,
                tiempo_cromado,
                corriente,
                voltaje,
            ))
            return cursor.lastrowid
    
    def finalizar_ciclo(self, ciclo_id: int, tiempo_real: float, 
                       espesor: float, calidad: float, 
                       resultado: str, observaciones: str = ""):
        """
        Actualiza un ciclo con los datos finales
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ciclos_cromado 
                SET timestamp_fin = ?,
                    tiempo_cromado_real = ?,
                    espesor_deposito = ?,
                    calidad_estimada = ?,
                    resultado = ?,
                    observaciones = ?
                WHERE ciclo_id = ?
            """, (
                datetime.now(),
                tiempo_real,
                espesor,
                calidad,
                resultado,
                observaciones,
                ciclo_id,
            ))
    
    def obtener_ciclo(self, ciclo_id: int) -> Optional[Dict]:
        """Obtiene los datos de un ciclo específico"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ciclos_cromado 
                WHERE ciclo_id = ?
            """, (ciclo_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def obtener_ciclos_recientes(self, limite: int = 10) -> List[Dict]:
        """Obtiene los ciclos más recientes"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ciclos_cromado 
                ORDER BY timestamp_inicio DESC 
                LIMIT ?
            """, (limite,))
            return [dict(row) for row in cursor.fetchall()]
    
    def obtener_estadisticas_produccion(self) -> Dict:
        """Obtiene estadísticas de producción"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            
            # Total de piezas
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_piezas,
                    SUM(CASE WHEN resultado = 'EXITOSO' THEN 1 ELSE 0 END) as exitosas,
                    SUM(CASE WHEN resultado = 'FALLIDO' THEN 1 ELSE 0 END) as fallidas,
                    AVG(tiempo_cromado_real) as tiempo_promedio,
                    AVG(calidad_estimada) as calidad_promedia
                FROM ciclos_cromado
                WHERE timestamp_inicio >= date('now', '-7 days')
            """)
            row = cursor.fetchone()
            
            if row:
                total = row['total_piezas'] or 0
                exitosas = row['exitosas'] or 0
                tasa_exito = (exitosas / total * 100) if total > 0 else 0
                
                return {
                    'total_piezas': total,
                    'piezas_exitosas': exitosas,
                    'piezas_fallidas': row['fallidas'] or 0,
                    'tasa_exito': tasa_exito,
                    'tiempo_promedio': row['tiempo_promedio'] or 0,
                    'calidad_promedia': row['calidad_promedia'] or 0,
                }
            
            return {
                'total_piezas': 0,
                'piezas_exitosas': 0,
                'piezas_fallidas': 0,
                'tasa_exito': 0,
                'tiempo_promedio': 0,
                'calidad_promedia': 0,
            }
    
    # ==================== OPERACIONES LOGS_SISTEMA ====================
    
    def insertar_log(self, tipo: str, nivel: str, mensaje: str):
        """Inserta un registro de log"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO logs_sistema (tipo, nivel, mensaje)
                VALUES (?, ?, ?)
            """, (tipo, nivel, mensaje))
    
    def obtener_logs(self, limite: int = 50, nivel: Optional[str] = None) -> List[Dict]:
        """
        Obtiene los logs del sistema
        
        Args:
            limite: Número máximo de logs a retornar
            nivel: Filtrar por nivel (INFO, WARNING, ERROR)
        """
        with self._conectar() as conn:
            cursor = conn.cursor()
            
            if nivel:
                cursor.execute("""
                    SELECT * FROM logs_sistema 
                    WHERE nivel = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (nivel, limite))
            else:
                cursor.execute("""
                    SELECT * FROM logs_sistema 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limite,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def limpiar_logs_antiguos(self, dias: int = 30):
        """Elimina logs más antiguos que X días"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM logs_sistema 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            """, (dias,))
            return cursor.rowcount
    
    # ==================== UTILIDADES ====================
    
    def ejecutar_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Ejecuta una query personalizada"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def vaciar_tabla(self, nombre_tabla: str):
        """Limpia todos los datos de una tabla"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {nombre_tabla}")
    
    def obtener_tamano_bd(self) -> float:
        """Retorna el tamaño de la base de datos en MB"""
        if os.path.exists(self.db_path):
            return os.path.getsize(self.db_path) / (1024 * 1024)
        return 0.0
    
    def crear_backup(self, ruta_backup: Optional[str] = None):
        """Crea un backup de la base de datos"""
        if not ruta_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_backup = f"data/backup_grua_{timestamp}.db"
        
        import shutil
        shutil.copy2(self.db_path, ruta_backup)
        return ruta_backup
