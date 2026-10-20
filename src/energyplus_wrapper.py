"""
EnergyPlus Wrapper - Integrator Model Fisik Gedung
===================================================
Modul ini berfungsi sebagai wrapper/integrator antara simulator
EnergyPlus (model termal gedung) dengan Agent-Based Model (ABM).

Pada implementasi penuh, modul ini memanggil EnergyPlus via API
atau subprocess untuk mensimulasikan beban termal gedung berdasarkan:
  - Data cuaca lokal (file .epw)
  - Konfigurasi zona termal gedung
  - Jadwal operasional (schedules)

Hasil simulasi EnergyPlus kemudian dikombinasikan dengan output ABM
untuk menghasilkan estimasi konsumsi energi yang lebih akurat.
"""

import csv
import os
import json


def parse_epw_weather(epw_path):
    """
    Mem-parsing file EPW (EnergyPlus Weather) untuk mengambil data cuaca.

    Parameters
    ----------
    epw_path : str
        Path ke file .epw

    Returns
    -------
    list[dict]
        Daftar record cuaca per jam.
    """
    weather_data = []
    with open(epw_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            parts = line.split(',')
            # Skip header lines (non-numeric first field)
            if len(parts) >= 8 and parts[0].isdigit():
                record = {
                    'year': int(parts[0]),
                    'month': int(parts[1]),
                    'day': int(parts[2]),
                    'hour': int(parts[3]),
                    'dry_bulb_temp': float(parts[4]),
                    'rel_humidity': float(parts[5]),
                    'wind_speed': float(parts[6]),
                    'solar_radiation': float(parts[7])
                }
                weather_data.append(record)
    return weather_data


def calculate_cooling_load(outdoor_temp, indoor_target_temp, floor_area_m2=500):
    """
    Menghitung estimasi beban pendinginan (cooling load) sederhana.

    Parameters
    ----------
    outdoor_temp : float
        Suhu udara luar (°C).
    indoor_target_temp : float
        Suhu target ruangan (°C).
    floor_area_m2 : float
        Luas lantai gedung (m²).

    Returns
    -------
    float
        Estimasi cooling load dalam kW.
    """
    delta_t = max(0, outdoor_temp - indoor_target_temp)
    # Koefisien transfer panas sederhana (W/m²·K)
    u_value = 2.5
    cooling_load_w = u_value * floor_area_m2 * delta_t
    return cooling_load_w / 1000  # Convert to kW


def estimate_hvac_energy(weather_data, target_temp=25, cop=3.0, floor_area_m2=500):
    """
    Mengestimasi konsumsi energi HVAC berdasarkan data cuaca dan target suhu.

    Parameters
    ----------
    weather_data : list[dict]
        Data cuaca per jam dari parse_epw_weather().
    target_temp : float
        Suhu target pendinginan (°C).
    cop : float
        Coefficient of Performance sistem AC.
    floor_area_m2 : float
        Luas lantai gedung (m²).

    Returns
    -------
    float
        Total konsumsi energi HVAC (kWh).
    """
    total_energy_kwh = 0.0

    for record in weather_data:
        cooling_load_kw = calculate_cooling_load(
            outdoor_temp=record['dry_bulb_temp'],
            indoor_target_temp=target_temp,
            floor_area_m2=floor_area_m2
        )
        # Energi listrik = cooling load / COP (per jam = kWh)
        electrical_kwh = cooling_load_kw / cop
        total_energy_kwh += electrical_kwh

    return total_energy_kwh


def run_cosimulation(epw_path, policy_path):
    """
    Menjalankan co-simulation antara model fisik gedung dan kebijakan energi.

    Parameters
    ----------
    epw_path : str
        Path ke file cuaca EPW.
    policy_path : str
        Path ke file kebijakan JSON.

    Returns
    -------
    dict
        Hasil ringkasan co-simulation.
    """
    # Load policy
    with open(policy_path, 'r') as f:
        policy = json.load(f)

    target_temp = policy['min_ac_temp']

    # Parse weather data
    weather_data = parse_epw_weather(epw_path)

    if not weather_data:
        print("[WARNING] No weather data parsed. Check EPW file format.")
        return {'hvac_energy_kwh': 0.0}

    # Estimate HVAC energy
    hvac_energy = estimate_hvac_energy(weather_data, target_temp=target_temp)

    # Account for restricted zones (always-on cooling)
    restricted_extra = 0.0
    for zone in policy.get('restricted_zones', []):
        # Restricted zones run 24h with lower temp target
        zone_load = calculate_cooling_load(
            outdoor_temp=30.0,  # Average assumption
            indoor_target_temp=zone['max_temp'],
            floor_area_m2=50   # Smaller zone area
        )
        restricted_extra += zone_load * 24 * policy['simulation_days'] / 3.0

    results = {
        'hvac_energy_kwh': hvac_energy,
        'restricted_zones_kwh': restricted_extra,
        'total_building_kwh': hvac_energy + restricted_extra,
        'target_temp': target_temp,
        'weather_records': len(weather_data)
    }

    return results


if __name__ == "__main__":
    import sys

    epw_file = sys.argv[1] if len(sys.argv) > 1 else "data/building_model.epw"
    policy_file = sys.argv[2] if len(sys.argv) > 2 else "data/policy_config.json"

    print("=" * 60)
    print("=== EnergyPlus Wrapper: Building Thermal Simulation ===")
    print("=" * 60)

    results = run_cosimulation(epw_file, policy_file)

    print(f"Weather records processed : {results['weather_records']}")
    print(f"Target indoor temperature : {results['target_temp']}°C")
    print(f"HVAC energy consumption   : {results['hvac_energy_kwh']:.2f} kWh")
    print(f"Restricted zones energy   : {results['restricted_zones_kwh']:.2f} kWh")
    print(f"Total building energy     : {results['total_building_kwh']:.2f} kWh")
    print("=" * 60)
