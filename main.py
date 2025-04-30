import pygame
import sys
from simulation.engine import Engine
from simulation.config import Config

def main():
    """
    Hauptfunktion, die die Simulation initialisiert und startet
    """
    # Konfiguration laden
    config = Config()
    
    # Engine initialisieren
    engine = Engine(config)
    
    # Main-Loop starten
    engine.run()

if __name__ == "__main__":
    main() 