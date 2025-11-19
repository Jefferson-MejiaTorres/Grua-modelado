# 📘 Manual de Usuario
## Sistema de Control de Grúa Viga

---

## 🚀 Inicio Rápido

### 1. Ejecutar el Sistema

**Windows:**
```bash
# Doble clic en:
iniciar.bat

# O en terminal:
python main.py
```

**Linux/Mac:**
```bash
chmod +x iniciar.sh
./iniciar.sh
```

---

## 🎮 Guía de Uso

### Pantalla Principal

```
┌─────────────────────────────────────────────────────┐
│  [⚡ ENCENDER]  [MODO]  [TIEMPO: 120s]  [▶ MARCHA] │
├─────────────────────────────────────────────────────┤
│                                                     │
│        🏗️ VISUALIZACIÓN DE LA GRÚA                │
│                                                     │
│   Estación      Estación        Estación           │
│    CARGA       CROMADO         DESCARGA            │
│                                                     │
├─────────────────────────────────────────────────────┤
│  [Estado] [Proceso] [Logs]                         │
│                                                     │
│  📊 Gráficas en Tiempo Real                        │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Modo de Operación

### ✅ Modo AUTOMÁTICO (Recomendado)

1. **Encender Sistema**
   - Clic en "⚡ ENCENDER SISTEMA"
   - El botón se volverá rojo: "🔴 APAGAR SISTEMA"

2. **Seleccionar Modo**
   - Verificar que está seleccionado "AUTOMÁTICO"

3. **Configurar Tiempo de Cromado**
   - Usar el spinner para ajustar (30-600 segundos)
   - Default: 120 segundos

4. **Iniciar Ciclo**
   - Clic en "▶ MARCHA"
   - El sistema ejecutará automáticamente:
     ```
     HOME → CARGA → ASCENSO → CROMADO (120s) → 
     DESCARGA → RETORNO HOME
     ```

5. **Monitorear**
   - Ver animación en tiempo real
   - Observar progreso en pestaña "Proceso"
   - Consultar logs en pestaña "Logs"

### 🎛️ Modo MANUAL

1. **Cambiar a Manual**
   - Seleccionar radiobutton "MANUAL"

2. **Control Manual** (próxima versión)
   - Usar controles de movimiento
   - Controlar gancho manualmente

---

## 📊 Pestañas de Información

### 📈 Pestaña: Estado del Sistema

Muestra información en tiempo real:

```
Sistema:
  ✅ Sistema encendido: 🟢 ENCENDIDO
  ✅ Modo operación: AUTOMATICO
  ✅ Parada emergencia: ✅ Normal

Ciclo:
  ✅ Estado actual: PROCESO_CROMADO
  ✅ Ciclo en ejecución: 🔄 EN CURSO
  ✅ Ciclos completados: 5

Grúa (PI-001):
  ✅ Posición X: 500.0
  ✅ Posición Y: 200.0
  ✅ Tiene pieza: ✅ SÍ
  ✅ En movimiento: ⏸ NO

Proceso (PC-001):
  ✅ Estado: EN_PROCESO
  ✅ Progreso: 45.5%
  ✅ Tiempo restante: 65.4s
```

### ⚗️ Pestaña: Proceso de Cromado

Muestra parámetros del proceso:

```
Parámetros Eléctricos (ISA 5.1):
  Corriente (A): 2.50
  Voltaje (V): 12.00

Progreso del Cromado:
  [████████████░░░░░░░░] 60%

Estadísticas de Producción:
  Piezas procesadas: 10
  Piezas exitosas: 9
  Tasa de éxito: 90.0%
```

### 📝 Pestaña: Logs del Sistema

Registro en tiempo real de eventos:

```
[14:30:15] [INFO] Sistema encendido
[14:30:20] [INFO] Ciclo iniciado
[14:30:22] [INFO] Transición: REPOSO → CARGA
[14:30:25] [INFO] Pieza cargada
[14:31:45] [INFO] Proceso cromado completado
[14:32:10] [INFO] Ciclo completado en 110.5s
```

---

## 🎯 Ciclo Automático Completo

### Secuencia de Estados

```
1. 🏠 REPOSO (Inicio)
   └─► Usuario presiona MARCHA

2. 📦 CARGA
   └─► Sistema cierra gancho y carga pieza

3. ⬆️ ASCENSO_INICIAL
   └─► Grúa sube al tope superior

4. ➡️ DESPLAZAMIENTO_CENTRO
   └─► Movimiento horizontal a estación de cromado

5. ⬇️ DESCENSO_CROMADO
   └─► Baja a estación de cromado

6. ⚗️ PROCESO_CROMADO
   └─► Inmersión durante tiempo configurado
   └─► Barra de progreso activa
   └─► Monitoreo de parámetros eléctricos

7. ⬆️ ASCENSO_POST_CROMADO
   └─► Eleva pieza cromada

8. ➡️ DESPLAZAMIENTO_DESCARGA
   └─► Movimiento a estación de descarga

9. ⬇️ DESCENSO_DESCARGA
   └─► Baja a estación de descarga

10. 📤 LIBERACION_PIEZA
    └─► Abre gancho y deposita pieza

11. ⬅️ RETORNO_HOME
    └─► Regresa a posición inicial

12. 🏠 REPOSO (Completado)
    └─► Ciclo finalizado
    └─► Contador incrementado
    └─► Listo para siguiente ciclo
```

**Duración típica:** ~150-180 segundos (dependiendo de tiempo de cromado)

---

## 🚨 Parada de Emergencia

### ¿Cuándo usar?

- ⚠️ Movimiento anormal detectado
- ⚠️ Necesidad de intervención manual
- ⚠️ Cualquier situación de riesgo

### Cómo activar:

1. **Clic en botón rojo "🛑 PARADA EMERGENCIA"**
2. **Confirmar en el diálogo**
3. **Resultado:**
   - ⏸ Todo movimiento se detiene INMEDIATAMENTE
   - ❌ Proceso de cromado se aborta
   - 🔒 Sistema entra en estado EMERGENCIA
   - 📝 Evento registrado en logs

### Recuperación:

1. **Verificar que es seguro continuar**
2. **Clic en "🔄 RESET"**
3. **Sistema vuelve a REPOSO**
4. **Listo para operar nuevamente**

---

## 📈 Gráficas en Tiempo Real

### Gráfica 1: Posición de la Grúa (PI-001)

- **Línea Cyan**: Posición X (horizontal)
- **Línea Amarilla**: Posición Y (vertical)
- **Tiempo**: Últimos 5 segundos

### Gráfica 2: Velocidad (SC-001)

- **Línea Verde**: Velocidad horizontal (Vx)
- **Línea Naranja**: Velocidad vertical (Vy)
- **Muestra**: Velocidad absoluta

---

## ⚙️ Configuración Avanzada

### Modificar Parámetros

Editar archivo: `config/config.py`

```python
# Velocidades de movimiento
VELOCIDADES = {
    'horizontal_rapido': 150,  # Más rápido = mayor número
    'vertical_rapido': 100,
}

# Tiempo de cromado
PROCESO_CROMADO = {
    'tiempo_default': 120,  # Segundos
    'tiempo_min': 30,
    'tiempo_max': 600,
}

# Posiciones de estaciones
POSICIONES = {
    'HOME': (100, 500),     # (X, Y)
    'CROMADO': (500, 200),
    'DESCARGA': (900, 500),
}
```

**⚠️ Reiniciar sistema después de cambios**

---

## 🗄️ Base de Datos

### Ubicación

```
data/grua_sistema.db
```

### Consultar con SQLite

```bash
sqlite3 data/grua_sistema.db

# Ver ciclos completados
SELECT * FROM ciclos_cromado ORDER BY timestamp_inicio DESC LIMIT 10;

# Ver estadísticas
SELECT 
    COUNT(*) as total,
    AVG(tiempo_cromado_real) as tiempo_promedio
FROM ciclos_cromado;

# Ver logs
SELECT * FROM logs_sistema WHERE nivel = 'ERROR';
```

---

## 🐛 Solución de Problemas

### Problema: Sistema no inicia

**Solución:**
```bash
# Verificar Python
python --version

# Reinstalar dependencias
pip install -r requirements.txt

# Verificar permisos
# Windows: Ejecutar como Administrador
# Linux: chmod +x iniciar.sh
```

### Problema: Error "tkinter not found"

**Solución:**
```bash
# Windows
pip install tk

# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk
```

### Problema: Gráficas no se ven

**Solución:**
```bash
pip install --upgrade matplotlib
```

### Problema: Sistema se congela

**Posibles causas:**
1. Ciclo automático en ejecución
2. Proceso de cromado activo
3. Error en threading

**Solución:**
1. Presionar "⏸ PARO"
2. Si no responde: "🛑 PARADA EMERGENCIA"
3. Último recurso: Cerrar ventana y reiniciar

---

## 📊 Indicadores de Estado

### Colores según ISA 5.1

| Color | Significado |
|-------|-------------|
| 🟢 Verde | Operación normal |
| 🔴 Rojo | Alarma / Parada |
| 🟡 Amarillo | Advertencia |
| ⚪ Gris | Inactivo |
| 🔵 Cian | En proceso |
| 🟠 Naranja | Modo manual |

### Instrumentos ISA

| Código | Nombre | Función |
|--------|--------|---------|
| PI-001 | Position Indicator | Posición grúa |
| SC-001 | Speed Controller | Control velocidad |
| TI-001 | Time Indicator | Tiempo cromado |
| PC-001 | Process Controller | Control proceso |
| PS-002 | Position Switch | Sensor cromado |
| PS-003 | Position Switch | Sensor descarga |

---

## 📝 Registro de Eventos

### Tipos de Eventos

| Tipo | Color | Descripción |
|------|-------|-------------|
| INFO | 🟢 Verde | Operaciones normales |
| WARNING | 🟡 Amarillo | Advertencias |
| ERROR | 🔴 Rojo | Errores críticos |

### Eventos Comunes

```
[INFO] Sistema encendido
[INFO] Ciclo iniciado
[INFO] Transición: ESTADO_A → ESTADO_B
[INFO] Proceso cromado completado
[INFO] Ciclo completado en X.Xs

[WARNING] Temperatura fuera de rango
[WARNING] pH anormal

[ERROR] Parada de emergencia activada
[ERROR] Fallo en movimiento
```

---

## 🎓 Tips para Demostración

### Para Profesor/Evaluador:

1. **Demostración Básica:**
   - Encender sistema
   - Configurar tiempo a 60s (para demo rápida)
   - Iniciar ciclo automático
   - Mostrar gráficas en tiempo real

2. **Demostración Avanzada:**
   - Activar parada de emergencia en medio del ciclo
   - Mostrar que sistema responde inmediatamente
   - Hacer reset y completar ciclo

3. **Mostrar Base de Datos:**
   - Abrir SQLite
   - Consultar tabla ciclos_cromado
   - Mostrar logs_sistema

4. **Explicar Código:**
   - Abrir `models/automata.py`
   - Mostrar definición formal del autómata
   - Explicar transiciones

---

## 📞 Información Adicional

### Documentación Completa

- `README.md` - Introducción general
- `docs/DOCUMENTACION.md` - Documentación técnica completa
- `docs/RESPUESTAS_PROYECTO.md` - Respuestas al proyecto
- `PROYECTO_COMPLETADO.md` - Resumen ejecutivo

### Archivos Clave

```
main.py                      # Punto de entrada
config/config.py             # Configuración
models/automata.py           # Autómata finito
controllers/controlador_plc.py  # Lógica de control
views/interfaz_hmi.py        # Interfaz gráfica
```

---

## ✅ Checklist de Operación

Antes de cada demostración:

- [ ] Sistema encendido correctamente
- [ ] Base de datos creada (data/)
- [ ] Modo AUTOMÁTICO seleccionado
- [ ] Tiempo de cromado configurado
- [ ] Ventana completamente visible
- [ ] Pestañas accesibles
- [ ] Gráficas funcionando

---

## 🎯 Resultado Esperado

Al completar un ciclo exitoso:

```
✅ Pieza cargada
✅ Movimiento a cromado completado
✅ Proceso de cromado: 100%
✅ Pieza descargada
✅ Grúa retornada a HOME
✅ Contador incrementado
✅ Registro en base de datos
```

**Tiempo típico:** 150-180 segundos

**Tasa de éxito esperada:** >95%

---

## 🚀 ¡Listo para Usar!

El sistema está **completamente funcional** y listo para:
- ✅ Demostración en clase
- ✅ Presentación del proyecto
- ✅ Análisis académico
- ✅ Evaluación del profesor

**¡Buena suerte con tu proyecto!** 🎓

---

**Universidad de Pamplona**  
*Modelado y Simulación de Sistemas*  
*Noviembre 2025*
