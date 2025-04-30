import pygame
from simulation.constants import *

class CelestialBody:
    """
    Klasse für einen Himmelskörper (Planeten, Monde, Sonne)
    """
    def __init__(self, name, mass, radius, position, velocity, color):
        self.name = name
        self.mass = mass  # kg
        self.radius = radius  # m
        self.position = pygame.math.Vector2(position)  # m
        self.velocity = pygame.math.Vector2(velocity)  # m/s
        self.color = color
        self.satellites = []  # Liste der Satelliten/Monde dieses Körpers
    
    def add_satellite(self, satellite):
        """
        Fügt einen Satelliten/Mond zu diesem Himmelskörper hinzu
        
        Args:
            satellite: Der hinzuzufügende Satellit
        """
        self.satellites.append(satellite)


class CelestialBodyManager:
    """
    Manager für die Verwaltung aller Himmelskörper im Sonnensystem
    """
    def __init__(self, config):
        self.config = config
        self.bodies = []
    
    def add_body(self, body):
        """
        Fügt einen Himmelskörper zur Simulation hinzu
        
        Args:
            body: Der hinzuzufügende Himmelskörper
        """
        self.bodies.append(body)
        return body
    
    def get_body_by_name(self, name):
        """
        Gibt einen Himmelskörper anhand seines Namens zurück
        
        Args:
            name: Name des gesuchten Himmelskörpers
            
        Returns:
            Der gefundene Himmelskörper oder None
        """
        for body in self.bodies:
            if body.name == name:
                return body
        return None
    
    def create_solar_system(self):
        """
        Erstellt das vollständige Sonnensystem mit allen Planeten und Monden
        """
        # Sonne (im Zentrum)
        sun = self.add_body(CelestialBody(
            name="Sun",
            mass=SUN_MASS,
            radius=SUN_RADIUS,
            position=(0, 0),
            velocity=(0, 0),
            color=self.config.colors['sun']
        ))
        
        # Merkur
        mercury = self.add_body(CelestialBody(
            name="Mercury",
            mass=MERCURY_MASS,
            radius=MERCURY_RADIUS,
            position=(MERCURY_ORBIT, 0),
            velocity=(0, MERCURY_VELOCITY),
            color=(180, 180, 180)
        ))
        
        # Venus
        venus = self.add_body(CelestialBody(
            name="Venus",
            mass=VENUS_MASS,
            radius=VENUS_RADIUS,
            position=(VENUS_ORBIT, 0),
            velocity=(0, VENUS_VELOCITY),
            color=(255, 198, 73)
        ))
        
        # Erde
        earth = self.add_body(CelestialBody(
            name="Earth",
            mass=EARTH_MASS,
            radius=EARTH_RADIUS,
            position=(EARTH_ORBIT, 0),
            velocity=(0, EARTH_VELOCITY),
            color=self.config.colors['earth']
        ))
        
        # Mond (um die Erde)
        moon = self.add_body(CelestialBody(
            name="Moon",
            mass=MOON_MASS,
            radius=MOON_RADIUS,
            position=(EARTH_ORBIT + MOON_ORBIT, 0),
            velocity=(0, EARTH_VELOCITY + MOON_VELOCITY),
            color=self.config.colors['moon']
        ))
        earth.add_satellite(moon)
        
        # Mars
        mars = self.add_body(CelestialBody(
            name="Mars",
            mass=MARS_MASS,
            radius=MARS_RADIUS,
            position=(MARS_ORBIT, 0),
            velocity=(0, MARS_VELOCITY),
            color=self.config.colors['mars']
        ))
        
        # Jupiter
        jupiter = self.add_body(CelestialBody(
            name="Jupiter",
            mass=JUPITER_MASS,
            radius=JUPITER_RADIUS,
            position=(JUPITER_ORBIT, 0),
            velocity=(0, JUPITER_VELOCITY),
            color=(255, 223, 191)
        ))
        
        # Saturn
        saturn = self.add_body(CelestialBody(
            name="Saturn",
            mass=SATURN_MASS,
            radius=SATURN_RADIUS,
            position=(SATURN_ORBIT, 0),
            velocity=(0, SATURN_VELOCITY),
            color=(240, 200, 150)
        ))
        
        # Uranus
        uranus = self.add_body(CelestialBody(
            name="Uranus",
            mass=URANUS_MASS,
            radius=URANUS_RADIUS,
            position=(URANUS_ORBIT, 0),
            velocity=(0, URANUS_VELOCITY),
            color=(200, 223, 255)
        ))
        
        # Neptun
        neptune = self.add_body(CelestialBody(
            name="Neptune",
            mass=NEPTUNE_MASS,
            radius=NEPTUNE_RADIUS,
            position=(NEPTUNE_ORBIT, 0),
            velocity=(0, NEPTUNE_VELOCITY),
            color=(100, 150, 255)
        ))
        
        # Füge die wichtigsten Monde der äußeren Planeten hinzu
        # (vereinfacht dargestellt, in der Realität gibt es viele mehr)
        
        # Jupiter-Monde (Galileische Monde)
        # Io
        io = self.add_body(CelestialBody(
            name="Io",
            mass=8.93e22,
            radius=1821.6e3,
            position=(JUPITER_ORBIT + 421.7e6, 0),
            velocity=(0, JUPITER_VELOCITY + 17.334e3),
            color=(255, 255, 150)
        ))
        jupiter.add_satellite(io)
        
        # Europa
        europa = self.add_body(CelestialBody(
            name="Europa",
            mass=4.8e22,
            radius=1560.8e3,
            position=(JUPITER_ORBIT + 670.9e6, 0),
            velocity=(0, JUPITER_VELOCITY + 13.740e3),
            color=(200, 200, 200)
        ))
        jupiter.add_satellite(europa)
        
        # Saturn-Mond
        # Titan
        titan = self.add_body(CelestialBody(
            name="Titan",
            mass=1.3452e23,
            radius=2574.73e3,
            position=(SATURN_ORBIT + 1221.87e6, 0),
            velocity=(0, SATURN_VELOCITY + 5.57e3),
            color=(255, 200, 100)
        ))
        saturn.add_satellite(titan) 