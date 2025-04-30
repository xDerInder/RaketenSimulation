import pygame
import math

class UI:
    """
    Benutzeroberfläche für die Anzeige von Simulationsinformationen
    """
    def __init__(self, config):
        self.config = config
        
        # Daten, die von der Engine aktualisiert werden
        self.rocket_data = {}
        self.celestial_bodies_data = {}
        self.orbit_data = {}
        
        # UI-Einstellungen
        self.show_telemetry = True
        self.show_orbit_info = True
        self.show_system_status = True
    
    def update(self, rocket, celestial_bodies, physics_engine, autopilot=None):
        """
        Aktualisiert die UI-Daten basierend auf dem Simulationszustand
        
        Args:
            rocket: Raketenobjekt
            celestial_bodies: Liste der Himmelskörper
            physics_engine: Physik-Engine
            autopilot: Autopilot-Objekt (optional)
        """
        # Aktualisiere Raketendaten
        self.rocket_data = {
            "position": (rocket.position.x, rocket.position.y),
            "velocity": (rocket.velocity.x, rocket.velocity.y),
            "speed": rocket.velocity.length(),
            "rotation": rocket.rotation,
            "mass": rocket.mass,
            "fuel": rocket.get_fuel_percentage(),
            "delta_v": rocket.get_delta_v(),
            "thrust_level": rocket.thrust_level,
            "engine_systems": rocket.engine_systems,
            "sensors": rocket.sensors,
            "landed": rocket.landed,
            "landed_on": rocket.landed_on.name if rocket.landed_on else None,
            "destroyed": rocket.destroyed
        }
        
        # Autopilot-Daten speichern, wenn verfügbar
        self.autopilot_data = {}
        if autopilot is not None:
            self.autopilot_data = {
                "enabled": autopilot.enabled,
                "mode": autopilot.mode.name if autopilot.enabled else None,
                "target": autopilot.target.name if autopilot.enabled and autopilot.target else None,
                "target_altitude": autopilot.target_orbit_altitude if autopilot.enabled else None
            }
        
        # Finde den nächsten Himmelskörper zur Rakete
        closest_body = None
        min_distance = float('inf')
        
        for body in celestial_bodies:
            dx = body.position.x - rocket.position.x
            dy = body.position.y - rocket.position.y
            distance = (dx*dx + dy*dy)**0.5 - body.radius  # Abstand zur Oberfläche
            
            if distance < min_distance:
                min_distance = distance
                closest_body = body
        
        # Berechne Orbitalparameter, wenn ein Himmelskörper in der Nähe ist
        if closest_body:
            self.orbit_data = physics_engine.calculate_orbital_parameters(rocket, closest_body)
            self.orbit_data["reference_body"] = closest_body.name
            self.orbit_data["distance"] = min_distance
    
    def render(self, screen):
        """
        Rendert die UI auf dem Bildschirm
        
        Args:
            screen: Pygame-Surface zum Zeichnen
        """
        # Autopilot-Status anzeigen
        if hasattr(self, 'autopilot_data'):
            self._render_autopilot_status(screen)
        
        if self.show_telemetry:
            self._render_telemetry(screen)
            
        if self.show_orbit_info and "reference_body" in self.orbit_data:
            self._render_orbit_info(screen)
            
        if self.show_system_status:
            self._render_system_status(screen)
            
        # Zeige Landung/Zerstörung an
        if self.rocket_data.get("landed"):
            self._render_landing_success(screen)
        elif self.rocket_data.get("destroyed"):
            self._render_destruction(screen)
    
    def _render_telemetry(self, screen):
        """
        Zeigt Telemetriedaten der Rakete an
        
        Args:
            screen: Pygame-Surface zum Zeichnen
        """
        # Erstelle einen halbtransparenten Hintergrund
        ui_surface = pygame.Surface((300, 180), pygame.SRCALPHA)
        ui_surface.fill(self.config.colors['ui_background'])
        
        # Setze die Position in der oberen rechten Ecke
        ui_rect = ui_surface.get_rect(topright=(self.config.width - 10, 10))
        
        # Erstelle die Textanzeigen
        font = pygame.font.SysFont('Arial', 16)
        
        # Geschwindigkeit
        speed_text = font.render(f"Geschwindigkeit: {self.rocket_data.get('speed', 0):.1f} m/s", True, self.config.colors['ui_text'])
        ui_surface.blit(speed_text, (10, 10))
        
        # Position
        pos_x = self.rocket_data.get('position', (0, 0))[0] / 1000  # km
        pos_y = self.rocket_data.get('position', (0, 0))[1] / 1000  # km
        pos_text = font.render(f"Position: ({pos_x:.0f}, {pos_y:.0f}) km", True, self.config.colors['ui_text'])
        ui_surface.blit(pos_text, (10, 30))
        
        # Treibstoff
        fuel_text = font.render(f"Treibstoff: {self.rocket_data.get('fuel', 0):.1f}%", True, self.config.colors['ui_text'])
        ui_surface.blit(fuel_text, (10, 50))
        
        # Delta-V
        delta_v_text = font.render(f"Delta-V: {self.rocket_data.get('delta_v', 0):.0f} m/s", True, self.config.colors['ui_text'])
        ui_surface.blit(delta_v_text, (10, 70))
        
        # Masse
        mass_text = font.render(f"Masse: {self.rocket_data.get('mass', 0)/1000:.1f} Tonnen", True, self.config.colors['ui_text'])
        ui_surface.blit(mass_text, (10, 90))
        
        # Rotation
        rotation_text = font.render(f"Rotation: {self.rocket_data.get('rotation', 0):.1f}°", True, self.config.colors['ui_text'])
        ui_surface.blit(rotation_text, (10, 110))
        
        # Schub
        thrust_percent = self.rocket_data.get('thrust_level', 0) * 100
        thrust_text = font.render(f"Schub: {thrust_percent:.0f}%", True, self.config.colors['ui_text'])
        ui_surface.blit(thrust_text, (10, 130))
        
        # Nächster Körper
        if "reference_body" in self.orbit_data:
            body_text = font.render(f"Nächster Körper: {self.orbit_data['reference_body']}", True, self.config.colors['ui_text'])
            ui_surface.blit(body_text, (10, 150))
        
        # Zeichne die UI auf den Hauptbildschirm
        screen.blit(ui_surface, ui_rect)
    
    def _render_orbit_info(self, screen):
        """
        Zeigt Orbitalinformationen an
        
        Args:
            screen: Pygame-Surface zum Zeichnen
        """
        # Erstelle einen halbtransparenten Hintergrund
        ui_surface = pygame.Surface((300, 150), pygame.SRCALPHA)
        ui_surface.fill(self.config.colors['ui_background'])
        
        # Setze die Position in der unteren rechten Ecke
        ui_rect = ui_surface.get_rect(bottomright=(self.config.width - 10, self.config.height - 10))
        
        # Erstelle die Textanzeigen
        font = pygame.font.SysFont('Arial', 16)
        
        # Orbit-Typ
        type_text = font.render(f"Orbit-Typ: {self.orbit_data.get('type', 'Unbekannt')}", True, self.config.colors['ui_text'])
        ui_surface.blit(type_text, (10, 10))
        
        # Abstand
        dist_text = font.render(f"Abstand: {self.orbit_data.get('distance', 0)/1000:.1f} km", True, self.config.colors['ui_text'])
        ui_surface.blit(dist_text, (10, 30))
        
        # Halbachse
        if 'semimajor_axis' in self.orbit_data and self.orbit_data['semimajor_axis'] != float('inf'):
            sma_text = font.render(f"Große Halbachse: {self.orbit_data['semimajor_axis']/1000:.0f} km", True, self.config.colors['ui_text'])
            ui_surface.blit(sma_text, (10, 50))
        
        # Exzentrizität
        if 'eccentricity' in self.orbit_data:
            ecc_text = font.render(f"Exzentrizität: {self.orbit_data['eccentricity']:.3f}", True, self.config.colors['ui_text'])
            ui_surface.blit(ecc_text, (10, 70))
        
        # Periapsis und Apoapsis
        if 'periapsis' in self.orbit_data and self.orbit_data['periapsis'] is not None:
            peri_text = font.render(f"Periapsis: {self.orbit_data['periapsis']/1000:.0f} km", True, self.config.colors['ui_text'])
            ui_surface.blit(peri_text, (10, 90))
            
        if 'apoapsis' in self.orbit_data and self.orbit_data['apoapsis'] is not None:
            apo_text = font.render(f"Apoapsis: {self.orbit_data['apoapsis']/1000:.0f} km", True, self.config.colors['ui_text'])
            ui_surface.blit(apo_text, (10, 110))
        
        # Umlaufzeit
        if 'period' in self.orbit_data and self.orbit_data['period'] is not None:
            period_hours = self.orbit_data['period'] / 3600  # Sekunden zu Stunden
            period_text = font.render(f"Umlaufzeit: {period_hours:.1f} h", True, self.config.colors['ui_text'])
            ui_surface.blit(period_text, (10, 130))
        
        # Zeichne die UI auf den Hauptbildschirm
        screen.blit(ui_surface, ui_rect)
    
    def _render_system_status(self, screen):
        """
        Zeigt den Status der Raketensysteme an
        
        Args:
            screen: Pygame-Surface zum Zeichnen
        """
        # Anzahl der Systeme
        num_systems = len(self.rocket_data.get('engine_systems', {})) + len(self.rocket_data.get('sensors', {}))
        
        # Erstelle einen halbtransparenten Hintergrund
        ui_surface = pygame.Surface((300, 30 + num_systems * 20), pygame.SRCALPHA)
        ui_surface.fill(self.config.colors['ui_background'])
        
        # Setze die Position in der unteren linken Ecke
        ui_rect = ui_surface.get_rect(bottomleft=(10, self.config.height - 10))
        
        # Erstelle die Textanzeigen
        font = pygame.font.SysFont('Arial', 16)
        
        # Überschrift
        header_text = font.render("Systemstatus:", True, self.config.colors['ui_text'])
        ui_surface.blit(header_text, (10, 10))
        
        # Engine-Systeme
        row = 1
        for system, status in self.rocket_data.get('engine_systems', {}).items():
            color = (50, 255, 50) if status else (255, 50, 50)
            status_text = "OK" if status else "AUSGEFALLEN"
            
            system_text = font.render(f"{system}: {status_text}", True, color)
            ui_surface.blit(system_text, (10, 10 + row * 20))
            row += 1
        
        # Sensoren
        for sensor, status in self.rocket_data.get('sensors', {}).items():
            color = (50, 255, 50) if status else (255, 50, 50)
            status_text = "OK" if status else "AUSGEFALLEN"
            
            sensor_text = font.render(f"{sensor}: {status_text}", True, color)
            ui_surface.blit(sensor_text, (10, 10 + row * 20))
            row += 1
        
        # Zeichne die UI auf den Hauptbildschirm
        screen.blit(ui_surface, ui_rect)
    
    def _render_landing_success(self, screen):
        """
        Zeigt eine Erfolgsmeldung bei erfolgreicher Landung an
        
        Args:
            screen: Pygame-Surface zum Zeichnen
        """
        # Erstelle einen halbtransparenten Hintergrund
        ui_surface = pygame.Surface((400, 100), pygame.SRCALPHA)
        ui_surface.fill((0, 100, 0, 200))  # Grün, halbtransparent
        
        # Setze die Position in der Mitte des Bildschirms
        ui_rect = ui_surface.get_rect(center=(self.config.width // 2, self.config.height // 2))
        
        # Erstelle die Textanzeigen
        font_large = pygame.font.SysFont('Arial', 24)
        font_small = pygame.font.SysFont('Arial', 18)
        
        # Erfolgstext
        success_text = font_large.render("Landung erfolgreich!", True, (255, 255, 255))
        success_rect = success_text.get_rect(centerx=ui_surface.get_width()//2, y=20)
        ui_surface.blit(success_text, success_rect)
        
        # Zielinformation
        if self.rocket_data.get('landed_on'):
            target_text = font_small.render(f"Gelandet auf: {self.rocket_data['landed_on']}", True, (255, 255, 255))
            target_rect = target_text.get_rect(centerx=ui_surface.get_width()//2, y=60)
            ui_surface.blit(target_text, target_rect)
        
        # Zeichne die UI auf den Hauptbildschirm
        screen.blit(ui_surface, ui_rect)
    
    def _render_destruction(self, screen):
        """
        Zeigt eine Fehlermeldung bei Zerstörung der Rakete an
        
        Args:
            screen: Pygame-Surface zum Zeichnen
        """
        # Erstelle einen halbtransparenten Hintergrund
        ui_surface = pygame.Surface((400, 100), pygame.SRCALPHA)
        ui_surface.fill((150, 0, 0, 200))  # Rot, halbtransparent
        
        # Setze die Position in der Mitte des Bildschirms
        ui_rect = ui_surface.get_rect(center=(self.config.width // 2, self.config.height // 2))
        
        # Erstelle die Textanzeigen
        font_large = pygame.font.SysFont('Arial', 24)
        
        # Fehlertext
        error_text = font_large.render("Rakete zerstört!", True, (255, 255, 255))
        error_rect = error_text.get_rect(center=(ui_surface.get_width()//2, ui_surface.get_height()//2))
        ui_surface.blit(error_text, error_rect)
        
        # Zeichne die UI auf den Hauptbildschirm
        screen.blit(ui_surface, ui_rect)
    
    def _render_autopilot_status(self, screen):
        """
        Zeigt den Status des Autopiloten an
        
        Args:
            screen: Pygame-Surface zum Zeichnen
        """
        if not self.autopilot_data:
            return
        
        # Erstelle einen halbtransparenten Hintergrund
        ui_surface = pygame.Surface((300, 100), pygame.SRCALPHA)
        ui_surface.fill(self.config.colors['ui_background'])
        
        # Setze die Position in der oberen linken Ecke
        ui_rect = ui_surface.get_rect(topleft=(10, 10))
        
        # Erstelle die Textanzeigen
        font = pygame.font.SysFont('Arial', 16)
        
        # Autopilot-Status
        status_text = font.render(f"Autopilot: {'AKTIV' if self.autopilot_data.get('enabled', False) else 'INAKTIV'}", True, 
                                 (50, 255, 50) if self.autopilot_data.get('enabled', False) else (255, 50, 50))
        ui_surface.blit(status_text, (10, 10))
        
        # Weitere Informationen nur anzeigen, wenn der Autopilot aktiv ist
        if self.autopilot_data.get('enabled', False):
            # Navigationsmodus
            mode_text = font.render(f"Modus: {self.autopilot_data.get('mode', 'Unbekannt')}", True, self.config.colors['ui_text'])
            ui_surface.blit(mode_text, (10, 30))
            
            # Ziel
            if self.autopilot_data.get('target'):
                target_text = font.render(f"Ziel: {self.autopilot_data.get('target')}", True, self.config.colors['ui_text'])
                ui_surface.blit(target_text, (10, 50))
                
                # Zielhöhe
                altitude = self.autopilot_data.get('target_altitude', 0) / 1000  # In km
                altitude_text = font.render(f"Zielhöhe: {altitude:.0f} km", True, self.config.colors['ui_text'])
                ui_surface.blit(altitude_text, (10, 70))
        else:
            # Hinweis zur Aktivierung
            hint_text = font.render("Drücke P zum Aktivieren", True, self.config.colors['ui_text'])
            ui_surface.blit(hint_text, (10, 30))
        
        # Zeichne die UI auf den Hauptbildschirm
        screen.blit(ui_surface, ui_rect) 