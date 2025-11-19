"""
Interfaz Gráfica HMI - Sistema de Control de Grúa Viga
Vista principal con visualización según norma ISA 5.1
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Importación segura de matplotlib
try:
    import matplotlib
    matplotlib.use('TkAgg')  # Backend para Tkinter
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False
    print("⚠️  Matplotlib no disponible. Gráficas deshabilitadas.")

import config.config as cfg
from controllers.controlador_plc import ControladorPLC, ModoOperacion


class InterfazHMI:
    """
    Interfaz gráfica del sistema de control (patrón MVC - Vista)
    Cumple con norma ISA 5.1 para instrumentación industrial
    """
    
    def __init__(self, controlador: ControladorPLC):
        self.controlador = controlador
        
        # Ventana principal
        self.root = tk.Tk()
        self.root.title(cfg.VENTANA['titulo'])
        self.root.geometry(f"{cfg.VENTANA['ancho']}x{cfg.VENTANA['alto']}")
        self.root.configure(bg=cfg.COLORES_UI['fondo'])
        
        # Variables de UI
        self.var_sistema = tk.BooleanVar(value=False)
        self.var_modo = tk.StringVar(value=ModoOperacion.AUTOMATICO)
        self.var_tiempo_cromado = tk.IntVar(value=cfg.PROCESO_CROMADO['tiempo_default'])
        
        # Canvas para visualización de grúa
        self.canvas = None
        self.canvas_elementos = {}
        self.elementos_temporales = []  # Para elementos que se borran (estelas, sombras)
        
        # Sistema de estela de movimiento
        self.estela_posiciones = []  # Historial de posiciones para dibujar estela
        self.max_estela = 15  # Número máximo de puntos en la estela
        self.mostrar_estela = True
        
        # Gráficas (solo si matplotlib está disponible)
        self.fig_graficas = None
        self.ax_posicion = None
        self.ax_velocidad = None
        self.canvas_graficas = None
        self.frame_graficas = None
        
        # Históricos para gráficas
        self.hist_tiempo = []
        self.hist_pos_x = []
        self.hist_pos_y = []
        self.hist_vel_x = []
        self.hist_vel_y = []
        self.max_puntos_grafica = 100
        
        # Construir interfaz
        self._construir_interfaz()
        
        # Registrar callbacks con controlador
        self.controlador.registrar_callback_actualizacion(self._actualizar_visualizacion)
        self.controlador.registrar_callback_log(self._agregar_log)
        
        # Iniciar bucle de actualización
        self._actualizar_periodicamente()
    
    def _construir_interfaz(self):
        """Construye todos los componentes de la interfaz"""
        
        # Frame superior - Panel de control
        frame_control = tk.Frame(self.root, bg=cfg.COLORES_UI['panel'], 
                                relief=tk.RAISED, bd=2)
        frame_control.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self._construir_panel_control(frame_control)
        
        # Frame central - Área de trabajo
        frame_central = tk.Frame(self.root, bg=cfg.COLORES_UI['fondo'])
        frame_central.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5)
        
        # Dividir en izquierda (visualización) y derecha (información)
        frame_izq = tk.Frame(frame_central, bg=cfg.COLORES_UI['panel'], 
                            relief=tk.RAISED, bd=2)
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        frame_der = tk.Frame(frame_central, bg=cfg.COLORES_UI['panel'], 
                            relief=tk.RAISED, bd=2, width=400)
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        frame_der.pack_propagate(False)
        
        # Construir secciones
        self._construir_visualizacion_grua(frame_izq)
        self._construir_panel_informacion(frame_der)
        
        # Frame inferior - Gráficas
        frame_graficas = tk.Frame(self.root, bg=cfg.COLORES_UI['panel'], 
                                 relief=tk.RAISED, bd=2, height=250)
        frame_graficas.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        frame_graficas.pack_propagate(False)
        self._construir_graficas(frame_graficas)
    
    def _construir_panel_control(self, parent):
        """Panel superior de control"""
        
        # Frame izquierdo - Controles principales
        frame_izq = tk.Frame(parent, bg=cfg.COLORES_UI['panel'])
        frame_izq.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Botón de encendido/apagado con estilo mejorado
        self.btn_sistema = tk.Button(
            frame_izq, text="⚡ ENCENDER SISTEMA", 
            font=('Arial', 13, 'bold'),
            bg=cfg.COLORES_UI['boton_activo'], fg='white',
            activebackground='#66BB6A',
            command=self._toggle_sistema, width=22, height=2,
            relief=tk.RAISED, bd=5, cursor='hand2',
            highlightthickness=2, highlightbackground='#81C784'
        )
        self.btn_sistema.pack(pady=8)
        # Efecto hover
        self.btn_sistema.bind('<Enter>', lambda e: e.widget.config(bg='#66BB6A' if 'ENCENDER' in e.widget['text'] else '#E53935'))
        self.btn_sistema.bind('<Leave>', lambda e: e.widget.config(bg=cfg.COLORES_UI['boton_activo'] if 'ENCENDER' in e.widget['text'] else cfg.COLORES_UI['emergencia']))
        
        # Selector de modo
        frame_modo = tk.LabelFrame(frame_izq, text="Modo de Operación",
                                  bg=cfg.COLORES_UI['panel'], fg=cfg.COLORES_UI['texto'],
                                  font=('Arial', 10, 'bold'))
        frame_modo.pack(pady=5, fill=tk.X)
        
        tk.Radiobutton(
            frame_modo, text="AUTOMÁTICO", variable=self.var_modo,
            value=ModoOperacion.AUTOMATICO, bg=cfg.COLORES_UI['panel'],
            fg=cfg.COLORES_UI['texto'], selectcolor=cfg.COLORES_UI['panel'],
            font=('Arial', 10), command=self._cambiar_modo
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        tk.Radiobutton(
            frame_modo, text="MANUAL", variable=self.var_modo,
            value=ModoOperacion.MANUAL, bg=cfg.COLORES_UI['panel'],
            fg=cfg.COLORES_UI['texto'], selectcolor=cfg.COLORES_UI['panel'],
            font=('Arial', 10), command=self._cambiar_modo
        ).pack(anchor=tk.W, padx=10, pady=2)
        
        # Frame central - Parámetros
        frame_centro = tk.Frame(parent, bg=cfg.COLORES_UI['panel'])
        frame_centro.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Configuración tiempo de cromado
        frame_tiempo = tk.LabelFrame(frame_centro, text="Tiempo de Cromado (ISA TI-001)",
                                    bg=cfg.COLORES_UI['panel'], fg=cfg.COLORES_UI['texto'],
                                    font=('Arial', 10, 'bold'))
        frame_tiempo.pack(pady=5)
        
        tk.Label(frame_tiempo, text="Setpoint (segundos):",
                bg=cfg.COLORES_UI['panel'], fg='#FFD700',
                font=('Arial', 10, 'bold')).pack(pady=3)
        
        # Frame para spinbox con mejor diseño
        frame_spin = tk.Frame(frame_tiempo, bg='#1a1a1a', relief=tk.SUNKEN, bd=2)
        frame_spin.pack(pady=5, padx=10)
        
        spinbox_tiempo = tk.Spinbox(
            frame_spin, from_=cfg.PROCESO_CROMADO['tiempo_min'],
            to=cfg.PROCESO_CROMADO['tiempo_max'],
            textvariable=self.var_tiempo_cromado,
            font=('Arial', 14, 'bold'), width=8,
            bg='#2a2a2a', fg='#00FF00', buttonbackground='#4CAF50',
            relief=tk.FLAT, justify=tk.CENTER,
            command=self._actualizar_tiempo_cromado
        )
        spinbox_tiempo.pack(padx=3, pady=3)
        # Binding adicional para detectar cambios manuales
        spinbox_tiempo.bind('<Return>', lambda e: self._actualizar_tiempo_cromado())
        spinbox_tiempo.bind('<FocusOut>', lambda e: self._actualizar_tiempo_cromado())
        
        # Label de confirmación
        self.label_tiempo_confirmacion = tk.Label(
            frame_tiempo, text="✓ Configurado",
            bg=cfg.COLORES_UI['panel'], fg='#4CAF50',
            font=('Arial', 8, 'italic')
        )
        self.label_tiempo_confirmacion.pack(pady=2)
        
        # Frame derecho - Controles de ciclo
        frame_der = tk.Frame(parent, bg=cfg.COLORES_UI['panel'])
        frame_der.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.btn_marcha = tk.Button(
            frame_der, text="▶ MARCHA\n(Iniciar Ciclo)",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50', fg='white', activebackground='#66BB6A',
            command=self._iniciar_ciclo, width=16, height=3,
            relief=tk.RAISED, bd=5, cursor='hand2',
            highlightthickness=2, highlightbackground='#81C784'
        )
        self.btn_marcha.pack(pady=8)
        # Efecto hover
        self.btn_marcha.bind('<Enter>', lambda e: self.btn_marcha.config(bg='#66BB6A'))
        self.btn_marcha.bind('<Leave>', lambda e: self.btn_marcha.config(bg='#4CAF50'))
        
        self.btn_paro = tk.Button(
            frame_der, text="⏸ PARO\n(Detener Ciclo)",
            font=('Arial', 12, 'bold'),
            bg='#FF9800', fg='white', activebackground='#FFB74D',
            command=self._detener_ciclo, width=16, height=3,
            relief=tk.RAISED, bd=5, cursor='hand2',
            highlightthickness=2, highlightbackground='#FFCC80'
        )
        self.btn_paro.pack(pady=8)
        # Efecto hover
        self.btn_paro.bind('<Enter>', lambda e: self.btn_paro.config(bg='#FFB74D'))
        self.btn_paro.bind('<Leave>', lambda e: self.btn_paro.config(bg='#FF9800'))
        
        # Frame extremo derecho - Emergencia
        frame_emer = tk.Frame(parent, bg=cfg.COLORES_UI['panel'])
        frame_emer.pack(side=tk.RIGHT, padx=10, pady=10)
        
        self.btn_emergencia = tk.Button(
            frame_emer, text="🛑 PARADA\nEMERGENCIA",
            font=('Arial', 13, 'bold'),
            bg=cfg.COLORES_UI['emergencia'], fg='white', activebackground='#E53935',
            command=self._parada_emergencia, width=16, height=3,
            relief=tk.RAISED, bd=6, cursor='hand2',
            highlightthickness=3, highlightbackground='#FF5252'
        )
        self.btn_emergencia.pack(pady=8)
        # Efecto hover pulsante
        self.btn_emergencia.bind('<Enter>', lambda e: self.btn_emergencia.config(bg='#E53935', bd=8))
        self.btn_emergencia.bind('<Leave>', lambda e: self.btn_emergencia.config(bg=cfg.COLORES_UI['emergencia'], bd=6))
        
        self.btn_reset = tk.Button(
            frame_emer, text="🔄 RESET",
            font=('Arial', 11, 'bold'),
            bg='#2196F3', fg='white', activebackground='#42A5F5',
            command=self._reset_sistema, width=16,
            relief=tk.RAISED, bd=4, cursor='hand2',
            highlightthickness=2, highlightbackground='#64B5F6'
        )
        self.btn_reset.pack(pady=5)
        # Efecto hover
        self.btn_reset.bind('<Enter>', lambda e: self.btn_reset.config(bg='#42A5F5'))
        self.btn_reset.bind('<Leave>', lambda e: self.btn_reset.config(bg='#2196F3'))
    
    def _construir_visualizacion_grua(self, parent):
        """Construye el área de visualización de la grúa"""
        
        # Título
        tk.Label(parent, text="Visualización del Sistema - Norma ISA 5.1",
                font=('Arial', 12, 'bold'), bg=cfg.COLORES_UI['panel'],
                fg=cfg.COLORES_UI['texto']).pack(pady=5)
        
        # Canvas para dibujar
        self.canvas = tk.Canvas(
            parent, width=cfg.AREA_TRABAJO['ancho'], 
            height=cfg.AREA_TRABAJO['alto'],
            bg='#0a0a0a', highlightthickness=2,
            highlightbackground=cfg.COLORES_UI['texto']
        )
        self.canvas.pack(pady=10)
        
        # Dibujar elementos estáticos
        self._dibujar_escenario_base()
    
    def _dibujar_escenario_base(self):
        """Dibuja los elementos estáticos del escenario"""
        
        # Fondo con gradiente simulado
        self.canvas.create_rectangle(
            0, 0, cfg.AREA_TRABAJO['ancho'], cfg.AREA_TRABAJO['alto'],
            fill='#0a0a0a', outline=''
        )
        
        # Viga principal (línea horizontal superior) con sombra
        self.canvas.create_line(
            50, 52, cfg.AREA_TRABAJO['ancho']-50, 52,
            fill='#1a1a1a', width=10
        )
        self.canvas.create_line(
            50, 50, cfg.AREA_TRABAJO['ancho']-50, 50,
            fill=cfg.COLORES_UI['linea_grua'], width=8
        )
        
        # Línea de piso industrial
        self.canvas.create_line(
            30, cfg.AREA_TRABAJO['alto']-30, cfg.AREA_TRABAJO['ancho']-30, cfg.AREA_TRABAJO['alto']-30,
            fill='#404040', width=3, dash=(10, 5)
        )
        
        # Estación de CARGA (HOME)
        x1, y1 = cfg.POSICIONES['CARGA']
        self._dibujar_estacion(x1, y1, "ESTACIÓN\nCARGA", '#4CAF50', 'PS-001')
        
        # Estación de CROMADO
        x2, y2 = cfg.POSICIONES['CROMADO']
        self._dibujar_estacion(x2, y2, "ESTACIÓN\nCROMADO", '#2196F3', 'PS-002')
        
        # Estación de DESCARGA
        x3, y3 = cfg.POSICIONES['DESCARGA']
        self._dibujar_estacion(x3, y3, "ESTACIÓN\nDESCARGA", '#FF9800', 'PS-003')
        
        # Dibujar grúa inicial
        self._actualizar_dibujo_grua()
    
    def _dibujar_estacion(self, x, y, texto, color, tag_isa):
        """Dibuja una estación de trabajo con estilo mejorado"""
        ancho = cfg.TAMANHOS['estacion_ancho']
        alto = cfg.TAMANHOS['estacion_alto']
        
        # Sombra de la estación
        self.canvas.create_rectangle(
            x - ancho//2 + 3, y + 3, x + ancho//2 + 3, y + alto + 3,
            fill='#000000', outline='', stipple='gray50'
        )
        
        # Base de la estación con gradiente simulado
        self.canvas.create_rectangle(
            x - ancho//2, y, x + ancho//2, y + alto//3,
            fill=color, outline=''
        )
        self.canvas.create_rectangle(
            x - ancho//2, y + alto//3, x + ancho//2, y + alto,
            fill=self._oscurecer_color(color), outline='white', width=2
        )
        
        # Borde superior decorativo
        self.canvas.create_rectangle(
            x - ancho//2, y - 5, x + ancho//2, y,
            fill='#2a2a2a', outline='white', width=1
        )
        
        # Etiqueta principal
        self.canvas.create_text(
            x, y + alto//2, text=texto,
            fill='white', font=('Arial', 10, 'bold')
        )
        
        # Tag ISA en la parte superior
        self.canvas.create_rectangle(
            x - 30, y - 25, x + 30, y - 8,
            fill='#1a1a1a', outline=color, width=2
        )
        self.canvas.create_text(
            x, y - 16, text=tag_isa,
            fill=color, font=('Arial', 8, 'bold')
        )
    
    def _oscurecer_color(self, color_hex):
        """Oscurece un color hexadecimal para efecto de gradiente"""
        try:
            color_hex = color_hex.lstrip('#')
            r, g, b = int(color_hex[0:2], 16), int(color_hex[2:4], 16), int(color_hex[4:6], 16)
            r, g, b = int(r * 0.6), int(g * 0.6), int(b * 0.6)
            return f'#{r:02x}{g:02x}{b:02x}'
        except:
            return color_hex
    
    def _dibujar_estela_movimiento(self):
        """Dibuja la estela de movimiento con efecto fade"""
        if len(self.estela_posiciones) < 2:
            return
        
        # Dibujar líneas conectando las posiciones con transparencia creciente
        for i in range(len(self.estela_posiciones) - 1):
            x1, y1 = self.estela_posiciones[i]
            x2, y2 = self.estela_posiciones[i + 1]
            
            # Calcular opacidad (más reciente = más opaco)
            alpha = int(255 * (i + 1) / len(self.estela_posiciones))
            
            # Color de la estela con fade
            if alpha < 100:
                color = '#1a1a2e'
            elif alpha < 180:
                color = '#3a3a5e'
            else:
                color = '#5a5a8e'
            
            # Grosor variable (más reciente = más grueso)
            width = 1 + (i * 2 // len(self.estela_posiciones))
            
            # Dibujar línea de estela
            linea = self.canvas.create_line(
                x1, y1, x2, y2,
                fill=color, width=width, smooth=True
            )
            self.elementos_temporales.append(linea)
            
            # Puntos en la estela
            if i % 2 == 0:  # Dibujar puntos alternados
                punto = self.canvas.create_oval(
                    x1 - 2, y1 - 2, x1 + 2, y1 + 2,
                    fill=color, outline=''
                )
                self.elementos_temporales.append(punto)
    
    def _limpiar_estela(self):
        """Limpia completamente la estela de movimiento"""
        self.estela_posiciones.clear()
        for elemento in self.elementos_temporales:
            try:
                self.canvas.delete(elemento)
            except:
                pass
        self.elementos_temporales.clear()
    
    def _actualizar_dibujo_grua(self):
        """Actualiza la visualización de la grúa con estela de movimiento"""
        # Limpiar elementos temporales (estelas, sombras antiguas)
        for elemento in self.elementos_temporales:
            try:
                self.canvas.delete(elemento)
            except:
                pass
        self.elementos_temporales.clear()
        
        # Eliminar elementos principales anteriores
        if 'grua_carro' in self.canvas_elementos:
            self.canvas.delete(self.canvas_elementos['grua_carro'])
            self.canvas.delete(self.canvas_elementos['gancho'])
            if 'pieza' in self.canvas_elementos:
                self.canvas.delete(self.canvas_elementos['pieza'])
        
        # Obtener posición actual
        x, y = self.controlador.grua.obtener_posicion()
        
        # Actualizar historial de estela
        if self.controlador.grua.en_movimiento and self.mostrar_estela:
            self.estela_posiciones.append((x, y))
            if len(self.estela_posiciones) > self.max_estela:
                self.estela_posiciones.pop(0)
        
        # Dibujar estela de movimiento
        if len(self.estela_posiciones) > 1 and self.mostrar_estela:
            self._dibujar_estela_movimiento()
        
        # Dibujar carro de la grúa
        ancho_grua = cfg.TAMANHOS['grua_ancho']
        alto_grua = cfg.TAMANHOS['grua_alto']
        
        # Sombra del carro (temporal)
        sombra_carro = self.canvas.create_rectangle(
            x - ancho_grua//2 + 2, 52, x + ancho_grua//2 + 2, 50 + alto_grua + 2,
            fill='#0a0a0a', outline=''
        )
        self.elementos_temporales.append(sombra_carro)
        
        # Carro de la grúa con gradiente
        self.canvas.create_rectangle(
            x - ancho_grua//2, 50, x + ancho_grua//2, 50 + alto_grua//2,
            fill=cfg.COLORES_UI['linea_grua'], outline=''
        )
        self.canvas_elementos['grua_carro'] = self.canvas.create_rectangle(
            x - ancho_grua//2, 50 + alto_grua//2, x + ancho_grua//2, 50 + alto_grua,
            fill=self._oscurecer_color(cfg.COLORES_UI['linea_grua']), outline='black', width=2
        )
        
        # Ruedas del carro (temporales)
        rueda1 = self.canvas.create_oval(x - ancho_grua//2 + 5, 50, x - ancho_grua//2 + 15, 60, fill='#2a2a2a', outline='white', width=1)
        rueda2 = self.canvas.create_oval(x + ancho_grua//2 - 15, 50, x + ancho_grua//2 - 5, 60, fill='#2a2a2a', outline='white', width=1)
        self.elementos_temporales.extend([rueda1, rueda2])
        
        # Dibujar gancho
        largo_gancho = cfg.TAMANHOS['gancho_largo']
        
        # Cable del gancho con sombra (temporales)
        cable_sombra = self.canvas.create_line(
            x + 1, 50 + alto_grua + 1, x + 1, y - largo_gancho//2 + 1,
            fill='#1a1a1a', width=4
        )
        cable = self.canvas.create_line(
            x, 50 + alto_grua, x, y - largo_gancho//2,
            fill=cfg.COLORES_UI['gancho'], width=3
        )
        self.elementos_temporales.extend([cable_sombra, cable])
        
        # Gancho mejorado
        self.canvas_elementos['gancho'] = self.canvas.create_oval(
            x - 10, y - largo_gancho//2, x + 10, y + largo_gancho//2,
            fill=cfg.COLORES_UI['gancho'], outline='black', width=2
        )
        # Detalle del gancho (temporal)
        detalle_gancho = self.canvas.create_oval(
            x - 5, y - largo_gancho//2 + 5, x + 5, y + 5,
            fill='#ff9999', outline=''
        )
        self.elementos_temporales.append(detalle_gancho)
        
        # Dibujar pieza si está cargada
        if self.controlador.grua.tiene_pieza:
            ancho_pieza = cfg.TAMANHOS['pieza_ancho']
            alto_pieza = cfg.TAMANHOS['pieza_alto']
            
            # Sombra de la pieza (temporal)
            sombra_pieza = self.canvas.create_rectangle(
                x - ancho_pieza//2 + 2, y + 2, x + ancho_pieza//2 + 2, y + alto_pieza + 2,
                fill='#000000', outline='', stipple='gray50'
            )
            self.elementos_temporales.append(sombra_pieza)
            
            self.canvas_elementos['pieza'] = self.canvas.create_rectangle(
                x - ancho_pieza//2, y, x + ancho_pieza//2, y + alto_pieza,
                fill=cfg.COLORES_UI['pieza'], outline='black', width=2
            )
            
            # Brillo en la pieza (temporal)
            brillo_pieza = self.canvas.create_rectangle(
                x - ancho_pieza//2 + 5, y + 5, x - ancho_pieza//2 + 15, y + 10,
                fill='white', outline='', stipple='gray25'
            )
            self.elementos_temporales.append(brillo_pieza)
    
    def _construir_panel_informacion(self, parent):
        """Panel de información y estado"""
        
        # Notebook para pestañas
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Pestaña 1: Estado del sistema
        tab_estado = tk.Frame(notebook, bg=cfg.COLORES_UI['panel'])
        notebook.add(tab_estado, text="Estado del Sistema")
        self._construir_tab_estado(tab_estado)
        
        # Pestaña 2: Proceso de Cromado
        tab_proceso = tk.Frame(notebook, bg=cfg.COLORES_UI['panel'])
        notebook.add(tab_proceso, text="Proceso de Cromado")
        self._construir_tab_proceso(tab_proceso)
        
        # Pestaña 3: Logs
        tab_logs = tk.Frame(notebook, bg=cfg.COLORES_UI['panel'])
        notebook.add(tab_logs, text="Logs del Sistema")
        self._construir_tab_logs(tab_logs)
    
    def _construir_tab_estado(self, parent):
        """Construye la pestaña de estado"""
        
        # Frame scrollable
        canvas = tk.Canvas(parent, bg=cfg.COLORES_UI['panel'])
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        frame_contenido = tk.Frame(canvas, bg=cfg.COLORES_UI['panel'])
        
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas.create_window((0, 0), window=frame_contenido, anchor='nw')
        
        # Labels de estado
        self.labels_estado = {}
        
        categorias = [
            ("Sistema", ['sistema_encendido', 'modo_operacion', 'parada_emergencia']),
            ("Ciclo", ['estado_automata', 'ciclo_en_ejecucion', 'ciclos_completados']),
            ("Grúa (PI-001)", ['posicion_x', 'posicion_y', 'tiene_pieza', 'en_movimiento']),
            ("Proceso (PC-001)", ['estado_proceso', 'progreso', 'tiempo_restante']),
        ]
        
        for categoria, campos in categorias:
            frame_cat = tk.LabelFrame(
                frame_contenido, text=categoria,
                bg=cfg.COLORES_UI['panel'], fg=cfg.COLORES_UI['texto'],
                font=('Arial', 10, 'bold')
            )
            frame_cat.pack(fill=tk.X, padx=10, pady=5)
            
            for campo in campos:
                frame_campo = tk.Frame(frame_cat, bg='#1a1a1a', relief=tk.GROOVE, bd=1)
                frame_campo.pack(fill=tk.X, padx=8, pady=3)
                
                tk.Label(
                    frame_campo, text=f"{campo.replace('_', ' ').title()}:",
                    bg='#1a1a1a', fg='#FFD700',
                    font=('Arial', 10, 'bold'), anchor='w'
                ).pack(side=tk.LEFT, padx=8, pady=4)
                
                label_valor = tk.Label(
                    frame_campo, text="-",
                    bg='#1a1a1a', fg='#00FF00',
                    font=('Arial', 10, 'bold'), anchor='e'
                )
                label_valor.pack(side=tk.RIGHT, padx=8, pady=4)
                
                self.labels_estado[campo] = label_valor
        
        frame_contenido.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    def _construir_tab_proceso(self, parent):
        """Construye la pestaña del proceso de cromado"""
        
        self.labels_proceso = {}
        
        # Parámetros eléctricos
        frame_elec = tk.LabelFrame(
            parent, text="⚡ Parámetros Eléctricos (ISA 5.1)",
            bg=cfg.COLORES_UI['panel'], fg='#FFD700',
            font=('Arial', 11, 'bold'), relief=tk.GROOVE, bd=3
        )
        frame_elec.pack(fill=tk.X, padx=10, pady=10)
        
        for param, unidad, color in [('Corriente', 'A', '#FF9800'), ('Voltaje', 'V', '#2196F3')]:
            frame = tk.Frame(frame_elec, bg='#1a1a1a', relief=tk.SUNKEN, bd=2)
            frame.pack(fill=tk.X, padx=8, pady=6)
            
            tk.Label(frame, text=f"⚡ {param} ({unidad}):",
                    bg='#1a1a1a', fg=color,
                    font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10, pady=6)
            
            label = tk.Label(frame, text="-",
                           bg='#1a1a1a', fg='#00FF00',
                           font=('Arial', 14, 'bold'))
            label.pack(side=tk.RIGHT, padx=10, pady=6)
            
            self.labels_proceso[param.lower()] = label
        
        # Barra de progreso
        frame_prog = tk.LabelFrame(
            parent, text="📊 Progreso del Cromado",
            bg=cfg.COLORES_UI['panel'], fg='#FFD700',
            font=('Arial', 11, 'bold'), relief=tk.GROOVE, bd=3
        )
        frame_prog.pack(fill=tk.X, padx=10, pady=10)
        
        # Crear estilo personalizado para la barra
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Horizontal.TProgressbar",
                       troughcolor='#1a1a1a',
                       background='#4CAF50',
                       darkcolor='#4CAF50',
                       lightcolor='#66BB6A',
                       bordercolor='#2d2d2d',
                       thickness=30)
        
        self.progressbar_cromado = ttk.Progressbar(
            frame_prog, mode='determinate', length=400,
            style="Horizontal.TProgressbar"
        )
        self.progressbar_cromado.pack(padx=10, pady=10)
        
        self.label_progreso = tk.Label(
            frame_prog, text="0%",
            bg=cfg.COLORES_UI['panel'], fg='#00FF00',
            font=('Arial', 16, 'bold')
        )
        self.label_progreso.pack(pady=5)
        
        # Estadísticas
        frame_stats = tk.LabelFrame(
            parent, text="📈 Estadísticas de Producción",
            bg=cfg.COLORES_UI['panel'], fg='#FFD700',
            font=('Arial', 11, 'bold'), relief=tk.GROOVE, bd=3
        )
        frame_stats.pack(fill=tk.X, padx=10, pady=10)
        
        stats_config = [
            ('piezas_procesadas', '📦', '#2196F3'),
            ('piezas_exitosas', '✅', '#4CAF50'),
            ('tasa_exito', '💯', '#FF9800')
        ]
        
        for stat, icon, color in stats_config:
            frame = tk.Frame(frame_stats, bg='#1a1a1a', relief=tk.SUNKEN, bd=2)
            frame.pack(fill=tk.X, padx=8, pady=5)
            
            tk.Label(frame, text=f"{icon} {stat.replace('_', ' ').title()}:",
                    bg='#1a1a1a', fg=color,
                    font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10, pady=6)
            
            label = tk.Label(frame, text="-",
                           bg='#1a1a1a', fg='#00FFFF',
                           font=('Arial', 12, 'bold'))
            label.pack(side=tk.RIGHT, padx=10, pady=6)
            
            self.labels_proceso[stat] = label
    
    def _construir_tab_logs(self, parent):
        """Construye la pestaña de logs"""
        
        # Text widget con scrollbar
        frame_logs = tk.Frame(parent, bg=cfg.COLORES_UI['panel'])
        frame_logs.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(frame_logs)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.text_logs = tk.Text(
            frame_logs, height=20, bg='#1a1a1a', fg='#00FF00',
            font=('Consolas', 9), yscrollcommand=scrollbar.set
        )
        self.text_logs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_logs.yview)
        
        # Configurar tags para colores
        self.text_logs.tag_config('INFO', foreground='#00FF00')
        self.text_logs.tag_config('WARNING', foreground='#FFFF00')
        self.text_logs.tag_config('ERROR', foreground='#FF0000')
    
    def _construir_graficas(self, parent):
        """Construye las gráficas de desempeño"""
        
        if not MATPLOTLIB_DISPONIBLE:
            # Mostrar mensaje si matplotlib no está disponible
            tk.Label(
                parent, 
                text="⚠️ Gráficas no disponibles (matplotlib no instalado)\nEjecute: pip install matplotlib",
                bg=cfg.COLORES_UI['panel'], fg='yellow',
                font=('Arial', 12, 'bold'), justify=tk.CENTER
            ).pack(expand=True)
            return
        
        # Crear figura de matplotlib
        self.fig_graficas = Figure(figsize=(12, 3), facecolor=cfg.COLORES_UI['panel'])
        
        # Subplot 1: Posición
        self.ax_posicion = self.fig_graficas.add_subplot(121)
        self.ax_posicion.set_title('Posición de la Grúa (PI-001)', color='white')
        self.ax_posicion.set_xlabel('Tiempo (s)', color='white')
        self.ax_posicion.set_ylabel('Posición', color='white')
        self.ax_posicion.tick_params(colors='white')
        self.ax_posicion.set_facecolor('#1a1a1a')
        
        # Subplot 2: Velocidad
        self.ax_velocidad = self.fig_graficas.add_subplot(122)
        self.ax_velocidad.set_title('Velocidad (SC-001)', color='white')
        self.ax_velocidad.set_xlabel('Tiempo (s)', color='white')
        self.ax_velocidad.set_ylabel('Velocidad', color='white')
        self.ax_velocidad.tick_params(colors='white')
        self.ax_velocidad.set_facecolor('#1a1a1a')
        
        # Integrar con tkinter
        self.canvas_graficas = FigureCanvasTkAgg(self.fig_graficas, parent)
        self.canvas_graficas.draw()
        self.canvas_graficas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # ==================== CALLBACKS DE EVENTOS ====================
    
    def _toggle_sistema(self):
        """Enciende o apaga el sistema"""
        if not self.var_sistema.get():
            self.controlador.encender_sistema()
            self.var_sistema.set(True)
            self.btn_sistema.config(
                text="🔴 APAGAR SISTEMA",
                bg=cfg.COLORES_UI['emergencia'],
                activebackground='#E53935',
                highlightbackground='#FF5252'
            )
        else:
            self.controlador.apagar_sistema()
            self.var_sistema.set(False)
            self.btn_sistema.config(
                text="⚡ ENCENDER SISTEMA",
                bg=cfg.COLORES_UI['boton_activo'],
                activebackground='#66BB6A',
                highlightbackground='#81C784'
            )
    
    def _cambiar_modo(self):
        """Cambia el modo de operación"""
        modo = self.var_modo.get()
        self.controlador.cambiar_modo(modo)
    
    def _actualizar_tiempo_cromado(self):
        """Actualiza el tiempo de cromado configurado"""
        try:
            tiempo = self.var_tiempo_cromado.get()
            if self.controlador.proceso.configurar_tiempo(tiempo):
                self.label_tiempo_confirmacion.config(
                    text=f"✓ {tiempo}s configurado",
                    fg='#4CAF50'
                )
            else:
                self.label_tiempo_confirmacion.config(
                    text=f"⚠ Rango: 30-600s",
                    fg='#FF9800'
                )
        except:
            pass
    
    def _iniciar_ciclo(self):
        """Inicia el ciclo automático"""
        if self.controlador.iniciar_ciclo_automatico():
            messagebox.showinfo("Ciclo Iniciado", "El ciclo automático ha comenzado")
        else:
            messagebox.showerror("Error", "No se pudo iniciar el ciclo. Verifique el estado del sistema.")
    
    def _detener_ciclo(self):
        """Detiene el ciclo en ejecución"""
        self.controlador.detener_ciclo()
        messagebox.showinfo("Ciclo Detenido", "El ciclo ha sido detenido")
    
    def _parada_emergencia(self):
        """Activa la parada de emergencia"""
        respuesta = messagebox.askyesno(
            "Parada de Emergencia",
            "¿Confirma activar la PARADA DE EMERGENCIA?"
        )
        if respuesta:
            self.controlador.activar_parada_emergencia()
    
    def _reset_sistema(self):
        """Resetea el sistema después de emergencia"""
        self.controlador.resetear_emergencia()
        messagebox.showinfo("Sistema Reseteado", "El sistema ha sido reseteado")
    
    # ==================== ACTUALIZACIÓN DE UI ====================
    
    def _actualizar_visualizacion(self):
        """Callback para actualizar la visualización"""
        pass  # La actualización se hace en _actualizar_periodicamente
    
    def _agregar_log(self, log_entry):
        """Callback para agregar un log"""
        timestamp = log_entry['timestamp'].strftime('%H:%M:%S')
        nivel = log_entry['nivel']
        mensaje = log_entry['mensaje']
        
        linea = f"[{timestamp}] [{nivel}] {mensaje}\n"
        self.text_logs.insert(tk.END, linea, nivel)
        self.text_logs.see(tk.END)
        
        # Limitar número de líneas
        if int(self.text_logs.index('end-1c').split('.')[0]) > 500:
            self.text_logs.delete('1.0', '2.0')
    
    def _actualizar_periodicamente(self):
        """Actualiza la UI periódicamente"""
        
        # Actualizar controlador
        self.controlador.actualizar()
        
        # Actualizar visualización de grúa
        self._actualizar_dibujo_grua()
        
        # Actualizar labels de estado
        self._actualizar_labels_estado()
        
        # Actualizar gráficas
        self._actualizar_graficas()
        
        # Programar siguiente actualización
        self.root.after(50, self._actualizar_periodicamente)  # 20 FPS
    
    def _actualizar_labels_estado(self):
        """Actualiza los labels con el estado del sistema"""
        estado = self.controlador.obtener_estado_completo()
        
        # Limpiar estela cuando el ciclo termine o no esté en movimiento
        if not self.controlador.ciclo_en_ejecucion or estado['estado_automata'] == 'REPOSO':
            if len(self.estela_posiciones) > 0:
                self._limpiar_estela()
        
        # Mapeo de valores
        mapeo = {
            'sistema_encendido': "🟢 ENCENDIDO" if estado['sistema_encendido'] else "🔴 APAGADO",
            'modo_operacion': estado['modo_operacion'],
            'parada_emergencia': "🚨 ACTIVA" if estado['parada_emergencia'] else "✅ Normal",
            'estado_automata': estado['estado_automata'],
            'ciclo_en_ejecucion': "🔄 EN CURSO" if estado['ciclo_en_ejecucion'] else "⏸ Detenido",
            'ciclos_completados': str(estado['ciclos_completados']),
            'posicion_x': f"{estado['grua']['posicion_x']:.1f}",
            'posicion_y': f"{estado['grua']['posicion_y']:.1f}",
            'tiene_pieza': "✅ SÍ" if estado['grua']['tiene_pieza'] else "❌ NO",
            'en_movimiento': "🔄 SÍ" if estado['grua']['en_movimiento'] else "⏸ NO",
            'estado_proceso': estado['proceso']['estado'],
            'progreso': f"{estado['proceso']['progreso']:.1f}%",
            'tiempo_restante': f"{estado['proceso']['tiempo_restante']:.1f}s",
        }
        
        for campo, label in self.labels_estado.items():
            if campo in mapeo:
                label.config(text=mapeo[campo])
        
        # Actualizar proceso
        self.labels_proceso['corriente'].config(text=f"{estado['proceso']['corriente']:.2f}")
        self.labels_proceso['voltaje'].config(text=f"{estado['proceso']['voltaje']:.2f}")
        self.progressbar_cromado['value'] = estado['proceso']['progreso']
        self.label_progreso.config(text=f"{estado['proceso']['progreso']:.1f}%")
        
        # Estadísticas
        stats = self.controlador.proceso.obtener_estadisticas()
        self.labels_proceso['piezas_procesadas'].config(text=str(stats['piezas_procesadas']))
        self.labels_proceso['piezas_exitosas'].config(text=str(stats['piezas_exitosas']))
        self.labels_proceso['tasa_exito'].config(text=f"{stats['tasa_exito']:.1f}%")
    
    def _actualizar_graficas(self):
        """Actualiza las gráficas de desempeño"""
        
        # Si matplotlib no está disponible, salir
        if not MATPLOTLIB_DISPONIBLE or self.ax_posicion is None:
            return
        
        # Agregar datos actuales
        estado = self.controlador.obtener_estado_completo()
        tiempo_actual = len(self.hist_tiempo) * 0.05  # 50ms por actualización
        
        self.hist_tiempo.append(tiempo_actual)
        self.hist_pos_x.append(estado['grua']['posicion_x'])
        self.hist_pos_y.append(estado['grua']['posicion_y'])
        self.hist_vel_x.append(abs(estado['grua']['velocidad_x']))
        self.hist_vel_y.append(abs(estado['grua']['velocidad_y']))
        
        # Limitar puntos
        if len(self.hist_tiempo) > self.max_puntos_grafica:
            self.hist_tiempo.pop(0)
            self.hist_pos_x.pop(0)
            self.hist_pos_y.pop(0)
            self.hist_vel_x.pop(0)
            self.hist_vel_y.pop(0)
        
        try:
            # Actualizar gráfica de posición
            self.ax_posicion.clear()
            self.ax_posicion.plot(self.hist_tiempo, self.hist_pos_x, 'cyan', label='X', linewidth=2)
            self.ax_posicion.plot(self.hist_tiempo, self.hist_pos_y, 'yellow', label='Y', linewidth=2)
            self.ax_posicion.set_title('Posición de la Grúa (PI-001)', color='white')
            self.ax_posicion.set_xlabel('Tiempo (s)', color='white')
            self.ax_posicion.set_ylabel('Posición', color='white')
            self.ax_posicion.legend()
            self.ax_posicion.tick_params(colors='white')
            self.ax_posicion.set_facecolor('#1a1a1a')
            self.ax_posicion.grid(True, alpha=0.2)
            
            # Actualizar gráfica de velocidad
            self.ax_velocidad.clear()
            self.ax_velocidad.plot(self.hist_tiempo, self.hist_vel_x, 'lime', label='Vx', linewidth=2)
            self.ax_velocidad.plot(self.hist_tiempo, self.hist_vel_y, 'orange', label='Vy', linewidth=2)
            self.ax_velocidad.set_title('Velocidad (SC-001)', color='white')
            self.ax_velocidad.set_xlabel('Tiempo (s)', color='white')
            self.ax_velocidad.set_ylabel('Velocidad', color='white')
            self.ax_velocidad.legend()
            self.ax_velocidad.tick_params(colors='white')
            self.ax_velocidad.set_facecolor('#1a1a1a')
            self.ax_velocidad.grid(True, alpha=0.2)
            
            # Redibujar
            self.canvas_graficas.draw()
        except Exception as e:
            pass  # Ignorar errores de matplotlib
    
    # ==================== EJECUCIÓN ====================
    
    def ejecutar(self):
        """Inicia el bucle principal de la interfaz"""
        self.root.mainloop()
