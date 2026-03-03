🧪 96-Well Plate Multi-Round Data Entry & Clustering GUI
  A Python desktop application for managing, tracking, and analyzing multi-round 96-well plate experiments.
  Designed for synthetic biology, microbiology, fluorescence plate reader experiments, and iterative screening workflows.

🚀 What This Tool Does
  Provides an interactive 8×12 (96-well) plate interface
  Tracks Promoter, AHL concentration, OD, and RFU
  Supports unlimited experimental rounds
  Automatically saves each round as a timestamped CSV
  Visualizes OD/RFU across rounds
  Performs feature-based clustering of wells

🖼 Interface Overview
  Click any well (A1–H12) to enter data
  Press Enter to save and move to the next well
  Start new rounds with one click
  Plot selected wells individually or as clustered groups

✨ Features
  Interactive 96-Well Plate
  8 rows (A–H), 12 columns (1–12)
  Visual button feedback on selection
  Hover-to-identify wells

📝 Structured Well Metadata

  Each well stores:
  Promoter (locked after Round 1)
  AHL concentration (locked after Round 1)
  OD (per round)
  RFU (per round)

🔁 Multi-Round Tracking
  Click Start New Round
  Automatically saves previous round
  Clears OD/RFU for new measurements
  Maintains full OD/RFU time-series per well

Internal structure example:
well_history = {
    "A1": {
        "promoter": "pLux",
        "ahl": "10nM",
        "od": [0.21, 0.35, 0.52],
        "rfu": [120, 300, 540]
    }
}
💾 Automatic CSV Export

Each round saves as:
  plate_data_round_<round_number>_<timestamp>.csv

  Format:
		
📊 Plotting Options

1️⃣ Standard Plot
  Dual-axis visualization
  OD (left axis)
  RFU (right axis)
  Multiple wells overlaid
  Separate legend window

2️⃣ Clustered Plot

  Cluster wells by signal similarity using:
  Selected signals:
    OD
    RFU
  Signal features:
    Total
    Peak
    Ending
  Optional categorical features:
    Promoter
    AHL concentration
    Clustering modes:
    Automatic
    Manual (specify number of clusters)
  Cluster means are plotted as representative curves.

🧠 Clustering Engine
  Requires a companion file:
    cluster_plate.py
  Expected functions:
    build_feature_matrix()

cluster_signal()

build_cluster_map()

Clustering supports feature extraction and grouping of wells based on signal dynamics.

⚙️ Configuration
Development Mode (Load Existing CSVs)
DEV_MODE = True
CSV_FOLDER = "plate_test_rounds_native"

When enabled:
Loads all .csv files from the folder
Reconstructs well history
Continues round numbering
Change Plate Size
rows = 8
columns = 12

The UI, CSV export, and selection interface update automatically.

📦 Requirements

Python 3.8+
Install dependencies:

pip install matplotlib numpy

Uses: tkinter, matplotlib, numpy, csv, datetime, os

📁 Project Structure
project/
│
├── main_script.py
├── cluster_plate.py
├── Ecoli.png
└── plate_test_rounds_native/   (optional)
▶️ Running the Program
python main_script.py

The timer begins automatically on launch.

🎯 Example Use Cases

Promoter strength characterization
AHL titration curves
Multi-round optimization experiments
Fluorescence response profiling
Signal-shape based phenotype clustering

🛠 Future Improvements

Heatmap plate visualization
RFU/OD normalization toggle
Export plots to PNG/PDF
Direct plate reader file import
Save/load complete experiment session

📜 License

Add your preferred license (MIT recommended for academic tools).

👨‍🔬 Intended Audience

Researchers who need:
Flexible plotting
Cluster-based analysis of plate data
A version formatted for publication supplement

A version tailored for a synthetic biology portfolio
