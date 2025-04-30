import random
import pygame
import math

class Event:
    """
    Basisklasse für Ereignisse in der Simulation
    """
    def __init__(self, duration=5.0):
        self.duration = duration  # Dauer des Ereignisses in Sekunden
        self.elapsed_time = 0  # Vergangene Zeit seit Beginn des Ereignisses
        self.active = True
    
    def update(self, dt, bodies, rocket):
        """
        Aktualisiert den Zustand des Ereignisses
        
        Args:
            dt: Zeitschritt in Sekunden
            bodies: Liste der Himmelskörper
            rocket: Raketenobjekt
            
        Returns:
            True, wenn das Ereignis aktiv ist, False wenn es beendet ist
        """
        self.elapsed_time += dt
        if self.elapsed_time >= self.duration:
            self.active = False
        return self.active
    
    def render(self, screen, camera):
        """
        Rendert visuelle Elemente des Ereignisses
        
        Args:
            screen: Pygame-Surface zum Zeichnen
            camera: Kameraobjekt für Koordinatentransformation
        """
        pass


class MeteorShower(Event):
    """
    Meteoritenschauer, dem die Rakete ausweichen muss
    """
    def __init__(self, duration=15.0, meteor_count=20, danger_zone_radius=5000000):
        super().__init__(duration)
        self.meteor_count = meteor_count
        self.danger_zone_radius = danger_zone_radius  # Radius des Gefahrenbereichs in Metern
        self.meteors = []
        self.warning_time = 5.0  # Sekunden Vorwarnzeit
        self.warning_active = True
        self.warning_message = "WARNUNG: Meteoritenschauer erkannt!"
        self.collision_check_radius = 50000  # Kollisionsradius in Metern
    
    def update(self, dt, bodies, rocket):
        """
        Aktualisiert den Meteoritenschauer
        
        Args:
            dt: Zeitschritt in Sekunden
            bodies: Liste der Himmelskörper
            rocket: Raketenobjekt
            
        Returns:
            True, wenn das Ereignis aktiv ist, False wenn es beendet ist
        """
        # Aktualisiere vergangene Zeit
        self.elapsed_time += dt
        
        # Verwalte die Warnungsphase
        if self.warning_active:
            if self.elapsed_time >= self.warning_time:
                self.warning_active = False
                # Generiere Meteoriten, wenn die Warnzeit abgelaufen ist
                self._generate_meteors(rocket)
        
        # Beende das Ereignis nach der festgelegten Dauer
        if self.elapsed_time >= self.duration:
            self.active = False
            return False
        
        # Wenn keine Warnung mehr aktiv ist, bewege die Meteoriten
        if not self.warning_active:
            self._update_meteors(dt, rocket)
        
        return True
    
    def _generate_meteors(self, rocket):
        """
        Generiert Meteoriten um die Rakete herum
        
        Args:
            rocket: Raketenobjekt
        """
        self.meteors = []
        
        for _ in range(self.meteor_count):
            # Wähle einen zufälligen Startpunkt am Rand des Gefahrenbereichs
            angle = random.uniform(0, 2 * math.pi)
            distance = self.danger_zone_radius
            
            # Berechne Position relativ zur Rakete
            meteor_x = rocket.position.x + distance * math.cos(angle)
            meteor_y = rocket.position.y + distance * math.sin(angle)
            
            # Berechne Geschwindigkeitsvektor zur Rakete mit Zufallsvariation
            speed = random.uniform(1000, 5000)  # m/s
            direction_angle = angle + math.pi + random.uniform(-0.5, 0.5)
            
            velocity_x = speed * math.cos(direction_angle)
            velocity_y = speed * math.sin(direction_angle)
            
            # Größe und Farbe des Meteoriten
            size = random.uniform(10, 50)  # Größe in Metern
            color = (random.randint(150, 255), random.randint(100, 150), random.randint(50, 100))
            
            # Füge den Meteoriten zur Liste hinzu
            self.meteors.append({
                'position': pygame.math.Vector2(meteor_x, meteor_y),
                'velocity': pygame.math.Vector2(velocity_x, velocity_y),
                'size': size,
                'color': color,
                'hit': False
            })
    
    def _update_meteors(self, dt, rocket):
        """
        Aktualisiert die Positionen der Meteoriten und prüft auf Kollisionen
        
        Args:
            dt: Zeitschritt in Sekunden
            rocket: Raketenobjekt
        """
        for meteor in self.meteors:
            if meteor['hit']:
                continue
                
            # Aktualisiere Position
            meteor['position'].x += meteor['velocity'].x * dt
            meteor['position'].y += meteor['velocity'].y * dt
            
            # Prüfe auf Kollision mit der Rakete
            distance_to_rocket = (meteor['position'] - rocket.position).length()
            
            # Kollision, wenn Distanz kleiner als Kollisionsradius
            if distance_to_rocket < self.collision_check_radius:
                meteor['hit'] = True
                # Beschädige die Rakete (zufälliges System)
                systems = list(rocket.engine_systems.keys()) + list(rocket.sensors.keys())
                damaged_system = random.choice(systems)
                rocket.trigger_system_failure(damaged_system)
    
    def render(self, screen, camera, config):
        """
        Rendert den Meteoritenschauer
        
        Args:
            screen: Pygame-Surface zum Zeichnen
            camera: Kameraobjekt für Koordinatentransformation
            config: Konfigurationsobjekt
        """
        # Zeige Warnungstext an
        if self.warning_active:
            font = pygame.font.SysFont('Arial', 24)
            warning_text = font.render(self.warning_message, True, (255, 50, 50))
            warning_rect = warning_text.get_rect(center=(config.width // 2, 50))
            screen.blit(warning_text, warning_rect)
        
        # Zeichne Meteoriten
        for meteor in self.meteors:
            if meteor['hit']:
                continue
                
            # Konvertiere Weltkoordinaten zu Bildschirmkoordinaten
            screen_pos = camera.world_to_screen(meteor['position'])
            
            # Berechne Größe basierend auf Zoom
            screen_size = max(2, meteor['size'] / config.scale * camera.zoom)
            
            # Zeichne den Meteoriten nur, wenn er im sichtbaren Bereich ist
            if (0 <= screen_pos[0] <= config.width and
                0 <= screen_pos[1] <= config.height):
                pygame.draw.circle(screen, meteor['color'], screen_pos, screen_size)
                
                # Füge einen Schweif hinzu (als Linie)
                tail_length = screen_size * 3
                tail_end = (
                    screen_pos[0] - (meteor['velocity'].x / meteor['velocity'].length()) * tail_length,
                    screen_pos[1] - (meteor['velocity'].y / meteor['velocity'].length()) * tail_length
                )
                pygame.draw.line(screen, meteor['color'], screen_pos, tail_end, max(1, int(screen_size // 3)))


class SystemFailure(Event):
    """
    Ereignis für zufällige Systemausfälle an der Rakete
    """
    def __init__(self, duration=30.0):
        super().__init__(duration)
        self.affected_systems = []
        self.warning_message = "WARNUNG: Systemausfall erkannt!"
        self.repair_time = 10.0  # Zeit bis zur automatischen Reparatur
        self.repair_timer = 0
    
    def update(self, dt, bodies, rocket):
        """
        Aktualisiert den Systemausfall
        
        Args:
            dt: Zeitschritt in Sekunden
            bodies: Liste der Himmelskörper
            rocket: Raketenobjekt
            
        Returns:
            True, wenn das Ereignis aktiv ist, False wenn es beendet ist
        """
        # Beim ersten Update Systeme auswählen
        if self.elapsed_time == 0:
            self._select_systems(rocket)
            
        # Aktualisiere Zeit
        self.elapsed_time += dt
        self.repair_timer += dt
        
        # Automatische Reparatur nach bestimmter Zeit
        if self.repair_timer >= self.repair_time:
            self._repair_systems(rocket)
            
        # Beende nach festgelegter Dauer
        if self.elapsed_time >= self.duration:
            self.active = False
            # Stelle sicher, dass alle Systeme repariert sind
            self._repair_systems(rocket)
            return False
            
        return True
    
    def _select_systems(self, rocket):
        """
        Wählt zufällige Systeme für einen Ausfall aus
        
        Args:
            rocket: Raketenobjekt
        """
        # Wähle 1-2 Systeme aus
        systems = list(rocket.engine_systems.keys()) + list(rocket.sensors.keys())
        num_failures = random.randint(1, 2)
        
        # Vermeide die Auswahl des Haupttriebwerks, wenn andere Systeme verfügbar sind
        if len(systems) > 1 and "main_engine" in systems:
            systems.remove("main_engine")
            
        self.affected_systems = random.sample(systems, min(num_failures, len(systems)))
        
        # Löse Systemausfälle aus
        for system in self.affected_systems:
            rocket.trigger_system_failure(system)
    
    def _repair_systems(self, rocket):
        """
        Repariert die ausgefallenen Systeme
        
        Args:
            rocket: Raketenobjekt
        """
        for system in self.affected_systems:
            rocket.repair_system(system)
        
        # Leere die Liste der betroffenen Systeme
        self.affected_systems = []
        self.repair_timer = 0
    
    def render(self, screen, camera, config):
        """
        Rendert visuelle Elemente des Systemausfalls
        
        Args:
            screen: Pygame-Surface zum Zeichnen
            camera: Kameraobjekt für Koordinatentransformation
            config: Konfigurationsobjekt
        """
        if self.affected_systems:
            # Zeige Warnmeldung an
            font = pygame.font.SysFont('Arial', 24)
            warning_text = font.render(self.warning_message, True, (255, 50, 50))
            warning_rect = warning_text.get_rect(center=(config.width // 2, 50))
            screen.blit(warning_text, warning_rect)
            
            # Zeige betroffene Systeme an
            system_font = pygame.font.SysFont('Arial', 18)
            for i, system in enumerate(self.affected_systems):
                system_text = system_font.render(f"Ausgefallen: {system}", True, (255, 150, 50))
                system_rect = system_text.get_rect(center=(config.width // 2, 80 + i * 25))
                screen.blit(system_text, system_rect)
            
            # Zeige Reparaturzeit an
            repair_progress = min(1.0, self.repair_timer / self.repair_time)
            repair_text = system_font.render(f"Reparatur: {int(repair_progress * 100)}%", True, (50, 255, 50))
            repair_rect = repair_text.get_rect(center=(config.width // 2, 80 + len(self.affected_systems) * 25))
            screen.blit(repair_text, repair_rect)


class EventManager:
    """
    Manager für alle Ereignisse in der Simulation
    """
    def __init__(self, config):
        self.config = config
        self.active_events = []
        self.cooldown = 0  # Cooldown zwischen Ereignissen
        self.min_cooldown = 30.0  # Mindestzeit zwischen Ereignissen
        self.event_types = [
            {"class": MeteorShower, "weight": 0.6, "enabled": config.meteors_enabled},
            {"class": SystemFailure, "weight": 0.4, "enabled": config.system_failures_enabled}
        ]
    
    def update(self, dt, bodies, rocket):
        """
        Aktualisiert alle aktiven Ereignisse und generiert neue
        
        Args:
            dt: Zeitschritt in Sekunden
            bodies: Liste der Himmelskörper
            rocket: Raketenobjekt
            
        Returns:
            Liste der aktiven Ereignisse
        """
        # Aktualisiere den Cooldown
        if self.cooldown > 0:
            self.cooldown -= dt
        
        # Aktualisiere aktive Ereignisse
        for event in self.active_events[:]:
            if not event.update(dt, bodies, rocket):
                self.active_events.remove(event)
        
        # Generiere ein neues Ereignis, wenn kein Cooldown aktiv ist und die Rakete nicht zerstört oder gelandet ist
        if (self.cooldown <= 0 and not self.active_events and not rocket.destroyed and 
            not rocket.landed and random.random() < self.config.event_probability):
            self.trigger_random_event()
        
        # Gib die Liste der aktiven Ereignisse zurück
        return self.active_events.copy() if self.active_events else []
    
    def trigger_random_event(self):
        """
        Löst ein zufälliges Ereignis basierend auf den Gewichtungen aus
        """
        # Filtere aktivierte Event-Typen
        enabled_events = [event for event in self.event_types if event["enabled"]]
        
        if not enabled_events:
            return
            
        # Berechne die Gesamtgewichtung
        total_weight = sum(event["weight"] for event in enabled_events)
        
        # Wähle ein zufälliges Ereignis basierend auf Gewichtung
        random_value = random.uniform(0, total_weight)
        cumulative_weight = 0
        
        for event_type in enabled_events:
            cumulative_weight += event_type["weight"]
            if random_value <= cumulative_weight:
                # Erstelle ein neues Ereignis
                new_event = event_type["class"]()
                self.active_events.append(new_event)
                
                # Setze den Cooldown
                self.cooldown = self.min_cooldown
                break
    
    def render(self, screen, camera):
        """
        Rendert alle aktiven Ereignisse
        
        Args:
            screen: Pygame-Surface zum Zeichnen
            camera: Kameraobjekt für Koordinatentransformation
        """
        for event in self.active_events:
            event.render(screen, camera, self.config) 