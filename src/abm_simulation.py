"""
Agent-Based Model (ABM) Simulation - Konsumsi Energi Gedung Kampus
==================================================================
Mensimulasikan kepatuhan penghuni gedung terhadap kebijakan energi
serta dampaknya pada estimasi konsumsi daya listrik.

Bagian dari Co-Simulation: EnergyPlus + ABM pada kluster HPC.
"""

import json
import random
import sys


def load_policy(config_path):
    """Memuat konfigurasi kebijakan energi dari file JSON."""
    with open(config_path, 'r') as f:
        return json.load(f)


def run_agent_simulation(num_agents, days, min_ac_temp):
    """
    Menjalankan simulasi agen untuk mengestimasi konsumsi energi harian.

    Parameters
    ----------
    num_agents : int
        Jumlah agen (penghuni gedung) yang disimulasikan.
    days : int
        Jumlah hari simulasi.
    min_ac_temp : float
        Suhu minimum AC sesuai kebijakan (°C).

    Returns
    -------
    float
        Total konsumsi energi selama periode simulasi (kWh).
    """
    total_energy_kwh = 0.0

    for day in range(1, days + 1):
        daily_kwh = 0.0
        for agent in range(num_agents):
            # Simulasi durasi kehadiran agen dalam jam (4-10 jam)
            presence_hours = random.uniform(4, 10)

            # Pengaruh kebijakan suhu AC (makin dingin = daya makin tinggi)
            # Jika suhu minimum >= 25°C → faktor normal (1.0)
            # Jika suhu minimum < 25°C  → konsumsi naik 35% (1.35)
            ac_factor = 1.0 if min_ac_temp >= 25 else 1.35

            # Konsumsi energi dasar per agen (kWh)
            agent_consumption = presence_hours * 0.45 * ac_factor
            daily_kwh += agent_consumption

        total_energy_kwh += daily_kwh
        print(f"[Day {day:>3}] Daily Consumption: {daily_kwh:>10.2f} kWh")

    return total_energy_kwh


if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv) > 1 else "data/policy_config.json"
    policy = load_policy(config_file)

    print("=" * 60)
    print("=== Starting HPC Co-Simulation: Agent-Based Model ===")
    print("=" * 60)
    print(f"Building       : {policy.get('building_name', 'N/A')}")
    print(f"Policy AC Temp : {policy['min_ac_temp']}°C (minimum)")
    print(f"Num Agents     : {policy['num_agents']}")
    print(f"Sim Duration   : {policy['simulation_days']} days")
    print("-" * 60)

    total = run_agent_simulation(
        num_agents=policy['num_agents'],
        days=policy['simulation_days'],
        min_ac_temp=policy['min_ac_temp']
    )

    print("-" * 60)
    print(f"Total Simulated Energy Consumption: {total:.2f} kWh")
    avg_daily = total / policy['simulation_days']
    print(f"Average Daily Consumption         : {avg_daily:.2f} kWh")
    print(f"Average per Agent per Day         : {avg_daily / policy['num_agents']:.2f} kWh")
    print("=" * 60)
