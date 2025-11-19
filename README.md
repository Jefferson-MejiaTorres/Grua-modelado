# 🏗️ Sistema de Control de Grúa Viga para Proceso de Cromado

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/Status-Completado-success.svg)
![License](https://img.shields.io/badge/License-Academic-yellow.svg)
![ISA](https://img.shields.io/badge/Standard-ISA_5.1-orange.svg)

**Sistema de simulación de control automatizado de una grúa viga utilizada en proceso de cromado por electrólisis**

[Características](#-características-principales) •
[Instalación](#-instalación) •
[Uso](#-uso-rápido) •
[Documentación](#-documentación) •
[Arquitectura](#-arquitectura)

</div>

---

## 👥 Integrantes del Proyecto

**Universidad de Pamplona - Facultad de Ingenierías**  
**Curso:** Modelado y Simulación de Sistemas  
**Periodo:** II Corte 2025

| Nombre | Rol |
|--------|-----|
| **Jefferson Mejía Torres** | Desarrollador Principal |
| **Luis Miguel Bonett** | Desarrollador |
| **Sebastián Sánchez Barrera** | Desarrollador |

---

## 📋 Descripción del Proyecto

Sistema completo de simulación para el control automatizado de una grúa viga industrial utilizada en procesos de cromado por electrólisis. El proyecto implementa un **autómata finito determinista** con 12 estados, siguiendo la **norma ISA 5.1** para instrumentación industrial.

### 🎯 Objetivos Cumplidos

- ✅ **Modelado formal del autómata** con definición completa (Q, Σ, δ, q₀, F)
- ✅ **Interfaz gráfica profesional (HMI)** con visualización en tiempo real
- ✅ **Arquitectura MVC** robusta y escalable
- ✅ **Base de datos SQLite** para persistencia de datos
- ✅ **Control automático y manual** del proceso
- ✅ **Cumplimiento de norma ISA 5.1** en instrumentación
- ✅ **Sistema de logs y trazabilidad** completo

---

## ✨ Características Principales

### 🖥️ Interfaz Gráfica (HMI)
- 📊 Visualización en tiempo real del movimiento de la grúa
- 🎨 Diseño según norma ISA 5.1 (colores, símbolos, instrumentación)
- 📈 Gráficas de posición y velocidad con matplotlib
- 🎛️ Panel de control intuitivo con botones de operación
- ⚡ Actualización a 20 FPS para animación fluida
- 🔴 Parada de emergencia funcional desde cualquier estado

### 🤖 Autómata de Estados
**12 Estados definidos:**
1. REPOSO - Posición inicial
2. CARGA - Colocación de pieza
3. ASCENSO_INICIAL - Subida desde reposo
4. DESPLAZAMIENTO_CENTRO - Movimiento horizontal hacia cromado
5. DESCENSO_CROMADO - Bajada a estación de cromado
6. PROCESO_CROMADO - Inmersión y electrólisis (30-600s)
7. ASCENSO_POST_CROMADO - Subida después de cromado
8. DESPLAZAMIENTO_DESCARGA - Movimiento hacia descarga
9. DESCENSO_DESCARGA - Bajada a estación de descarga
10. LIBERACION_PIEZA - Depositar pieza cromada
11. RETORNO_HOME - Regreso a posición inicial
12. EMERGENCIA - Estado de parada de emergencia

### 🔧 Control del Proceso
- ⚙️ **Modo Automático**: Ciclo completo automatizado
- 🎮 **Modo Manual**: Control directo de movimientos
- ⏱️ **Temporizador configurable** (30-600 segundos)
- ⚡ **Parámetros eléctricos**: Corriente (2.5A), Voltaje (12V)
- 🌡️ **Monitoreo de temperatura** y pH del baño electrolítico
- 📊 **Estadísticas de producción** en tiempo real

### 💾 Base de Datos SQLite
**3 Tablas principales:**
- `estado_grua`: Histórico de posiciones y velocidades
- `ciclos_cromado`: Registro completo de cada ciclo de producción
- `logs_sistema`: Eventos, alarmas y trazabilidad

### 📡 Instrumentación ISA 5.1
- **PI-001**: Position Indicator (indicador de posición)
- **SC-001**: Speed Controller (controlador de velocidad)
- **TI-001**: Time Indicator (indicador de tiempo)
- **PC-001**: Process Controller (controlador de proceso)
- **PS-002/003**: Position Switches (sensores de posición)

---

## 🏗️ Arquitectura

### Patrón MVC (Modelo-Vista-Controlador)

```
┌─────────────────────────────────────────────────┐
│              VISTA (HMI)                        │
│  • Interfaz gráfica Tkinter                    │
│  • Visualización en tiempo real                │
│  • Gráficas matplotlib                         │
│  • Panel de control ISA 5.1                    │
└────────────────┬────────────────────────────────┘
                 │
                 ↕ Actualización bidireccional
                 │
┌────────────────▼────────────────────────────────┐
│          CONTROLADOR (PLC)                      │
│  • Lógica de control tipo PLC                  │
│  • Coordinación de subsistemas                 │
│  • Gestión de ciclos automáticos               │
│  • Threading para procesos concurrentes        │
└────────────────┬────────────────────────────────┘
                 │
                 ↕ Comandos y consultas
                 │
┌────────────────▼────────────────────────────────┐
│               MODELO                            │
│  • AutomataGrua (estados y transiciones)       │
│  • Grua (física y movimiento)                  │
│  • ProcesoChromado (electrólisis)              │
│  • BaseDatos (persistencia SQLite)             │
└─────────────────────────────────────────────────┘
```

### 📂 Estructura del Proyecto

```
Grua-modelado/
│
├── 📂 config/                    # Configuración del sistema
│   ├── __init__.py
│   └── config.py                 # Parámetros ISA 5.1, velocidades, posiciones
│
├── 📂 models/                    # MODELO (Arquitectura MVC)
│   ├── __init__.py
│   ├── automata.py               # Autómata finito (12 estados, 12 eventos)
│   ├── grua.py                   # Modelo físico de grúa
│   └── proceso_cromado.py        # Proceso de electrólisis
│
├── 📂 controllers/               # CONTROLADOR (Arquitectura MVC)
│   ├── __init__.py
│   └── controlador_plc.py        # Lógica tipo PLC, coordina todo
│
├── 📂 views/                     # VISTA (Arquitectura MVC)
│   ├── __init__.py
│   └── interfaz_hmi.py           # Interfaz gráfica HMI (Tkinter)
│
├── 📂 utils/                     # Utilidades
│   ├── __init__.py
│   └── base_datos.py             # Gestión SQLite (3 tablas)
│
├── 📂 data/                      # Datos persistentes (auto-creado)
│   └── grua_sistema.db           # Base de datos SQLite
│
├── 📂 docs/                      # Documentación técnica completa
│   ├── DOCUMENTACION.md          # Documentación técnica completa
│   └── RESPUESTAS_PROYECTO.md    # Respuestas al proyecto académico
│
├── 🚀 main.py                    # Punto de entrada principal
├── ⚙️ iniciar.bat                # Script de inicio para Windows
├── ⚙️ iniciar.sh                 # Script de inicio para Linux/Mac
├── 📋 requirements.txt           # Dependencias Python
├── 📖 README.md                  # Este archivo
├── 📘 MANUAL_USUARIO.md          # Manual de usuario completo
├── ✅ PROYECTO_COMPLETADO.md     # Resumen ejecutivo
└── 📄 INICIO_RAPIDO.md           # Guía de inicio rápido
```

---

## 🚀 Instalación

### Requisitos Previos
- **Python 3.8 o superior**
- **pip** (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/Jefferson-MejiaTorres/Grua-modelado.git
cd Grua-modelado
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

Las dependencias principales son:
- `matplotlib` - Gráficas en tiempo real
- `numpy` - Cálculos numéricos
- `Pillow` - Procesamiento de imágenes (opcional)

3. **Ejecutar el sistema**

**Opción A - Windows:**
```bash
# Doble clic en:
iniciar.bat

# O desde terminal:
python main.py
```

**Opción B - Linux/Mac:**
```bash
chmod +x iniciar.sh
./iniciar.sh
```

---

## 🎮 Uso Rápido

### Modo Automático (Recomendado)

1. **Encender el Sistema**
   - Clic en botón "⚡ ENCENDER SISTEMA"
   - El botón cambiará a rojo: "🔴 APAGAR SISTEMA"

2. **Verificar Modo**
   - Asegurar que está seleccionado "AUTOMÁTICO"

3. **Configurar Tiempo de Cromado**
   - Ajustar el spinner (30-600 segundos)
   - Valor por defecto: 120 segundos

4. **Iniciar Ciclo**
   - Clic en "▶ MARCHA"
   - El sistema ejecutará automáticamente los 11 estados

5. **Monitorear**
   - Ver animación en tiempo real
   - Consultar pestaña "Estado del Sistema"
   - Revisar logs en pestaña "Logs"

### Interfaz Principal

```
┌─────────────────────────────────────────────────────────┐
│  [⚡ ENCENDER]  [MODO]  [TIEMPO: 120s]  [▶ MARCHA]     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│        🏗️ VISUALIZACIÓN DE LA GRÚA                    │
│                                                         │
│   Estación      Estación        Estación               │
│    CARGA       CROMADO         DESCARGA                │
│      🟢           🔵              🟡                    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  [Estado del Sistema] [Proceso] [Logs]                 │
│                                                         │
│  📊 Gráficas: Posición | Velocidad                     │
└─────────────────────────────────────────────────────────┘
```

### Parada de Emergencia

- **Botón rojo "🔴 EMERGENCIA"** disponible en todo momento
- Detiene inmediatamente todos los movimientos
- Transiciona el autómata al estado EMERGENCIA
- Para reanudar: presionar "🔄 RESET"

---

## 📚 Documentación

### Documentos Disponibles

| Documento | Descripción |
|-----------|-------------|
| 📖 [README.md](README.md) | Este archivo - Visión general |
| 📘 [MANUAL_USUARIO.md](MANUAL_USUARIO.md) | Manual completo de usuario |
| 📄 [INICIO_RAPIDO.md](INICIO_RAPIDO.md) | Guía de inicio rápido |
| 📋 [docs/DOCUMENTACION.md](docs/DOCUMENTACION.md) | Documentación técnica completa |
| 📝 [docs/RESPUESTAS_PROYECTO.md](docs/RESPUESTAS_PROYECTO.md) | Respuestas académicas del proyecto |
| ✅ [PROYECTO_COMPLETADO.md](PROYECTO_COMPLETADO.md) | Resumen ejecutivo |

### Definición Formal del Autómata

**Autómata Finito Determinista (AFD):**

```
A = (Q, Σ, δ, q₀, F)
```

Donde:
- **Q**: Conjunto de 12 estados (EstadoGrua)
- **Σ**: Alfabeto de 12 eventos de entrada (EventoAutomata)
- **δ**: Función de transición δ: Q × Σ → Q
- **q₀**: Estado inicial REPOSO
- **F**: Conjunto de estados finales {REPOSO}

---

## 🔧 Tecnologías Utilizadas

| Tecnología | Uso |
|------------|-----|
| **Python 3.8+** | Lenguaje principal |
| **Tkinter** | Interfaz gráfica (GUI) |
| **Matplotlib** | Gráficas en tiempo real |
| **SQLite3** | Base de datos embebida |
| **Threading** | Concurrencia |
| **Enum** | Definición de estados y eventos |
| **Type Hints** | Anotaciones de tipo |

---

## 🎓 Contexto Académico

**Institución:** Universidad de Pamplona  
**Facultad:** Ingenierías  
**Curso:** Modelado y Simulación de Sistemas  
**Profesor:** [Nombre del Profesor]  
**Periodo:** II Corte 2025

### Competencias Desarrolladas

- ✅ Modelado de sistemas de eventos discretos
- ✅ Implementación de autómatas finitos
- ✅ Arquitecturas de software (MVC)
- ✅ Programación orientada a objetos
- ✅ Interfaces gráficas de usuario
- ✅ Bases de datos relacionales
- ✅ Normas industriales (ISA 5.1)
- ✅ Control de procesos industriales
- ✅ Documentación técnica

---

## 📊 Estadísticas del Proyecto

- **Líneas de código:** ~2,500+
- **Archivos Python:** 12
- **Clases implementadas:** 8
- **Estados del autómata:** 12
- **Eventos definidos:** 12
- **Tablas de BD:** 3
- **Páginas de documentación:** 100+

---

## 🤝 Contribuciones

Este es un proyecto académico. Para sugerencias o mejoras:

1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit de cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

---

## 📄 Licencia

Este proyecto es de carácter **académico** y fue desarrollado como parte del curso de Modelado y Simulación de Sistemas de la Universidad de Pamplona.

**Uso educativo permitido** - No uso comercial sin autorización.

---

## 📞 Contacto

**Integrantes del Equipo:**
- Jefferson Mejía Torres
- Luis Miguel Bonett  
- Sebastián Sánchez Barrera

**Universidad de Pamplona**  
**Facultad de Ingenierías**  
**Colombia** 🇨🇴

---

## 🙏 Agradecimientos

- Universidad de Pamplona - Facultad de Ingenierías
- Profesores del curso de Modelado y Simulación
- Comunidad de Python y bibliotecas open source
- Norma ISA 5.1 para instrumentación industrial

---

<div align="center">

**⭐ Si este proyecto te fue útil, considera darle una estrella ⭐**

Hecho con ❤️ por el equipo de Grúa-modelado

</div>
