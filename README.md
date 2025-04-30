# Raketensimulation

Eine physikalisch korrekte 2D-Weltraumsimulation, die das Fliegen einer Rakete im Sonnensystem ermöglicht.

## Funktionen

- Vollständig physikalisch korrekte Simulation des N-Körper-Problems
- Realistische Raketenphysik mit Schub, Masse, Brennstoffverbrauch und Delta-V
- Komplettes Sonnensystem mit allen Planeten und wichtigen Monden
- Dynamische Kamera mit automatischem Zoom
- Zufällige Ereignisse wie Meteoritenschauer und Systemausfälle
- Detaillierte UI mit Telemetrie- und Orbitaldaten
- Fortschrittlicher Autopilot mit verschiedenen Navigationsmodi

## Installation

### Voraussetzungen

- Python 3.7 oder höher
- PyGame 2.0.0 oder höher

### Installation

1. Klone dieses Repository oder lade es als ZIP-Datei herunter.
2. Installiere die erforderlichen Abhängigkeiten:

```bash
pip install pygame numpy
```

## Verwendung

Starte die Simulation mit:

```bash
python main.py
```

### Steuerung

- **P**: Autopilot ein-/ausschalten
- **R**: Zufälliges Ziel für den Autopiloten wählen
- **1-4**: Voreingestellte Ziele wählen (1: Venus, 2: Erde, 3: Mars, 4: Jupiter)

Manuelle Steuerung (wenn Autopilot deaktiviert):
- **W**: Haupttriebwerk aktivieren (vorwärts)
- **S**: Rückwärtstreiber aktivieren
- **A**: Links drehen
- **D**: Rechts drehen

Allgemeine Steuerung:
- **Q**: Hineinzoomen
- **E**: Herauszoomen
- **C**: Kameraverfolgung ein/aus
- **Leertaste**: Pause
- **ESC**: Beenden

## Autopilot-System

Die Simulation verfügt über ein fortschrittliches Autopilot-System, das die Rakete automatisch steuern kann. Der Autopilot kann:

- Zwischen verschiedenen Planeten navigieren
- Die Rakete in einen stabilen Orbit um einen Planeten bringen
- Die Orbitalhöhe anpassen und stabilisieren
- Auf Ereignisse wie Meteoritenschauer reagieren
- Kurskorrekturen durchführen
- Ausweichmanöver einleiten

Der Autopilot verwendet verschiedene Navigationsmodi:
- **IDLE**: Wartemodus, keine Aktion
- **ORBIT_MAINTAIN**: Hält einen stabilen Orbit
- **ORBIT_ADJUST**: Passt die Orbitalhöhe an
- **PLANET_APPROACH**: Nähert sich einem Planeten
- **EVASIVE_MANEUVER**: Führt ein Ausweichmanöver durch
- **COURSE_CORRECTION**: Führt eine Kurskorrektur durch

## Physikalisches Modell

Die Simulation implementiert folgende physikalische Konzepte:

- Gravitationskraft nach Newton (F = G·m₁·m₂/r²)
- N-Körper-Problem (jeder Körper beeinflusst jeden anderen)
- Raketengleichung nach Ziolkowski (Δv = v_e·ln(m₀/m₁))
- Numerische Integration (Runge-Kutta-Verfahren)
- Realistische Bahnmechanik (Keplersche Gesetze)

## Projektstruktur

- `main.py`: Hauptdatei zum Starten der Simulation
- `simulation/config.py`: Konfigurationseinstellungen
- `simulation/constants.py`: Astronomische und physikalische Konstanten
- `simulation/engine.py`: Hauptsimulationsschleife und Rendering
- `simulation/physics.py`: Physikalische Berechnungen
- `simulation/rocket.py`: Raketenmodell
- `simulation/celestial_bodies.py`: Planeten und andere Himmelskörper
- `simulation/camera.py`: Kamerasteuerung und Zoom
- `simulation/events.py`: Zufällige Ereignisse
- `simulation/ui.py`: Benutzeroberfläche
- `simulation/autopilot.py`: Autopilot-System

## Tipps für die Simulation

1. Der Autopilot kann automatisch zwischen verschiedenen Planeten navigieren.
2. Verwende die Tasten 1-4, um ein bestimmtes Ziel auszuwählen.
3. Die grüne Markierung zeigt das aktuelle Ziel des Autopiloten an.
4. Bei Meteoritenschauern führt der Autopilot automatisch Ausweichmanöver durch.
5. Das UI zeigt den aktuellen Status des Autopiloten und viele nützliche Informationen an.
6. Die Rakete verbraucht Treibstoff, achte auf die Treibstoffanzeige.

## Erweiterungsmöglichkeiten

- 3D-Darstellung
- Detailliertere Raketenmodelle mit mehreren Stufen
- Atmosphärische Physik (Wiedereintritt, Luftwiderstand)
- Missionsplaner mit vordefinierten Zielen
- Mehrspieler-Unterstützung
- VR-Integration 