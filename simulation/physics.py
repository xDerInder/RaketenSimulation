import numpy as np
import pygame
import math

class PhysicsEngine:
    """
    Physik-Engine für die Weltraumsimulation
    Implementiert das N-Körper-Problem mit Gravitation zwischen allen Körpern
    """
    def __init__(self, config):
        self.config = config
        # Trajektorie der Rakete (für Visualisierung)
        self.trajectory = []
        # Maximale Anzahl der Punkte in der Trajektorie
        self.max_trajectory_points = 1000
        # Speichert die Trajektorie nur jeden X-ten Punkt
        self.trajectory_sample_interval = 10
        # Zähler für das Sampling der Trajektorie
        self.trajectory_counter = 0
    
    def update(self, dt, celestial_bodies, rocket):
        """
        Aktualisiert die Physik der Simulation
        
        Args:
            dt: Zeitschritt in Sekunden
            celestial_bodies: Liste aller Himmelskörper
            rocket: Raketenobjekt
        """
        # Gravitationsberechnungen (N-Körper-Problem)
        self._calculate_gravity(dt, celestial_bodies, rocket)
        
        # Kollisionserkennung
        self._check_collisions(celestial_bodies, rocket)
        
        # Aktualisiere die Trajektorie
        self.trajectory_counter += 1
        if self.trajectory_counter >= self.trajectory_sample_interval:
            self.trajectory.append(pygame.math.Vector2(rocket.position))
            self.trajectory_counter = 0
            
            # Begrenze die Länge der Trajektorie - AUSKOMMENTIERT für persistente Bahn
            # if len(self.trajectory) > self.max_trajectory_points:
            #     self.trajectory.pop(0)
    
    def _calculate_gravity(self, dt, celestial_bodies, rocket):
        """
        Berechnet die Gravitationskräfte zwischen allen Körpern
        
        Args:
            dt: Zeitschritt in Sekunden
            celestial_bodies: Liste aller Himmelskörper
            rocket: Raketenobjekt
        """
        # Planeten bewegen sich NICHT mehr (deaktiviert für Simulationsstabilität)
        # Aber ihre Gravitation wirkt weiterhin auf die Rakete
        
        # Nur die Rakete wird von der Gravitation beeinflusst
        if not rocket.landed:
            for body in celestial_bodies:
                self._apply_gravity_to_rocket(dt, rocket, body)
    
    def _apply_gravity_to_rocket(self, dt, rocket, celestial_body):
        """
        Wendet die Gravitationskraft eines Himmelskörpers auf die Rakete an
        
        Args:
            dt: Zeitschritt in Sekunden
            rocket: Raketenobjekt
            celestial_body: Himmelskörper
        """
        # Abstand und Richtungsvektor zwischen Rakete und Himmelskörper
        dx = celestial_body.position.x - rocket.position.x
        dy = celestial_body.position.y - rocket.position.y
        distance = (dx**2 + dy**2)**0.5
        
        # Richtungsvektor normalisieren
        if distance > 0:
            dx /= distance
            dy /= distance
            
        # Für den Mond reduzieren wir die Gravitation bei Annäherung, 
        # um eine stabilere Landung zu ermöglichen
        gravity_factor = 1.0
        if celestial_body.name == "Moon" and distance < celestial_body.radius * 5:
            # Bei Mondannäherung: Reduzierte Gravitation (bis 40% der normalen Stärke)
            # Dies hilft, langsamer und kontrollierbarer zu landen
            distance_factor = (distance - celestial_body.radius) / (celestial_body.radius * 4)
            gravity_factor = max(0.4, min(1.0, distance_factor))
            
            # Wenn wir eine Landung durchführen (Schub gegen den Mond), noch weniger Gravitation
            if rocket.thrust_forward:
                # Prüfen, ob die Rakete gegen den Mond gerichtet ist (±90° von der Landungsrichtung)
                landing_vector = pygame.math.Vector2(dx, dy)  # Vektor zum Mond
                rocket_direction = pygame.math.Vector2(1, 0).rotate(rocket.rotation)
                alignment = landing_vector.dot(rocket_direction)
                
                # Wenn die Rakete gegen den Mond gerichtet ist (Skalarprodukt negativ), reduziere Gravitation weiter
                if alignment < 0:
                    gravity_factor *= 0.8  # Nur 80% der bereits reduzierten Gravitation
            
        # Gravitationskraft berechnen: F = G * m1 * m2 / r^2
        # Angepasst durch den Gravitationsfaktor
        force_magnitude = self.config.G * celestial_body.mass * rocket.mass / (distance**2) * gravity_factor
        
        # Kraft in Beschleunigung umrechnen: a = F / m
        # Da wir die Masse der Rakete bereits in der Kraftberechnung hatten,
        # müssen wir hier nicht mehr durch die Masse teilen (würde sich rauskürzen)
        acceleration_x = force_magnitude * dx / rocket.mass
        acceleration_y = force_magnitude * dy / rocket.mass
        
        # Beschleunigung auf die Rakete anwenden
        rocket.velocity.x += acceleration_x * dt
        rocket.velocity.y += acceleration_y * dt
    
    def _check_collisions(self, celestial_bodies, rocket):
        """
        Überprüft auf Kollisionen zwischen der Rakete und Himmelskörpern
        
        Args:
            celestial_bodies: Liste aller Himmelskörper
            rocket: Raketenobjekt
        """
        for body in celestial_bodies:
            # Kollisionen mit allen Himmelskörpern prüfen
            # Keine Ausnahmen mehr für die Erde
                
            # Berechne den Abstand zwischen Rakete und Himmelskörper
            dx = body.position.x - rocket.position.x
            dy = body.position.y - rocket.position.y
            distance = (dx*dx + dy*dy)**0.5
            
            # Wenn der Abstand kleiner ist als die Summe der Radien, liegt eine Kollision vor
            if distance < body.radius:
                # Setze die Kollisionsflagge der Rakete
                rocket.collision_with = body
                
                # Vektor vom Körper zur Rakete für die Landeausrichtung
                approach_vector = pygame.math.Vector2(-dx, -dy).normalize()
                
                # Bewegungsrichtung der Rakete
                rocket_direction = pygame.math.Vector2(1, 0).rotate(rocket.rotation)
                
                # Winkel zwischen Landevektor und Raketenausrichtung
                # (1.0 = perfekt ausgerichtet, -1.0 = falsch ausgerichtet)
                alignment = approach_vector.dot(rocket_direction)
                
                # Berechne die Aufprallgeschwindigkeit
                impact_speed = (rocket.velocity.x - body.velocity.x)**2 + (rocket.velocity.y - body.velocity.y)**2
                impact_speed = impact_speed**0.5
                
                # Für den Mond spezifisch großzügigere Parameter verwenden
                is_special_moon_landing = body.name == "Moon" and alignment < 0  # Für den Mond: Wenn Triebwerk einigermaßen zum Mond zeigt
                is_aligned_for_landing = alignment < -0.5 or is_special_moon_landing
                
                # Höhere Geschwindigkeitsgrenze bei korrekter Ausrichtung
                # Für den Mond noch großzügiger sein
                if body.name == "Moon":
                    # Für den Mond viel höhere Toleranz
                    
                    # Aktualisiere den Abstand nach der Positionskorrektur
                    dx = body.position.x - rocket.position.x
                    dy = body.position.y - rocket.position.y
                    distance = (dx**2 + dy**2)**0.5
                
                # Relative Geschwindigkeit zum Planeten berechnen
                rel_vx = rocket.velocity.x - body.velocity.x
                rel_vy = rocket.velocity.y - body.velocity.y
                impact_speed = (rel_vx**2 + rel_vy**2)**0.5
                
                # Richtung, in die die Rakete zeigt (normalisierter Vektor)
                rocket_direction_x = math.cos(math.radians(rocket.rotation))
                rocket_direction_y = math.sin(math.radians(rocket.rotation))
                
                # Richtung zum Planeten (normalisierter Vektor)
                to_planet_x = dx / distance if distance > 0 else 0
                to_planet_y = dy / distance if distance > 0 else 0
                
                # Skalarprodukt gibt -1 für perfekte Ausrichtung zur Landung (Rakete zeigt vom Planeten weg)
                alignment = rocket_direction_x * to_planet_x + rocket_direction_y * to_planet_y
                
                # Für die Landung: Rakete sollte vom Planeten wegzeigen (nach unten)
                is_aligned_for_landing = alignment < -0.7  # Ein Winkel von etwa ±45° ist akzeptabel
                
                # Bei zu hoher Geschwindigkeit oder falscher Ausrichtung: Abprallen
                if impact_speed >= 100.0 or not is_aligned_for_landing:
                    # Berechne den Reflexionsvektor für das Abprallen
                    dot_product = (rel_vx * to_planet_x + rel_vy * to_planet_y)
                    
                    # Reflexionsvektor berechnen (mit Energieverlust durch Dämpfungsfaktor)
                    dampening = 0.5  # Dämpfungsfaktor (1.0 = elastisch, 0.0 = komplett gedämpft)
                    reflect_vx = rel_vx - 2 * dot_product * to_planet_x
                    reflect_vy = rel_vy - 2 * dot_product * to_planet_y
                    
                    # Neue Geschwindigkeit setzen (mit Dämpfung)
                    rocket.velocity.x = body.velocity.x + reflect_vx * dampening
                    rocket.velocity.y = body.velocity.y + reflect_vy * dampening
                    
                    if impact_speed > 200.0:
                        print(f"Kollision mit {body.name}! Aufprallgeschwindigkeit: {impact_speed:.1f} m/s")
                        # Bei sehr hoher Geschwindigkeit wird die Rakete zerstört
                        if impact_speed > 500.0:
                            rocket.destroyed = True
                            rocket.collision_with = body
                            print(f"Rakete wurde bei Kollision mit {body.name} zerstört!")
                else:
                    # Sanfte Landung - positioniere die Rakete auf die Oberfläche
                    normal_x = dx / distance
                    normal_y = dy / distance
                    offset = (body.radius + rocket.radius) - distance
                    rocket.position.x -= normal_x * offset * 1.01  # Leicht nach außen versetzen
                    rocket.position.y -= normal_y * offset * 1.01
                    
                    # Markiere die Rakete als gelandet
                    rocket.landed = True
                    rocket.landed_on = body
                    # Geschwindigkeit synchronisieren
                    rocket.velocity.x = body.velocity.x
                    rocket.velocity.y = body.velocity.y
                    
                    print(f"Rakete erfolgreich auf {body.name} gelandet! (Geschwindigkeit: {impact_speed:.1f} m/s)")
    
    def runge_kutta4_step(self, y, f, dt):
        """
        Führt einen Runge-Kutta-4-Integrationsschritt durch
        
        Args:
            y: Aktueller Zustand [Position, Geschwindigkeit]
            f: Funktion, die dy/dt berechnet (Beschleunigung)
            dt: Zeitschritt
            
        Returns:
            Neuer Zustand nach dem Integrationsschritt
        """
        k1 = f(y)
        k2 = f(y + dt/2 * k1)
        k3 = f(y + dt/2 * k2)
        k4 = f(y + dt * k3)
        
        return y + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
    
    def calculate_orbital_parameters(self, rocket, central_body):
        """
        Berechnet die Orbitalparameter der Rakete um einen Zentralkörper
        
        Args:
            rocket: Raketenobjekt
            central_body: Zentraler Himmelskörper
            
        Returns:
            Dictionary mit Orbitalparametern
        """
        # Vektor von Zentralkörper zur Rakete
        r_vec = pygame.math.Vector2(
            rocket.position.x - central_body.position.x,
            rocket.position.y - central_body.position.y
        )
        r = r_vec.length()
        
        # Geschwindigkeitsvektor relativ zum Zentralkörper
        v_vec = pygame.math.Vector2(
            rocket.velocity.x - central_body.velocity.x,
            rocket.velocity.y - central_body.velocity.y
        )
        v = v_vec.length()
        
        # Berechne spezifische Energie
        mu = self.config.G * central_body.mass
        specific_energy = v**2 / 2 - mu / r
        
        # Bestimme Bahntyp
        if abs(specific_energy) < 1e-10:  # Fast 0 = Parabel
            orbit_type = "Parabolic"
            semimajor_axis = float('inf')
        elif specific_energy < 0:  # Negativ = Ellipse
            orbit_type = "Elliptic"
            semimajor_axis = -mu / (2 * specific_energy)
        else:  # Positiv = Hyperbel
            orbit_type = "Hyperbolic"
            semimajor_axis = mu / (2 * specific_energy)
        
        # Spezifischer Drehimpuls (senkrecht zur Orbitalebene in 2D)
        h_vec = r_vec.cross(v_vec)  # In 2D ist dies ein Skalar
        
        # Exzentrizitätsvektor
        e_vec_x = (v**2 * r_vec.x - (r_vec.x * v_vec.x + r_vec.y * v_vec.y) * v_vec.x) / mu - r_vec.x / r
        e_vec_y = (v**2 * r_vec.y - (r_vec.x * v_vec.x + r_vec.y * v_vec.y) * v_vec.y) / mu - r_vec.y / r
        e_vec = pygame.math.Vector2(e_vec_x, e_vec_y)
        eccentricity = e_vec.length()
        
        # Periapsis und Apoapsis (nur für elliptische Bahnen sinnvoll)
        if orbit_type == "Elliptic":
            periapsis = semimajor_axis * (1 - eccentricity)
            apoapsis = semimajor_axis * (1 + eccentricity)
        else:
            periapsis = semimajor_axis * (1 - eccentricity) if eccentricity < 1 else None
            apoapsis = None
        
        # Orbitalperiode (nur für elliptische Bahnen)
        if orbit_type == "Elliptic":
            period = 2 * np.pi * (semimajor_axis**3 / mu)**0.5
        else:
            period = None
        
        return {
            "type": orbit_type,
            "semimajor_axis": semimajor_axis,
            "eccentricity": eccentricity,
            "periapsis": periapsis,
            "apoapsis": apoapsis,
            "period": period,
            "specific_energy": specific_energy
        } 