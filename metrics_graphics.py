import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Загружаем файл
file_path = "mot_experiment_results.xlsx"
df = pd.read_excel(file_path)

trackers = df['Tracker'].unique()

# Переводы на русский
weather_map = {
    'Clear': 'Ясно',
    'Fog': 'Туман',
    'Rain': 'Дождь',
    'Heavy rain': 'Сильный дождь',
    'Snow': 'Снег'
}
traffic_map = {
    'Low': 'Низкий',
    'Medium': 'Средний',
    'High': 'Высокий'
}
lighting_map = {
    'Day': 'День',
    'Night': 'Ночь',
    'Low light': 'Плохое освещение'
}

# ===== Графики погода =====
weather_order = ['Clear', 'Fog', 'Rain', 'Heavy rain', 'Snow']
weather_labels = [weather_map[w] for w in weather_order]
df_weather = df[df['Weather'].isin(weather_order)]

for metric in ['MOTA', 'IDF1']:
    plt.figure(figsize=(10,6))
    width = 0.15
    x = np.arange(len(weather_order))
    for i, tracker in enumerate(trackers):
        means = (
            df_weather[df_weather['Tracker'] == tracker]
            .groupby('Weather')[metric]
            .mean()
            .reindex(weather_order)
        )
        plt.bar(x + i*width, means, width=width, label=tracker)
    plt.title(f'{metric} при различных погодных условиях')
    plt.ylabel(metric)
    plt.xticks(x + width*(len(trackers)-1)/2, weather_labels, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.show()

# ===== График трафик =====
traffic_order = ['Low', 'Medium', 'High']
traffic_labels = [traffic_map[t] for t in traffic_order]

plt.figure(figsize=(8,6))
width = 0.15
x = np.arange(len(traffic_order))
for i, tracker in enumerate(trackers):
    means = (
        df[df['Tracker'] == tracker]
        .groupby('Traffic')['MOTA']
        .mean()
        .reindex(traffic_order)
    )
    plt.bar(x + i*width, means, width=width, label=tracker)
plt.title('MOTA при различных уровнях трафика')
plt.ylabel('MOTA')
plt.xticks(x + width*(len(trackers)-1)/2, traffic_labels)
plt.legend()
plt.tight_layout()
plt.show()

# ===== График освещение =====
lighting_order = ['Day', 'Night', 'Low light']
lighting_labels = [lighting_map[l] for l in lighting_order]
df_light = df[df['Lighting'].isin(lighting_order)]

plt.figure(figsize=(8,6))
width = 0.1
x = np.arange(len(lighting_order))
for i, tracker in enumerate(trackers):
    means = (
        df_light[df_light['Tracker'] == tracker]
        .groupby('Lighting')['MOTA']
        .mean()
        .reindex(lighting_order)
    )
    plt.bar(x + i*width, means, width=width, label=tracker)
plt.title('MOTA при различных условиях освещения')
plt.ylabel('MOTA')
plt.xticks(x + width*(len(trackers)-1)/2, lighting_labels)
plt.legend()
plt.tight_layout()
plt.show()
