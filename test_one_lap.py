
import fastf1
import matplotlib.pyplot as plt

# activar cache
fastf1.Cache.enable_cache('data/raw')

# cargar sesión
session = fastf1.get_session(2025, 1, 'R')
session.load()

print("Session:", session.event['EventName'])

# obtener laps
laps = session.laps
print("Total laps:", len(laps))

# seleccionar una vuelta
lap = laps.iloc[10]

print("Driver:", lap['Driver'])
print("LapNumber:", lap['LapNumber'])

# telemetría
tel = lap.get_car_data().add_distance()

print(tel.head())

# plot
plt.plot(tel['Distance'], tel['Speed'])
plt.xlabel("Distance")
plt.ylabel("Speed")
plt.title("1 Lap Speed Profile")
plt.show()