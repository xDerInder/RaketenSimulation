import pygame
import sys
import time
import random
import math
from simulation.physics import PhysicsEngine
from simulation.camera import Camera
from simulation.events import EventManager
from simulation.ui import UI
from simulation.celestial_bodies import CelestialBodyManager
from simulation.rocket import Rocket
from simulation.autopilot import AutoPilot

class Engine:
    """
    Hauptsimulationsengine, die die Simulation verwaltet und ausführt
    """
    def __init__(self, config):
        self.config = config
        self.running = False
        self.paused = False
        
        # Pygame initialisieren
        pygame.init()
        pygame.display.set_caption(self.config.title)
        
        # Display-Oberfläche erstellen
        self.screen = pygame.display.set_mode((self.config.width, self.config.height))
        self.clock = pygame.time.Clock()
        
        # Subsysteme initialisieren
        self.physics_engine = PhysicsEngine(self.config)
        self.camera = Camera(self.config)
        self.event_manager = EventManager(self.config)
        self.ui = UI(self.config)
        
        # Himmelskörper initialisieren
        self.celestial_bodies = CelestialBodyManager(self.config)
        self.celestial_bodies.create_solar_system()
        
        # Rakete initialisieren
        self.rocket = Rocket(self.config)
        
        # Autopilot initialisieren
        self.autopilot = AutoPilot(self.config)
        
        # Die Rakete auf der Erdoberfläche platzieren
        earth = self.celestial_bodies.get_body_by_name("Earth")
        
        # Zielplanet festlegen (standardmäßig der Mond, kann aber jeder Planet sein)
        target_planet = self.celestial_bodies.get_body_by_name("Moon")
        
        if earth and target_planet:
            # Startposition auf der Erdoberfläche berechnen
            # Wir platzieren die Rakete auf der Seite der Erde, die dem Zielplaneten zugewandt ist
            
            # Richtungsvektor von Erde zum Zielplaneten
            to_target_x = target_planet.position.x - earth.position.x
            to_target_y = target_planet.position.y - earth.position.y
            
            # --- Entferne den alten Codeblock, der die Rakete auf halbem Weg platzierte ---
            # # Position der Rakete auf halbem Weg zwischen Erde und Mond (alt, nur für Testzwecke)
            # if earth and target_planet:
            #     mid_x = (earth.position.x + target_planet.position.x) / 2
            #     mid_y = (earth.position.y + target_planet.position.y) / 2
            #     self.rocket.position = pygame.math.Vector2(mid_x, mid_y)
            #     print(f"Rakete auf halbem Weg zwischen Erde und Mond platziert, bereit zum Start.")
            #     # Keine Anfangsgeschwindigkeit hier setzen, der Autopilot soll übernehmen            # Normalisieren
            distance_to_target = math.sqrt(to_target_x**2 + to_target_y**2)
            to_target_x /= distance_to_target
            to_target_y /= distance_to_target
            
            # Startposition: 10% über der Erdoberfläche in Richtung Zielplanet
            earth_radius_factor = 1.1  # 10% über der Erdoberfläche
            
            # Position der Rakete berechnen
            self.rocket.position.x = earth.position.x + to_target_x * earth.radius * earth_radius_factor
            self.rocket.position.y = earth.position.y + to_target_y * earth.radius * earth_radius_factor
            
            # Anfangsgeschwindigkeit: Erdgeschwindigkeit + moderate Startgeschwindigkeit
            # Die Fluchtgeschwindigkeit der Erde beträgt ca. 11.2 km/s
            # Wir geben der Rakete eine Startgeschwindigkeit von 3 km/s
            escape_velocity_factor = 0.3  # 30% der Fluchtgeschwindigkeit
            self.rocket.velocity.x = earth.velocity.x + to_target_x * 11200 * escape_velocity_factor
            self.rocket.velocity.y = earth.velocity.y + to_target_y * 11200 * escape_velocity_factor
            
            # Ausrichtung der Rakete zum Zielplaneten
            angle = math.degrees(math.atan2(to_target_y, to_target_x))
            self.rocket.rotation = angle
            
            print(f"Rakete auf der Erdoberfläche platziert, Ausrichtung zum {target_planet.name}: {angle:.1f}°")
            
            # Ziel für den Autopiloten setzen
            self.autopilot.set_target(target_planet)
            print(f"Autopilot target set to: {target_planet.name}")
            
            # Rakete ist nicht gelandet
            self.rocket.landed = False
            self.rocket.landed_on = None
            print(f"Rakete auf halbem Weg zwischen Erde und Mond platziert, bereit zum Start.")
        else:
            print("Erde nicht gefunden! Verwende Standardposition.")
        
        # Kamera erstellen
        self.camera = Camera(self.config)
        
        # Physik-Engine erstellen
        self.physics_engine = PhysicsEngine(self.config)
        
        # Autopilot aktivieren und auf Zielplaneten setzen
        self.autopilot.enable()
        
        # Zielplanet setzen (standardmäßig der Mond, kann aber jeder Planet sein)
        if target_planet:
            # Orbithöhe auf 1.5 * Radius des Zielplaneten setzen für einen stabilen Orbit
            self.autopilot.set_target(target_planet, target_planet.radius * 1.5)
            print(f"Autopilot: {target_planet.name} als Ziel gesetzt")
        
        # Simulationsgeschwindigkeit massiv erhöhen für sehr schnelle Reisen
        self.config.sim_speed = 200.0  # Erhöht von 50.0 auf 200.0 für extrem schnelle Simulation
    
    def process_input(self):
        """
        Verarbeitet Benutzereingaben
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_w and not self.autopilot.enabled:
                    self.rocket.thrust_forward = True
                elif event.key == pygame.K_s and not self.autopilot.enabled:
                    self.rocket.thrust_backward = True
                elif event.key == pygame.K_a and not self.autopilot.enabled:
                    self.rocket.rotate_counterclockwise = True
                elif event.key == pygame.K_d and not self.autopilot.enabled:
                    self.rocket.rotate_clockwise = True
                elif event.key == pygame.K_q:
                    self.camera.zoom_in()
                elif event.key == pygame.K_e:
                    self.camera.zoom_out()
                elif event.key == pygame.K_c:
                    self.config.camera_follow = not self.config.camera_follow
                elif event.key == pygame.K_p:
                    # Autopilot umschalten mit der P-Taste
                    self.autopilot.toggle()
                elif event.key == pygame.K_r:
                    # Zufälliges Ziel für den Autopiloten wählen
                    if self.autopilot.enabled:
                        self.autopilot.choose_random_destination(self.celestial_bodies.bodies)
                elif event.key == pygame.K_1:
                    # Setze Venus als Ziel
                    venus = self.celestial_bodies.get_body_by_name("Venus")
                    if venus and self.autopilot.enabled:
                        self.autopilot.set_target(venus, venus.radius * 2)
                elif event.key == pygame.K_2:
                    # Setze Erde als Ziel
                    earth = self.celestial_bodies.get_body_by_name("Earth")
                    if earth and self.autopilot.enabled:
                        self.autopilot.set_target(earth, 300_000)
                elif event.key == pygame.K_3:
                    # Setze Mars als Ziel
                    mars = self.celestial_bodies.get_body_by_name("Mars")
                    if mars and self.autopilot.enabled:
                        self.autopilot.set_target(mars, mars.radius * 2)
                elif event.key == pygame.K_4:
                    # Setze Jupiter als Ziel
                    jupiter = self.celestial_bodies.get_body_by_name("Jupiter")
                    if jupiter and self.autopilot.enabled:
                        self.autopilot.set_target(jupiter, jupiter.radius * 3)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.rocket.thrust_forward = False
                elif event.key == pygame.K_s:
                    self.rocket.thrust_backward = False
                elif event.key == pygame.K_a:
                    self.rocket.rotate_counterclockwise = False
                elif event.key == pygame.K_d:
                    self.rocket.rotate_clockwise = False
    
    def update(self, dt):
        """
        Aktualisiert den Simulationszustand
        
        Args:
            dt: Delta Zeit in Sekunden seit dem letzten Update
        """
        if self.paused:
            return
            
        # Physik-Update mit mehreren Zeitschritten für genauere Berechnung
        physics_dt = self.config.time_step
        accumulated_time = dt * self.config.sim_speed
        
        # Stelle sicher, dass mindestens ein Physik-Update durchgeführt wird,
        # selbst wenn accumulated_time < physics_dt
        steps_done = 0
        
        while accumulated_time >= physics_dt or steps_done == 0:
            # Autopilot aktualisieren
            if self.autopilot.enabled and not self.rocket.destroyed and not self.rocket.landed:
                self.autopilot.update(
                    physics_dt,
                    self.rocket,
                    self.celestial_bodies.bodies
                )
            
            # Rakete aktualisieren
            self.rocket.update(physics_dt)
            
            # Physik-Engine aktualisieren
            self.physics_engine.update(
                physics_dt, 
                self.celestial_bodies.bodies, 
                self.rocket
            )
            
            # Event-Manager aktualisieren
            active_events = self.event_manager.update(
                physics_dt, 
                self.celestial_bodies.bodies, 
                self.rocket
            )
            
            # Prüfe, ob der Autopilot auf Ereignisse reagieren muss
            if self.autopilot.enabled and active_events:
                for event in active_events:
                    if hasattr(event, 'warning_message') and 'Meteoritenschauer' in event.warning_message:
                        # self.autopilot.handle_event("meteor_shower") # Auskommentiert, da Methode nicht existiert
                        pass # Platzhalter, falls später eine Reaktion implementiert wird
            
            accumulated_time -= physics_dt
            steps_done += 1
            
            # Vermeide Endlosschleife, falls dt sehr klein ist
            if steps_done > 10:
                break
        
        # Kamera aktualisieren
        if self.config.camera_follow:
            self.camera.follow(self.rocket.position)
        
        # UI-Daten aktualisieren
        self.ui.update(self.rocket, self.celestial_bodies.bodies, self.physics_engine, self.autopilot)
    
    def render(self):
        """
        Rendert die Simulation auf dem Bildschirm
        """
        # Bildschirm löschen
        self.screen.fill(self.config.colors['background'])
        
        # Sterne im Hintergrund zeichnen (reduzierte Anzahl)
        for _ in range(30):  # Reduziert von 100 auf 30
            x = random.randint(0, self.config.width)
            y = random.randint(0, self.config.height)
            pygame.draw.circle(self.screen, self.config.colors['stars'], (x, y), 1)
        
        # Himmelskörper zeichnen
        for body in self.celestial_bodies.bodies:
            screen_pos = self.camera.world_to_screen(body.position)
            
            # Skaliere den Radius basierend auf Kamerazoom
            screen_radius = max(5, body.radius / self.config.scale * self.camera.zoom)  # Minimum 5 statt 3
            
            # Zeichne den Himmelskörper nur, wenn er sichtbar ist
            if (screen_pos[0] + screen_radius > 0 and 
                screen_pos[0] - screen_radius < self.config.width and
                screen_pos[1] + screen_radius > 0 and
                screen_pos[1] - screen_radius < self.config.height):
                pygame.draw.circle(self.screen, body.color, screen_pos, screen_radius)
                
                # Name des Himmelskörpers zeichnen
                font = pygame.font.SysFont('Arial', 14)  # Größer: 12 -> 14
                text = font.render(body.name, True, self.config.colors['ui_text'])
                text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - screen_radius - 10))
                self.screen.blit(text, text_rect)
                
                # Markiere das aktuelle Ziel des Autopiloten
                if self.autopilot.enabled and self.autopilot.target is not None and body.name == self.autopilot.target.name:
                    # Zeichne einen Zielkreis um den Zielkörper
                    target_radius = screen_radius + 8  # Größer: 5 -> 8
                    pygame.draw.circle(self.screen, (0, 255, 0), screen_pos, target_radius, 2)  # Dicker: 1 -> 2
        
        # Rakete zeichnen
        rocket_pos = self.camera.world_to_screen(self.rocket.position)
        
        # Triebwerksfeuer zeichnen, wenn die Rakete Schub gibt
        if self.rocket.thrust_level > 0:  # Geändert von thrust_forward auf thrust_level für jeglichen Schub
            # Berechnung des Endpunkts des Feuerstrahls in Weltkoordinaten
            thrust_length = 60 / self.camera.zoom  # Vergrößert von 40 auf 60
            thrust_end_x = self.rocket.position.x - thrust_length * pygame.math.Vector2(1, 0).rotate(self.rocket.rotation).x
            thrust_end_y = self.rocket.position.y - thrust_length * pygame.math.Vector2(1, 0).rotate(self.rocket.rotation).y
            thrust_end_screen = self.camera.world_to_screen((thrust_end_x, thrust_end_y))
            
            # Zeichne das Feuer dicker und auffälliger
            pygame.draw.line(self.screen, (255, 165, 0), rocket_pos, thrust_end_screen, 8)  # Dicker und helleres Orange
        
        # Rakete als größeres, auffälligeres Dreieck zeichnen
        rocket_size = 20  # Vergrößert von 15 auf 20
        points = [
            (rocket_pos[0] + rocket_size * pygame.math.Vector2(1, 0).rotate(self.rocket.rotation).x,
             rocket_pos[1] + rocket_size * pygame.math.Vector2(1, 0).rotate(self.rocket.rotation).y),
            (rocket_pos[0] + rocket_size * pygame.math.Vector2(-0.5, 0.866).rotate(self.rocket.rotation).x,
             rocket_pos[1] + rocket_size * pygame.math.Vector2(-0.5, 0.866).rotate(self.rocket.rotation).y),
            (rocket_pos[0] + rocket_size * pygame.math.Vector2(-0.5, -0.866).rotate(self.rocket.rotation).x,
             rocket_pos[1] + rocket_size * pygame.math.Vector2(-0.5, -0.866).rotate(self.rocket.rotation).y)
        ]
        
        # Zeichne die Rakete mit Reflexionseffekt
        if self.rocket.destroyed:
            rocket_color = (150, 0, 0)  # Dunkelrot für zerstörte Rakete
        elif self.rocket.landed:
            rocket_color = (0, 200, 0)  # Grün für gelandete Rakete
        else:
            rocket_color = (255, 100, 100)  # Hellrot für normale Rakete
            
        pygame.draw.polygon(self.screen, rocket_color, points)
        
        # Umriss für bessere Sichtbarkeit
        pygame.draw.polygon(self.screen, (255, 255, 255), points, 2)  # Weißer Umriss mit Dicke 2
        
        # Statustext anzeigen
        status_text = ""
        if self.rocket.destroyed:
            status_text = "RAKETE ZERSTÖRT"
        elif self.rocket.landed:
            status_text = f"GELANDET AUF {self.rocket.landed_on.name}"
        
        if status_text:
            font = pygame.font.SysFont('Arial', 24, bold=True)
            text = font.render(status_text, True, (255, 0, 0) if self.rocket.destroyed else (0, 255, 0))
            text_rect = text.get_rect(center=(self.config.width // 2, 50))
            self.screen.blit(text, text_rect)
        
        # Flugbahn zeichnen
        if len(self.physics_engine.trajectory) > 1:
            trajectory_points = [self.camera.world_to_screen(pos) for pos in self.physics_engine.trajectory]
            pygame.draw.lines(self.screen, self.config.colors['trajectory'], False, trajectory_points, 2)  # Dicker: 1 -> 2
        
        # UI zeichnen
        self.ui.render(self.screen)
        
        # Anzeigen des gerenderten Frames
        pygame.display.flip()
    
    def run(self):
        """
        Hauptsimulationsschleife
        """
        self.running = True
        prev_time = time.time()
        
        while self.running:
            # Zeit seit dem letzten Frame berechnen
            current_time = time.time()
            dt = current_time - prev_time
            prev_time = current_time
            
            # Eingabe verarbeiten
            self.process_input()
            
            # Simulation aktualisieren
            self.update(dt)
            
            # Bildschirm rendern
            self.render()
            
            # FPS-Begrenzung
            self.clock.tick(self.config.fps)
        
        # Aufräumen
        pygame.quit()