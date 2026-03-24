# 🏎️ ai_f1: Predictive Modeling of High-Frequency F1 Telemetry

Objectives: 
1. Classify the circuit based on macro-telemetry
2. Predict the tire compound based on corner-exit acceleration (or other information)
3. Predict the teammate (e.g., Norris vs. Piastri) based on their micro-telemtry

## Setup

### Step 1: Install `uv` 

follow the tutorial from:

https://docs.astral.sh/uv/getting-started/installation/

### Step 2: setup the project 
choose where you want to clone the project:
```
git clone git@github.com:cristianooo1/ai_f1.git
cd ai_f1
uv sync
```

### Step 3: get the data
from the root of the folder `/path_to/ai_f1` run:
It might take up to 2 minutes for the data to be downloaded into the `/data/raw` folder.

```
uv run src/get_data.py
```

### Step 4: test notebooks
1. open `notebooks/01_circuit_driver.ipynb`
2. in the top right corner click **Select Kernel -> Python Environments** and selected the one named `ai-f1` from `.venv/bin/python`
3. run all the cells; at the bottom there should be displayed a plot comparing the speeds of 2 drivers!!