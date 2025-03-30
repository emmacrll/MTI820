import pandas as pd

# === 1. Charger le fichier qualité de l'air ===
df = pd.read_csv("qualite de air/rsqa-indice-qualite-air-2022-2024.csv")

# === 2. Convertir la colonne 'date' en datetime
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# === 3. Garder seulement les données de 2023
df = df[df['date'].dt.year == 2023]

# === 4. Supprimer la colonne 'heure' si elle existe
if 'heure' in df.columns:
    df = df.drop(columns=['heure'])

# === 5. Supprimer les lignes incomplètes
df = df.dropna(subset=['stationId', 'polluant', 'valeur', 'date'])

# === 6. Sauvegarder dans un nouveau fichier propre
df.to_csv("qualite de air/rsqa_air_montreal_2023_nettoye.csv", index=False)

print("✅ Fichier nettoyé pour 2023 enregistré ici : 'qualite de air/rsqa_air_montreal_2023_nettoye.csv'")
