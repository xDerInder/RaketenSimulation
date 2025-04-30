import pygame
import math
from simulation.constants import *

class Rocket:
    """
    Rakete für die Weltraumsimulation mit realistischer Physik
    """
    def __init__(self, config):
        self.config = config
        
        # Position und Bewegung
        self.position = pygame.math.Vector2(0, 0)  # m
        self.velocity = pygame.math.Vector2(0, 0)  # m/s
        self.rotation = 0  # Rotation in Grad
        self.rotation_speed = 0  # Grad/s
        
        # Physikalische Eigenschaften
        self.dry_mass = DEFAULT_ROCKET_MASS - DEFAULT_FUEL_MASS  # Masse ohne Treibstoff (kg)
        self.fuel_mass = DEFAULT_FUEL_MASS  # Treibstoffmasse (kg)
        self.mass = self.dry_mass + self.fuel_mass  # Gesamtmasse (kg)
        self.radius = 3.5  # Physikalischer Radius der Rakete (m)
        
        # Triebwerkseigenschaften
        self.max_thrust = DEFAULT_ENGINE_THRUST  # Maximaler Schub (N)
        self.specific_impulse = DEFAULT_SPECIFIC_IMPULSE  # Spezifischer Impuls (s)
        self.exhaust_velocity = DEFAULT_EXHAUST_VELOCITY  # Austrittsgeschwindigkeit (m/s)
        self.thrust_level = 0.0  # Aktueller Schubpegel (0.0 - 1.0)
        
        # Brennstoffverbrauch (kg/s bei vollem Schub)
        self.max_fuel_consumption = DEFAULT_FUEL_CONSUMPTION
        
        # Steuerungsflaggen
        self.thrust_forward = False
        self.thrust_backward = False
        self.rotate_clockwise = False
        self.rotate_counterclockwise = False
        
        # Zustandsflaggen
        self.landed = False
        self.landed_on = None
        self.destroyed = False
        self.collision_with = None
        
        # Navigationsziele
        self.target_body = None
        self.navigation_mode = "manual"  # 'manual', 'orbit', 'approach', 'land'
        
        # Triebwerkssysteme
        self.engine_systems = {
            "main_engine": True,
            "rcs_thrusters": True,
            "fuel_pump": True,
            "guidance": True
        }
        
        # Sensoren und Navigation
        self.sensors = {
            "radar": True,
            "accelerometer": True,
            "gyroscope": True
        }
    
    def update(self, dt):
        """
        Aktualisiert den Zustand der Rakete
        
        Args:
            dt: Zeitschritt in Sekunden
        """
        # Wenn zerstört, keine Updates durchführen
        if self.destroyed:
            return
            
        # Wenn gelandet, nur Updates durchführen, wenn wir starten wollen
        if self.landed and self.landed_on:
            # Aktualisiere die Position, um auf dem Planetenkörper zu bleiben
            if not self.thrust_forward:
                # Nur synchronisieren, wenn wir nicht starten wollen
                self.position = self.landed_on.position + pygame.math.Vector2(
                    math.cos(math.radians(self.rotation - 180)) * self.landed_on.radius,
                    math.sin(math.radians(self.rotation - 180)) * self.landed_on.radius
                )
                # Geschwindigkeit auf die des Planeten setzen
                self.velocity.x = self.landed_on.velocity.x
                self.velocity.y = self.landed_on.velocity.y
                return
            else:
                # Starten, wenn der Schub aktiviert wird
                if self.thrust_level > 0.2:  # Startsequenz schon bei 20% Schub aktivieren (reduziert von 50%)
                    print(f"Startsequenz von {self.landed_on.name} eingeleitet!")
                    self.landed = False
                    self.landed_on = None
                    # Leichte Anfangsgeschwindigkeit in Raketenrichtung geben
                    angle_rad = math.radians(self.rotation)
                    self.velocity.x += 50.0 * math.cos(angle_rad)  # Erhöht von 10.0 auf 50.0
                    self.velocity.y += 50.0 * math.sin(angle_rad)  # Höhere Anfangsgeschwindigkeit
                else:
                    # Nicht genug Schub zum Starten
                    return
            
        # Steuereingaben verarbeiten
        self._process_controls(dt)
        
        # Aktualisiere Position basierend auf Geschwindigkeit
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
        
        # Aktualisiere Rotation
        self.rotation += self.rotation_speed * dt
        
        # Schubkraft anwenden, wenn das Triebwerk aktiviert ist
        if self.thrust_level > 0 and self.fuel_mass > 0 and self.engine_systems["main_engine"]:
            self._apply_thrust(dt)
        
        # Treibstoff verbrauchen
        if self.thrust_level > 0 and self.fuel_mass > 0:
            fuel_consumed = self.max_fuel_consumption * self.thrust_level * dt
            self.fuel_mass = max(0, self.fuel_mass - fuel_consumed)
            # Aktualisiere die Gesamtmasse
            self.mass = self.dry_mass + self.fuel_mass
    
    def _process_controls(self, dt):
        """
        Verarbeitet die Steuerungseingaben und setzt entsprechende Werte
        
        Args:
            dt: Zeitschritt in Sekunden
        """
        # Schubsteuerung
        if self.thrust_forward:
            self.thrust_level = 1.0
        elif self.thrust_backward:
            self.thrust_level = 0.1  # Rückwärtsschub ist schwächer
        else:
            self.thrust_level = 0.0
        
        # Rotationssteuerung
        max_rotation_speed = 20.0  # Reduziert von 30.0 auf 20.0 Grad/s für stabilere Steuerung
        rotation_acceleration = 40.0  # Reduziert von 60.0 auf 40.0 Grad/s² für stabilere Steuerung
        
        if self.rotate_clockwise and self.engine_systems["rcs_thrusters"]:
            # Beschleunige die Rotationsgeschwindigkeit
            self.rotation_speed = min(max_rotation_speed, self.rotation_speed + rotation_acceleration * dt)
        elif self.rotate_counterclockwise and self.engine_systems["rcs_thrusters"]:
            # Beschleunige die Rotationsgeschwindigkeit in die andere Richtung
            self.rotation_speed = max(-max_rotation_speed, self.rotation_speed - rotation_acceleration * dt)
        else:
            # Starke Dämpfung, wenn keine Taste gedrückt wird (Simuliere RCS-Stabilisierung)
            self.rotation_speed = 0  # Sofort stoppen - war vorher eine sanfte Dämpfung
    
    def _apply_thrust(self, dt):
        """
        Wendet die Schubkraft des Raketentriebwerks an
        
        Args:
            dt: Zeitschritt in Sekunden
        """
        # Berechne den Schubvektor basierend auf der Rotation der Rakete
        # In Pygame zeigt 0 Grad nach rechts, 90 Grad nach unten
        # Wir wollen, dass 0 Grad nach rechts zeigt und Schub in diese Richtung erzeugt wird
        angle_rad = math.radians(self.rotation)
        
        # Berechne die Schubkraft (F = m * ve * (dm/dt) / m)
        thrust_force = self.max_thrust * self.thrust_level
        
        # Berechne die Beschleunigung (a = F/m)
        acceleration = thrust_force / self.mass
        
        # Berechne die Vektorkomponenten der Beschleunigung
        accel_x = acceleration * math.cos(angle_rad)
        accel_y = acceleration * math.sin(angle_rad)
        
        # Aktualisiere die Geschwindigkeit basierend auf der Beschleunigung
        self.velocity.x += accel_x * dt
        self.velocity.y += accel_y * dt
    
    def get_fuel_percentage(self):
        """
        Gibt den Treibstoffprozentsatz zurück
        
        Returns:
            Treibstoffprozentsatz (0-100)
        """
        return (self.fuel_mass / DEFAULT_FUEL_MASS) * 100.0
    
    def get_delta_v(self):
        """
        Berechnet das verbleibende Delta-V der Rakete
        
        Returns:
            Verbleibendes Delta-V in m/s
        """
        # Tsiolkovsky-Raketengleichung: Δv = ve * ln(m0/mf)
        # ve = Austrittsgeschwindigkeit, m0 = Anfangsmasse, mf = Endmasse
        if self.fuel_mass <= 0:
            return 0
        else:
            current_mass = self.dry_mass + self.fuel_mass
            final_mass = self.dry_mass  # Wenn der Treibstoff aufgebraucht ist
            return self.exhaust_velocity * math.log(current_mass / final_mass)
    
    def trigger_system_failure(self, system_name):
        """
        Löst einen Systemausfall aus
        
        Args:
            system_name: Name des betroffenen Systems
        """
        if system_name in self.engine_systems:
            self.engine_systems[system_name] = False
        elif system_name in self.sensors:
            self.sensors[system_name] = False
    
    def repair_system(self, system_name):
        """
        Repariert ein ausgefallenes System
        
        Args:
            system_name: Name des zu reparierenden Systems
        """
        if system_name in self.engine_systems:
            self.engine_systems[system_name] = True
        elif system_name in self.sensors:
            self.sensors[system_name] = True 