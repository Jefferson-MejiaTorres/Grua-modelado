"""
Sistema de Control de Grúa Viga para Proceso de Cromado
Punto de entrada principal de la aplicación

Proyecto: Modelado y Simulación de Sistemas de Eventos Discretos
Universidad de Pamplona
"""

import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.controlador_plc import ControladorPLC
from views.interfaz_hmi import InterfazHMI
from utils.base_datos import BaseDatos


def main():
    """
    Función principal que inicializa y ejecuta el sistema
    """
    
    print("=" * 60)
    print("SISTEMA DE CONTROL DE GRÚA VIGA")
    print("Proceso de Cromado por Electrólisis")
    print("Norma ISA 5.1")
    print("=" * 60)
    print()
    print("Inicializando sistema...")
    
    try:
        # Inicializar base de datos
        print("📊 Conectando a base de datos...")
        db = BaseDatos()
        print("   ✓ Base de datos inicializada")
        
        # Crear controlador PLC
        print("🎮 Inicializando controlador PLC...")
        controlador = ControladorPLC()
        print("   ✓ Controlador inicializado")
        
        # Crear interfaz gráfica HMI
        print("🖥️  Cargando interfaz gráfica HMI...")
        interfaz = InterfazHMI(controlador)
        print("   ✓ Interfaz cargada")
        
        print()
        print("✅ Sistema listo para operar")
        print()
        print("Instrucciones:")
        print("  1. Presione 'ENCENDER SISTEMA'")
        print("  2. Seleccione modo AUTOMÁTICO o MANUAL")
        print("  3. Configure el tiempo de cromado")
        print("  4. Presione 'MARCHA' para iniciar el ciclo")
        print()
        print("=" * 60)
        
        # Ejecutar interfaz (bucle principal)
        interfaz.ejecutar()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Sistema interrumpido por el usuario")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n\n❌ Error fatal en el sistema: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
