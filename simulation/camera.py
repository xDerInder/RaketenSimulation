import pygame

class Camera:
    """
    Kamera für die Simulation, die die Welt in Bildschirmkoordinaten umwandelt
    """
    def __init__(self, config):
        self.config = config
        self.position = pygame.math.Vector2(0, 0)
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.zoom_speed = 0.05  # Geschwindigkeit der Zoom-Animation
        
    def world_to_screen(self, world_pos):
        """
        Wandelt Weltkoordinaten in Bildschirmkoordinaten um
        
        Args:
            world_pos: Position in Weltkoordinaten
            
        Returns:
            Position in Bildschirmkoordinaten
        """
        # Kamera-relativ
        rel_x = (world_pos[0] - self.position.x) / self.config.scale * self.zoom
        rel_y = (world_pos[1] - self.position.y) / self.config.scale * self.zoom
        
        # In Bildschirmkoordinaten umwandeln (Bildschirmmitte als Ursprung)
        screen_x = self.config.width // 2 + rel_x
        screen_y = self.config.height // 2 + rel_y
        
        return (int(screen_x), int(screen_y))
        
    def screen_to_world(self, screen_pos):
        """
        Wandelt Bildschirmkoordinaten in Weltkoordinaten um
        
        Args:
            screen_pos: Position in Bildschirmkoordinaten
            
        Returns:
            Position in Weltkoordinaten
        """
        # In kamera-relative Koordinaten umwandeln
        rel_x = (screen_pos[0] - self.config.width // 2) * self.config.scale / self.zoom
        rel_y = (screen_pos[1] - self.config.height // 2) * self.config.scale / self.zoom
        
        # In Weltkoordinaten umwandeln
        world_x = self.position.x + rel_x
        world_y = self.position.y + rel_y
        
        return (world_x, world_y)
        
    def follow(self, position):
        """
        Setzt die Kameraposition, um ein Objekt zu verfolgen
        
        Args:
            position: Position des zu verfolgenden Objekts
        """
        self.position.x = position.x
        self.position.y = position.y
        
        # Sanfte Zoomstufenanpassung zu Ziel-Zoom
        if self.zoom != self.target_zoom:
            # Interpoliere in Richtung Ziel-Zoom
            self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed
            
            # Vermeidet Oszillation
            if abs(self.target_zoom - self.zoom) < 0.001:
                self.zoom = self.target_zoom
        
    def zoom_in(self):
        """
        Erhöht die Zoomstufe (näher heran)
        """
        self.target_zoom = min(self.config.max_zoom, self.target_zoom * 1.5)
        
    def zoom_out(self):
        """
        Verringert die Zoomstufe (weiter weg)
        """
        self.target_zoom = max(self.config.min_zoom, self.target_zoom / 1.5)
        
    def set_zoom(self, zoom_level):
        """
        Setzt die Zoomstufe direkt
        
        Args:
            zoom_level: Neue Zoomstufe
        """
        self.target_zoom = max(self.config.min_zoom, min(self.config.max_zoom, zoom_level))
        self.zoom = self.target_zoom  # Sofortiger Zoom ohne Animation