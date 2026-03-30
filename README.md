# 🏎️ ai_f1: Predictive Modeling of High-Frequency F1 Telemetry

Objectives: 
1. Classify the circuit and the driver
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
```
uv run src/get_data.py
```

> [!WARNING]  
> servers only allow **500 requests/hour**! the script will **intetionally pause/fail** around Round 10. If you see `"API Rate Limit Reached"` message, wait approx 60 minutes and run the above command again. You might need to run the script in 2-3 batches. Make sure you have 4-5 GB of free disk space! FOR NOW ONLY RUN IT ONCE TO TEST IF ITS WORKING!!!!!!!!!


### Step 4: test notebooks
1. open `notebooks/info_tables_available.ipynb`
2. in the top right corner click **Select Kernel -> Python Environments** and selected the one named `ai-f1` from `.venv/bin/python`
3. run all the cells; you should see all the available tables there

### Step 5 optional: visualize data in a better way
1. if you are using VSCODE, install **Data Wrangler** extension (the one from microsoft)
2. after running all the cells, at the top of the file click on  **View data** and open one of the existing workspace tables to visualize the data 

## Available Tables:
- **Laps**: 'Time', 'Driver', 'DriverNumber', 'LapTime', 'LapNumber', 'Stint', 'PitOutTime', 'PitInTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'Sector1SessionTime', 'Sector2SessionTime', 'Sector3SessionTime', 'SpeedI1', 'SpeedI2', 'SpeedFL', 'SpeedST', 'IsPersonalBest', 'Compound', 'TyreLife', 'FreshTyre', 'Team', 'LapStartTime', 'LapStartDate', 'TrackStatus', 'Position', 'Deleted', 'DeletedReason', 'FastF1Generated', 'IsAccurate'
- **Car Telemetry**: 'Date', 'RPM', 'Speed', 'nGear', 'Throttle', 'Brake', 'DRS', 'Source', 'Time', 'SessionTime', 'Distance'
- **GPS Position**: 'Date', 'Status', 'X', 'Y', 'Z', 'Source', 'Time', 'SessionTime'
- **Weather**: 'Time', 'AirTemp', 'Humidity', 'Pressure', 'Rainfall', 'TrackTemp', 'WindDirection', 'WindSpeed'
- **Track Status**: 'Time', 'Status', 'Message'
- **Race Control Messages**: 'Time', 'Category', 'Message', 'Status', 'Flag', 'Scope', 'Sector', 'RacingNumber', 'Lap'


## OBJECTIVE 1: Classify the circuit and the driver

1. **Filter Bad Laps:** Use **Track Status**, **Race Control Messages**, and the `IsAccurate` column to drop laps affected by Safety 2. **Contextual Join:** Join **Weather** data to the **Laps** table based on the closest `SessionTime` to capture track conditions.
3. **Telemetry Extraction:** For every valid lap, extract the corresponding high-frequency **Car Telemetry** array.
4. **Spatial Interpolation:** Resample the telemetry arrays over a uniform Distance grid (e.g., one data point every 5 meters) so that every lap vector has the exact same shape for the ML model.

> [!CAUTION]
> 1. COLUMNS TO DROP!
> - **Absolute Timestamps**: `Date, Time, SessionTime, LapStartTime, LapStartDate, PitOutTime, PitInTime`
> - **Direct Identifiers**: `Driver, DriverNumber, Team`
> - **GPS Data**: `X, Y, Z`
> - **Redundant Information**: `SpeedI1, SpeedI2, SpeedFL, SpeedST, FreshTyre`: they are already part of `Speed` or `TyreLife`
> - **System Metadata**: `FastF1Generated, IsAccurate, Deleted, DeletedReason`: irrelevant, we already use `IsAccurate` & `Deleted` to filter out bad laps
> - **Biased Flags**: `IsPersonalBest`: massive bias; someone's worst lap can be faster than another driver's best lap
> 
> 2. COLUMNS TO KEEP! ?? need more reasoning here
> - **Laps (Macro Features)**: `LapTime (converted to total seconds), Sector1Time, Sector2Time, Sector3Time, Compound (e.g., Soft/Medium/Hard), TyreLife, Stint`
> - **Car Telemetry (Micro Features)**: `Speed, RPM, nGear, Throttle, Brake, DRS`
> - **Weather**: `TrackTemp, AirTemp`
