#!/bin/bash
#SBATCH --job-name=energy_abm_sim
#SBATCH --output=logs/sim_%j.out
#SBATCH --error=logs/sim_%j.err
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --time=01:00:00
#SBATCH --partition=normal

# ============================================================
# HPC SLURM Job Script: Co-Simulation Efisiensi Energi Kampus
# ============================================================
# Skrip ini mengalokasikan 2 node dengan 4 task/node untuk
# menjalankan simulasi ABM + EnergyPlus wrapper secara paralel.
# ============================================================

# Load modul Python / Environment pada kluster HPC
module load python/3.10

# Pindah ke direktori kerja proyek
cd $SLURM_SUBMIT_DIR

# Buat direktori logs jika belum ada
mkdir -p logs

echo "============================================================"
echo "Job started on $(hostname) at $(date)"
echo "SLURM Job ID: $SLURM_JOB_ID"
echo "Nodes allocated: $SLURM_JOB_NODELIST"
echo "============================================================"

# Step 1: Jalankan simulasi model fisik gedung (EnergyPlus Wrapper)
echo "[Step 1] Running EnergyPlus Building Thermal Simulation..."
python3 src/energyplus_wrapper.py data/building_model.epw data/policy_config.json

# Step 2: Jalankan simulasi Agent-Based Model
echo "[Step 2] Running Agent-Based Model Simulation..."
python3 src/abm_simulation.py data/policy_config.json

echo "============================================================"
echo "Job completed successfully on $(hostname) at $(date)"
echo "============================================================"
