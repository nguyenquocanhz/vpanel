"""
VPS Panel - Temperature Monitor
Reads CPU and hardware temperature sensors.
"""

import psutil
import os


def get_temperatures() -> dict:
    """Get all available temperature sensor readings."""
    temps = {}

    try:
        sensor_temps = psutil.sensors_temperatures()
        if sensor_temps:
            for name, entries in sensor_temps.items():
                temps[name] = []
                for entry in entries:
                    temps[name].append({
                        "label": entry.label or f"Sensor {len(temps[name])}",
                        "current": round(entry.current, 1),
                        "high": round(entry.high, 1) if entry.high else None,
                        "critical": round(entry.critical, 1) if entry.critical else None,
                    })
    except (AttributeError, OSError):
        # psutil.sensors_temperatures() not available on this platform
        pass

    # Fallback: read from sysfs thermal zones
    if not temps:
        temps = _read_thermal_zones()

    return temps


def _read_thermal_zones() -> dict:
    """Fallback: Read temperature from /sys/class/thermal/."""
    zones = {}
    thermal_base = "/sys/class/thermal"

    if not os.path.exists(thermal_base):
        return zones

    try:
        for zone_dir in sorted(os.listdir(thermal_base)):
            if not zone_dir.startswith("thermal_zone"):
                continue

            zone_path = os.path.join(thermal_base, zone_dir)
            temp_file = os.path.join(zone_path, "temp")
            type_file = os.path.join(zone_path, "type")

            if not os.path.exists(temp_file):
                continue

            try:
                with open(temp_file, "r") as f:
                    temp_mc = int(f.read().strip())
                temp_c = round(temp_mc / 1000, 1)

                zone_type = "unknown"
                if os.path.exists(type_file):
                    with open(type_file, "r") as f:
                        zone_type = f.read().strip()

                if zone_type not in zones:
                    zones[zone_type] = []

                zones[zone_type].append({
                    "label": zone_dir,
                    "current": temp_c,
                    "high": None,
                    "critical": None,
                })
            except (IOError, ValueError):
                continue
    except OSError:
        pass

    return zones


def get_cpu_temperature() -> float:
    """Get the primary CPU temperature. Returns 0 if unavailable."""
    temps = get_temperatures()

    # Try common sensor names
    for name in ["coretemp", "k10temp", "cpu_thermal", "cpu-thermal", "x86_pkg_temp"]:
        if name in temps and temps[name]:
            return temps[name][0]["current"]

    # Try any available sensor
    for name, entries in temps.items():
        if entries:
            return entries[0]["current"]

    return 0.0


def get_temp_status(temp: float) -> str:
    """Determine temperature status based on thresholds."""
    if temp <= 0:
        return "unknown"
    elif temp < 60:
        return "normal"
    elif temp < 75:
        return "warm"
    elif temp < 85:
        return "warning"
    else:
        return "critical"


def get_full_temperature_data() -> dict:
    """Get comprehensive temperature data for dashboard."""
    cpu_temp = get_cpu_temperature()
    return {
        "sensors": get_temperatures(),
        "cpu_temp": cpu_temp,
        "status": get_temp_status(cpu_temp),
    }
