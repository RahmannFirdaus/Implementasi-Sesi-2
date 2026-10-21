# 🏛️ Campus Energy HPC Co-Simulation

## Co-Simulation Efisiensi Energi Gedung Kampus Berbasis HPC
*EnergyPlus + Agent-Based Modeling*

---

## 📋 Deskripsi

Proyek ini mengimplementasikan **co-simulation** untuk menganalisis dan mengoptimalkan konsumsi energi gedung kampus. Pendekatan yang digunakan menggabungkan:

1. **EnergyPlus Wrapper** - Model fisik gedung yang menghitung beban termal dan konsumsi HVAC berdasarkan data cuaca lokal.
2. **Agent-Based Model (ABM)** - Simulasi perilaku penghuni gedung dan kepatuhan terhadap kebijakan energi.

Kedua model dijalankan di **kluster HPC** menggunakan **SLURM** job scheduler untuk menguji berbagai skenario kebijakan penghematan listrik.

## 🚀 Cara Menjalankan

### Lokal (tanpa HPC)

```bash
# Jalankan simulasi ABM
python src/abm_simulation.py data/policy_config.json

# Jalankan EnergyPlus Wrapper
python src/energyplus_wrapper.py data/building_model.epw data/policy_config.json
```

### Di Kluster HPC (SLURM)

```bash
# Submit job ke antrian SLURM
sbatch hpc_jobs/submit_job.sh

# Monitor status job
squeue -u $USER

# Lihat output
cat logs/sim_<JOB_ID>.out
```

## ⚙️ Konfigurasi Kebijakan

Edit file `data/policy_config.json` untuk mengubah parameter simulasi:

| Parameter | Deskripsi | Default |
|---|---|---|
| `min_ac_temp` | Suhu minimum AC (°C) | 25 |
| `num_agents` | Jumlah penghuni yang disimulasikan | 200 |
| `simulation_days` | Durasi simulasi (hari) | 30 |
| `restricted_zones` | Zona dengan aturan pendinginan khusus | Lab Bio, Server Room |

## 📊 Skenario Kebijakan

- **Baseline**: AC diatur bebas → `min_ac_temp: 20`
- **Kebijakan Hemat**: AC minimum 25°C → `min_ac_temp: 25`
- **Kebijakan Ketat**: AC minimum 27°C → `min_ac_temp: 27`

## 📚 Referensi

- US Department of Energy - [EnergyPlus](https://energyplus.net/)
- SLURM Workload Manager - [Documentation](https://slurm.schedmd.com/)
