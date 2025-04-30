import pygame
import math
import random
from enum import Enum, auto

class NavigationMode(Enum):
    IDLE = auto()
    TRANSIT = auto()        # Flying towards target, far away
    APPROACH = auto()       # Closer to target, managing speed
    BRAKING = auto()        # Actively decelerating for landing approach
    LANDING = auto()        # Final descent and touchdown
    LANDED = auto()         # State after successful landing
    CRASHED = auto()        # State after destruction

class AutoPilot:
    """
    Autopilot-System für die automatische Steuerung der Rakete
    """
    def __init__(self, config):
        self.config = config
        self.enabled = False
        self.target = None
        self.target_distance = None
        self.mode = NavigationMode.IDLE
        self.target_selection_timer = 0  # Timer für die zufällige Zielauswahl
        
        # Parameter für PID-Regler
        self.rotation_kp = 0.5
        self.rotation_ki = 0.1
        self.rotation_kd = 0.2
        self.rotation_integral = 0
        self.rotation_prev_error = 0
        
        self.thrust_kp = 0.01
        self.thrust_ki = 0.005
        self.thrust_kd = 0.02
        self.thrust_integral = 0
        self.thrust_prev_error = 0
        
        # Minimale Entfernung zum Planeten für Landeanflug (proportional zum Radius)
        self.landing_approach_factor = 3.0
        
        self.target_orbit_altitude = 300_000  # Standard-Orbithöhe in Metern
        self.orbit_tolerance = 0.1  # Toleranz für die Orbitalparameter
        self.current_action_time = 0  # Zeit, die der aktuelle Aktionszustand aktiv ist
        self.action_timeout = 10.0  # Maximale Zeit für eine Aktion bevor ein neuer Plan erstellt wird
        self.evasive_maneuver_active = False
        self.evasive_direction = 1  # 1 oder -1 für die Richtung des Ausweichmanövers
        self.evasive_timer = 0
        self.course_correction_timer = 0
        self.random_destination_timer = 0
        self.random_destination_interval = 180.0  # 3 Minuten zwischen zufälligen Zielen
        
        # PID Controller Parameter für Orbitalstabilisierung
        self.pid_params = {
            'orbit': {
                'p': 0.05,
                'i': 0.001,
                'd': 0.02,
                'integral': 0,
                'prev_error': 0
            },
            'approach': {
                'p': 0.1,
                'i': 0.002,
                'd': 0.05,
                'integral': 0,
                'prev_error': 0
            }
        }
        
        # --- PID für Rotation ---
        # Moderate PID-Werte für Rotation (Kompromiss)
        self.rotation_pid = {'p': 0.4, 'i': 0.015, 'd': 0.2, 'integral': 0, 'prev_error': 0, 'max_integral': 50}
        
        # --- Neue Parameter für verbesserte Landung ---
        self.altitude_above_ground = 0
        self.required_thrust_for_hover = 0
        
        # Schwellenwerte für Bremsmodus
        self.BRAKING_ENTRY_SPEED_THRESHOLD = 1000 # m/s - Geschwindigkeit, über der Bremsen nötig ist
        self.BRAKING_EXIT_SPEED_THRESHOLD = 200  # m/s - Geschwindigkeit, unter der Landemodus beginnt
        self.MAX_LANDING_SPEED_VERTICAL = 5     # m/s - Max. sichere Landegeschwindigkeit vertikal
        self.MAX_LANDING_SPEED_HORIZONTAL = 2   # m/s - Max. sichere Landegeschwindigkeit horizontal

    def enable(self):
        """
        Aktiviert den Autopiloten
        """
        self.enabled = True
        print("Autopilot aktiviert")
        
    def disable(self):
        """
        Deaktiviert den Autopiloten
        """
        self.enabled = False
        self._reset_rocket_controls()
        print("Autopilot deaktiviert")
        
    def toggle(self):
        """
        Schaltet den Autopiloten ein oder aus
        """
        if self.enabled:
            self.disable()
        else:
            self.enable()
            
    def set_target(self, target_body, target_altitude=None):
        """
        Setzt das Ziel für den Autopiloten
        
        Args:
            target_body: Zielkörper (Himmelskörper)
            target_altitude: Gewünschte Orbithöhe (optional)
        """
        self.target = target_body
        if target_altitude is not None:
            self.target_orbit_altitude = target_altitude
        
        # Setze den Navigationsmodus NICHT hier fest. 
        # Die update-Methode wählt den Modus basierend auf der Entfernung.
        # self.mode = NavigationMode.ORBIT_ADJUST # Entfernt!
        print(f"Neues Ziel: {target_body.name} mit Orbithöhe {self.target_orbit_altitude/1000:.0f} km")
        
    def choose_random_destination(self, celestial_bodies):
        """
        Wählt einen zufälligen Planeten als Ziel aus
        
        Args:
            celestial_bodies: Liste der Himmelskörper
        """
        # Filtere verfügbare Himmelskörper (alles außer Sonne)
        available_bodies = [body for body in celestial_bodies if body.name != "Sun"]
        
        # Wenn keine Himmelskörper verfügbar sind, Autopilot deaktivieren
        if not available_bodies:
            self.disable()
            return
        
        # Wähle einen zufälligen Himmelskörper
        self.target = random.choice(available_bodies)
        self.target_orbit_altitude = self.target.radius * 2
        
        print(f"Autopilot: Neues Ziel ist {self.target.name} mit Orbithöhe {self.target_orbit_altitude/1000:.0f} km")
        
    def update(self, dt, rocket, celestial_bodies):
        if not self.enabled or self.target is None:
            self.mode = NavigationMode.IDLE
            # Ensure controls are reset if autopilot becomes inactive
            rocket.thrust_level = 0.0
            rocket.thrust_forward = False
            rocket.rotate_clockwise = False
            rocket.rotate_counterclockwise = False
            return

        # --- Vektoren und Distanzen ---
        vec_rocket_pos = rocket.position
        vec_rocket_vel = rocket.velocity
        vec_target_pos = self.target.position
        vec_target_vel = self.target.velocity
        vec_to_target = vec_target_pos - vec_rocket_pos
        target_distance = vec_to_target.length()
        vec_relative_velocity = vec_rocket_vel - vec_target_vel
        relative_speed = vec_relative_velocity.length()
        # Höhe über Grund (Radius des Ziels abziehen)
        altitude = max(0, target_distance - self.target.radius)

        # --- Schwellenwerte ---
        far_distance = self.target.radius * 50 # Grenze zwischen TRANSIT und anderen Modi

        # ==================================
        # ===== 1. MODUS BESTIMMEN =========
        # ==================================
        intended_mode = self.mode # Standard: Modus beibehalten

        # Prüfe zuerst, ob wir bereits gelandet oder gecrasht sind
        if self.mode == NavigationMode.LANDED or self.mode == NavigationMode.CRASHED:
            intended_mode = self.mode # Bleibe in diesem Endzustand

        # Dann prüfe, ob wir gerade die Oberfläche erreicht haben
        elif altitude <= 0:
            # Prüfe Landegeschwindigkeit für LANDED/CRASHED Entscheidung
            # Vertikale Geschw. relativ zur Oberfläche (Sinkgeschwindigkeit ist hier negativ)
            radial_unit_vector = -vec_to_target.normalize()
            vertical_velocity_ground = vec_relative_velocity.dot(radial_unit_vector)
            # Horizontale Geschwindigkeit
            vec_horizontal_velocity_ground = vec_relative_velocity - (radial_unit_vector * vertical_velocity_ground)
            horizontal_speed_ground = vec_horizontal_velocity_ground.length()

            print(f"Kontakt! Vert. Geschw.: {vertical_velocity_ground:.2f}, Horiz. Geschw.: {horizontal_speed_ground:.2f}")

            # Check against landing speed limits (vertical is speed towards surface)
            if abs(vertical_velocity_ground) < self.MAX_LANDING_SPEED_VERTICAL and horizontal_speed_ground < self.MAX_LANDING_SPEED_HORIZONTAL:
                intended_mode = NavigationMode.LANDED
            else:
                intended_mode = NavigationMode.CRASHED

        # Wenn noch in der Luft: Entscheide basierend auf Distanz und Geschwindigkeit
        elif target_distance > far_distance:
            # Weit weg -> IMMER TRANSIT (außer LANDED/CRASHED, was oben behandelt wird)
            intended_mode = NavigationMode.TRANSIT

        elif target_distance <= far_distance:
            # Nah dran -> BRAKING oder LANDING
            if self.mode == NavigationMode.BRAKING:
                # Wenn wir bremsen, bleiben wir drin, bis wir langsam genug sind
                if relative_speed < self.BRAKING_EXIT_SPEED_THRESHOLD:
                    intended_mode = NavigationMode.LANDING # Langsam genug für Landeanflug
                # else: intended_mode bleibt BRAKING
            elif self.mode == NavigationMode.LANDING:
                # Wenn wir im Landeanflug sind, bleiben wir erstmal drin
                # (Könnte später noch Logik bekommen, um ggf. wieder zu BRAKING zu wechseln, wenn Speed zu hoch wird)
                intended_mode = NavigationMode.LANDING
            else:
                # Wenn wir gerade erst nah rangekommen sind (von TRANSIT oder IDLE)
                if relative_speed > self.BRAKING_ENTRY_SPEED_THRESHOLD:
                    intended_mode = NavigationMode.BRAKING # Zu schnell -> Bremsen
                else:
                    intended_mode = NavigationMode.LANDING # Langsam genug -> direkt Landen

        # --- Moduswechsel-Logik (Logging, PID Reset etc.) ---
        if intended_mode != self.mode:
            print(f"MODE CHANGE: {self.mode.name} -> {intended_mode.name} (Dist: {target_distance/1000:.1f}km, Alt: {altitude:.0f}m, Speed: {relative_speed:.1f}m/s)")
            # PID Reset bei Wechsel zu/von Rotations-intensiven Modi
            if intended_mode in [NavigationMode.BRAKING, NavigationMode.LANDING, NavigationMode.TRANSIT] or \
               self.mode in [NavigationMode.BRAKING, NavigationMode.LANDING, NavigationMode.TRANSIT]:
                 # Reset PID only if it exists and is a dictionary (defensive check)
                 if hasattr(self, 'rotation_pid') and isinstance(self.rotation_pid, dict):
                     self.rotation_pid['integral'] = 0
                     self.rotation_pid['prev_error'] = 0
            self.mode = intended_mode

        # ==================================
        # ===== 2. MODUS AUSFÜHREN ========
        # ==================================

        # Endzustände: Keine Steuerung mehr, Autopilot deaktivieren
        if self.mode == NavigationMode.LANDED or self.mode == NavigationMode.CRASHED:
            rocket.thrust_level = 0.0
            rocket.thrust_forward = False
            rocket.rotate_clockwise = False
            rocket.rotate_counterclockwise = False
            if self.mode == NavigationMode.LANDED:
                 # Optional: Rakete exakt auf Oberfläche "kleben" und Geschwindigkeit anpassen
                 try:
                     # Match target velocity
                     rocket.velocity = pygame.math.Vector2(self.target.velocity)
                     # Place exactly on surface
                     surface_normal = -vec_to_target.normalize()
                     # Prevent division by zero or zero vector if already at center
                     if vec_to_target.length_squared() > 1e-6:
                          rocket.position = vec_target_pos + surface_normal * self.target.radius
                     print("LANDED SUCCESSFULLY!")
                 except Exception as e:
                     print(f"Error setting final position/velocity after landing: {e}")
            else:
                 # Crash message printed during mode determination
                 print(f"CRASHED!")

            self.enabled = False # Autopilot abschalten nach Endzustand
            return

        # Transit-Modus: Zum Ziel fliegen
        elif self.mode == NavigationMode.TRANSIT:
            target_angle = math.degrees(math.atan2(vec_to_target.y, vec_to_target.x))
            self._control_rotation_pid(dt, rocket, target_angle)

            current_angle = rocket.rotation % 360
            angle_diff = self._angle_diff(current_angle, target_angle)

            # Schub geben, wenn grob ausgerichtet
            if angle_diff < 30:
                rocket.thrust_forward = True
                rocket.thrust_level = 1.0
            else:
                rocket.thrust_forward = False
                rocket.thrust_level = 0.0

            if random.random() < 0.01: # Weniger Output
                 print(f"TRANSIT zu {self.target.name}: Dist: {target_distance/1000:.1f}km, AngleDiff: {angle_diff:.1f}°, Thrust: {rocket.thrust_level*100:.0f}%")

        # Brems-Modus: Gegen Flugrichtung ausrichten und bremsen
        elif self.mode == NavigationMode.BRAKING:
            # Ziel: Gegen die relative Geschwindigkeit ausrichten
            if relative_speed > 1.0: # Nur wenn nennenswerte Geschwindigkeit vorhanden
                # Winkel der Relativgeschwindigkeit + 180 Grad
                target_angle = (math.degrees(math.atan2(vec_relative_velocity.y, vec_relative_velocity.x)) + 180) % 360
            else:
                # Bei sehr geringer Geschwindigkeit: Vertikal zum Ziel ausrichten (Vorbereitung Landung)
                # Zielwinkel zeigt senkrecht vom Ziel weg
                 target_angle = math.degrees(math.atan2(-vec_to_target.y, -vec_to_target.x))


            self._control_rotation_pid(dt, rocket, target_angle)

            # Schub geben, wenn grob ausgerichtet
            current_angle = rocket.rotation % 360
            angle_diff = self._angle_diff(current_angle, target_angle)
            if angle_diff < 45: # Größere Toleranz beim Bremsen
                rocket.thrust_forward = True
                rocket.thrust_level = 1.0
            else:
                rocket.thrust_forward = False
                rocket.thrust_level = 0.0

            if random.random() < 0.05: # Weniger Output
                print(f"BRAKING: Speed: {relative_speed:.1f}m/s | Alt: {altitude:.0f}m | AlignDiff: {angle_diff:.1f}° | Thrust: {rocket.thrust_level*100:.0f}%")

        # Lande-Modus: Feinsteuerung für vertikale und horizontale Geschwindigkeit
        elif self.mode == NavigationMode.LANDING:
            # --- Schwerkraft berechnen (vereinfacht) ---
            G = 6.67430e-11
            gravity_force_magnitude = (G * self.target.mass * rocket.mass) / max(target_distance**2, 1e-6)
            gravity_accel_magnitude = gravity_force_magnitude / rocket.mass
            vec_gravity_accel = vec_to_target.normalize() * gravity_accel_magnitude

            # --- Zielgeschwindigkeiten definieren (wie vorher) ---
            target_vertical_speed = 0 # Target speed towards surface (negative)
            if altitude > 20000: target_vertical_speed = -150.0
            elif altitude > 5000: target_vertical_speed = -150.0 * ((altitude - 5000) / 15000)**1.5; target_vertical_speed = max(target_vertical_speed, -150)
            elif altitude > 1000: target_vertical_speed = -50.0 * ((altitude - 1000) / 4000)**1.2; target_vertical_speed = max(target_vertical_speed, -50)
            elif altitude > 50: target_vertical_speed = -10.0 * (altitude / 1000.0)
            else: target_vertical_speed = -1.0 # Final descent speed

            # --- Aktuelle Geschwindigkeiten zerlegen ---
            radial_unit_vector = -vec_to_target.normalize()
            vertical_velocity = vec_relative_velocity.dot(radial_unit_vector) # Positive = moving away
            vec_vertical_velocity = radial_unit_vector * vertical_velocity
            vec_horizontal_velocity = vec_relative_velocity - vec_vertical_velocity
            horizontal_speed = vec_horizontal_velocity.length()

            # --- Benötigte Korrektur-Beschleunigung berechnen (P-Regler) ---
            # Vertikal: Fehler zur Zielgeschwindigkeit (target is negative, velocity positive if ascending)
            # We want vertical_velocity to match target_vertical_speed
            vertical_error = target_vertical_speed - vertical_velocity
            # required_vertical_accel is the acceleration needed *radially outwards*
            required_vertical_accel = vertical_error * 0.8 # P-controller for vertical speed

            # Horizontal: Ziel ist 0 m/s
            required_horizontal_accel_vec = pygame.math.Vector2(0,0)
            if horizontal_speed > 0.1:
                 # Acceleration opposite to horizontal velocity
                 required_horizontal_accel_vec = -vec_horizontal_velocity.normalize() * horizontal_speed * 1.5 # P-controller for horizontal speed

            # Vektorielle Summe der *Korrektur*-Beschleunigungen
            total_required_correction_accel = required_horizontal_accel_vec + (radial_unit_vector * required_vertical_accel)

            # --- Gesamtbeschleunigung durch Schub ---
            # a_thrust = a_correction - a_gravity (vectors)
            # a_gravity points towards target, so -a_gravity points away
            final_accel_vec_by_thrust = total_required_correction_accel - vec_gravity_accel

            # --- Schubkraft und Richtung bestimmen ---
            required_thrust_force_vec = final_accel_vec_by_thrust * rocket.mass
            thrust_magnitude = required_thrust_force_vec.length()

            # Zielwinkel der Rakete (entgegengesetzt zur Schubrichtung)
            if thrust_magnitude > 0.01:
                thrust_direction_vec = required_thrust_force_vec.normalize()
                target_angle = (math.degrees(math.atan2(thrust_direction_vec.y, thrust_direction_vec.x)) + 180) % 360
            else:
                # Kein Schub nötig -> vertikal ausrichten (pointing away from target)
                target_angle = math.degrees(math.atan2(-vec_to_target.y, -vec_to_target.x))

            # --- Schublevel berechnen und begrenzen ---
            required_thrust_level = thrust_magnitude / rocket.max_thrust if rocket.max_thrust > 0 else 0
            required_thrust_level = max(0.0, min(1.0, required_thrust_level))

            # --- Steuerung anwenden ---
            self._control_rotation_pid(dt, rocket, target_angle)
            current_angle = rocket.rotation % 360
            thrust_align_angle_diff = self._angle_diff(current_angle, target_angle)

            # Schub nur geben, wenn genau ausgerichtet
            if thrust_align_angle_diff < 10: # Strict alignment for landing thrust
                rocket.thrust_forward = True
                rocket.thrust_level = required_thrust_level
            else:
                rocket.thrust_forward = False
                rocket.thrust_level = 0.0

            if random.random() < 0.05: # Weniger Output
                print(f"LANDING: Alt: {altitude:.0f}m | Vvert: {vertical_velocity:.1f} (Tgt: {target_vertical_speed:.1f}) | Vhoriz: {horizontal_speed:.1f} | Thrust: {rocket.thrust_level*100:.1f}% | AlignDiff: {thrust_align_angle_diff:.1f}°")

        # --- Fallback/Default: Controls reset ---
        # This should ideally not be reached if logic is correct, but as a safety net
        else:
             print(f"WARNING: Reached unexpected state in autopilot update. Mode: {self.mode}. Resetting controls.")
             rocket.thrust_level = 0.0
             rocket.thrust_forward = False
             rocket.rotate_clockwise = False
             rocket.rotate_counterclockwise = False
            
    # --- Hilfsmethoden für Winkelberechnung und PID ---
    def _angle_diff(self, angle1, angle2):
        """ Berechnet die kürzeste Differenz zwischen zwei Winkeln in Grad. """
        diff = (angle2 - angle1 + 180) % 360 - 180
        return abs(diff)

    def _control_rotation_pid(self, dt, rocket, target_angle):
        """ Steuert die Rotation der Rakete mit einem PID-Regler. """
        target_angle = target_angle % 360
        current_angle = rocket.rotation % 360

        error = (target_angle - current_angle + 180) % 360 - 180

        pid = self.rotation_pid
        pid['integral'] += error * dt
        pid['integral'] = max(min(pid['integral'], pid['max_integral']), -pid['max_integral']) # Anti-Windup

        derivative = (error - pid['prev_error']) / dt if dt > 0 else 0

        # Berechne Steuersignal
        control = pid['p'] * error + pid['i'] * pid['integral'] + pid['d'] * derivative

        # Rotationsgeschwindigkeit basierend auf Steuersignal setzen
        # Muss an rocket.rotation_speed angepasst werden, falls Rakete direkt Geschwindigkeit steuert
        # Annahme: rocket.rotate_clockwise/counterclockwise steuert direkt
        turn_threshold = 1.0 # Grad-Fehler, unter dem nicht mehr gedreht wird
        max_rotation_power = 5.0 # Skalierungsfaktor für die Drehkraft

        if abs(error) > turn_threshold:
            if control > 0:
                rocket.rotate_clockwise = True
                rocket.rotate_counterclockwise = False
                # Hier könnte man die `rotation_speed` anpassen, falls verfügbar
            else:
                rocket.rotate_clockwise = False
                rocket.rotate_counterclockwise = True
                # Hier könnte man die `rotation_speed` anpassen, falls verfügbar
        else:
            rocket.rotate_clockwise = False
            rocket.rotate_counterclockwise = False

        pid['prev_error'] = error