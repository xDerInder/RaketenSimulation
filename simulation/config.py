import pygame
from simulation.constants import *

class Config:
    """
    Konfigurationsklasse für die Simulation
    """
    def __init__(self):
        # Fensterkonfiguration
        self.width = 1200
        self.height = 800
        self.fps = 60
        self.title = "Raketensimulation"
        
        # Simulationseinstellungen
        self.sim_speed = 200.0  # Simulationsgeschwindigkeit erhöht auf 200x Echtzeit
        self.time_step = 1.0  # Zeitschritt in Sekunden für die Physikberechnung
        
        # Gravitationskonstante (N * m^2 / kg^2)
        self.G = 6.67430e-11 * 3.0  # Gravitationskonstante um Faktor 3 erhöht für stärkere Anziehungskraft
        
        # Maßstabsfaktor (1 Pixel = X Meter)
        self.scale = 1.0e5  # Auf 100.000 Meter pro Pixel reduziert für deutlich bessere Sichtbarkeit
        
        # Kameraeinstellungen
        self.camera_follow = True  # Kamera folgt der Rakete
        self.camera_zoom = 1.0  # Startzoom
        self.min_zoom = 0.01  # von 0.1 auf 0.01 reduziert für weiteres Auszoomen
        self.max_zoom = 20.0  # von 10.0 auf 20.0 erhöht für stärkeres Heranzoomen
        self.auto_zoom = True  # Automatischer Zoom basierend auf Distanz
        
        # Event-Einstellungen
        self.event_probability = 0.0005  # Reduziert von 0.001 für weniger häufige Events
        self.meteors_enabled = True
        self.system_failures_enabled = True
        
        # Farben
        self.colors = {
            'background': (0, 0, 30),  # Etwas helleres Dunkelblau
            'stars': (255, 255, 255),
            'rocket': (255, 100, 100),  # Hellere Rakete
            'thrust': (255, 165, 0),  # Helleres Orange für Triebwerk
            'earth': (50, 100, 255),  # Helleres Blau für Erde
            'moon': (200, 200, 200),
            'sun': (255, 255, 50),  # Helleres Gelb für Sonne
            'mars': (255, 80, 0),  # Helleres Rot für Mars
            'ui_text': (220, 220, 220),  # Hellerer Text
            'ui_background': (0, 0, 60, 180),  # Hellerer und transparenterer Hintergrund
            'trajectory': (100, 180, 255, 150),  # Hellere Flugbahn
        } 