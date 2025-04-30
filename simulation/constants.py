"""
Konstanten für die Weltraumsimulation
Alle Werte in SI-Einheiten (Meter, Kilogramm, Sekunden)
"""

# Astronomische Konstanten
# Massen (kg)
SUN_MASS = 1.989e30
MERCURY_MASS = 3.301e23
VENUS_MASS = 4.867e24
EARTH_MASS = 5.972e24
MOON_MASS = 7.348e22 * 2.0  # Mondmasse verdoppelt für stärkere Anziehungskraft
MARS_MASS = 6.417e23
JUPITER_MASS = 1.898e27
SATURN_MASS = 5.683e26
URANUS_MASS = 8.681e25
NEPTUNE_MASS = 1.024e26

# Radien (m) - erhöht für bessere Sichtbarkeit und einfacheres Erreichen
SUN_RADIUS = 6.957e8 * 2  # doppelt so groß
MERCURY_RADIUS = 2.440e6 * 5  # 5x so groß
VENUS_RADIUS = 6.052e6 * 5  # 5x so groß
EARTH_RADIUS = 6.371e6 * 5  # 5x so groß
MOON_RADIUS = 1.737e6 * 5  # 5x so groß
MARS_RADIUS = 3.390e6 * 10  # 10x so groß, besonders Mars für leichteres Erreichen
JUPITER_RADIUS = 6.991e7 * 3  # 3x so groß
SATURN_RADIUS = 5.823e7 * 3  # 3x so groß
URANUS_RADIUS = 2.536e7 * 3  # 3x so groß
NEPTUNE_RADIUS = 2.462e7 * 3  # 3x so groß

# Mittlere Abstände zur Sonne (m)
MERCURY_ORBIT = 5.790e10 * 0.05  # Auf 5% reduziert
VENUS_ORBIT = 1.082e11 * 0.05    # Auf 5% reduziert
EARTH_ORBIT = 1.496e11 * 0.05    # Auf 5% reduziert
MARS_ORBIT = 2.279e11 * 0.05     # Auf 5% reduziert (extrem verkleinertes Sonnensystem)
JUPITER_ORBIT = 7.785e11 * 0.05  # Auf 5% reduziert
SATURN_ORBIT = 1.432e12 * 0.05   # Auf 5% reduziert
URANUS_ORBIT = 2.867e12 * 0.05   # Auf 5% reduziert
NEPTUNE_ORBIT = 4.498e12 * 0.05  # Auf 5% reduziert

# Orbitalgeschwindigkeiten (m/s)
MERCURY_VELOCITY = 4.787e4
VENUS_VELOCITY = 3.502e4
EARTH_VELOCITY = 2.978e4
MARS_VELOCITY = 2.407e4
JUPITER_VELOCITY = 1.307e4
SATURN_VELOCITY = 9.687e3
URANUS_VELOCITY = 6.800e3
NEPTUNE_VELOCITY = 5.432e3

# Monde
MOON_ORBIT = 3.844e8 * 0.5  # Abstand zur Erde (m) - auf 50% reduziert für leichteres Erreichen
MOON_VELOCITY = 1.022e3  # Orbitalgeschwindigkeit (m/s)

# Raketenkonstanten
DEFAULT_ROCKET_MASS = 1.0e5  # 100 Tonnen (kg)
DEFAULT_FUEL_MASS = 8.0e4  # 80 Tonnen (kg)
DEFAULT_ENGINE_THRUST = 2.0e7  # 20 MN (Newton) - erhöht von 10MN für bessere Bremswirkung
DEFAULT_SPECIFIC_IMPULSE = 350.0  # Spezifischer Impuls (s)
DEFAULT_EXHAUST_VELOCITY = 350.0 * 9.81  # Isp * g0 (m/s)
DEFAULT_FUEL_CONSUMPTION = (DEFAULT_ENGINE_THRUST / DEFAULT_EXHAUST_VELOCITY) / 1000.0  # kg/s