import pandas as pd
import glob
import os
import seaborn as sns
import matplotlib.pyplot as plt

# === 1. Charger les fichiers météo nettoyés ===
weather_files = glob.glob("METEO_NETTOYE/*.csv")
weather_monthly = []

for f in weather_files:
    try:
        df = pd.read_csv(f)
        df["mois"] = os.path.splitext(os.path.basename(f))[0].lower()
        weather_monthly.append(df)
    except Exception as e:
        print(f"⚠️ Erreur dans le fichier {f} : {e}")

if not weather_monthly:
    raise ValueError("Aucun fichier météo chargé.")

df_meteo = pd.concat(weather_monthly, ignore_index=True)

# === ✅ Harmonisation des noms de colonnes météo ===
df_meteo = df_meteo.rename(columns={
    "Temp": "Temp (°C)",
    "Point de rosée": "Point de rosée (°C)",
    "Pression de la station (kPa)": "Pression à la station (kPa)"
})

# === ✅ Forcer les colonnes météo à être numériques ===
colonnes_meteo = [
    "Temp (°C)", "Point de rosée (°C)", "Hum. rel (%)",
    "Hauteur de précip. (mm)", "Vit. du vent (km/h)",
    "Pression à la station (kPa)"
]
for col in colonnes_meteo:
    if col in df_meteo.columns:
        df_meteo[col] = pd.to_numeric(df_meteo[col], errors="coerce")

# === ✅ Moyenne météo mensuelle comme pour la pollution
colonnes_meteo_presente = [col for col in colonnes_meteo if col in df_meteo.columns]
df_meteo_filtré = df_meteo[["mois"] + colonnes_meteo_presente]
df_meteo_avg = df_meteo_filtré.groupby("mois")[colonnes_meteo_presente].mean().reset_index()

# === 2. Charger activité sportive + santé mentale
df_sport = pd.read_csv("activité sportive/Activit__physique_mensuelle_simul_e_-_Qu_bec_2023.csv")
df_sante = pd.read_csv("Sant__mentale_simul_e_-_Qu_bec_2023.csv")

# === 3. Fusion sport + santé + météo
df = df_sport.merge(df_sante, on="mois").merge(df_meteo_avg, on="mois")

# === 4. Encodage qualitatif
stress_map = {"faible": 1, "modéré": 2, "élevé": 3}
bien_etre_map = {"faible": 1, "moyen": 2, "bon": 3}
df["stress_score"] = df["niveau_stress_dominant"].map(stress_map)
df["bien_etre_score"] = df["niveau_bien_etre_dominant"].map(bien_etre_map)

# === 5. Charger et préparer la pollution
df_pollution = pd.read_csv("qualite de air/rsqa_air_montreal_2023_nettoye.csv")
df_pollution["valeur"] = pd.to_numeric(df_pollution["valeur"], errors="coerce")
df_pollution["date"] = pd.to_datetime(df_pollution["date"], errors='coerce')
df_pollution["mois"] = df_pollution["date"].dt.month_name().str.lower()

mois_en_fr = {
    "january": "janvier", "february": "février", "march": "mars",
    "april": "avril", "may": "mai", "june": "juin",
    "july": "juillet", "august": "août", "september": "septembre",
    "october": "octobre", "november": "novembre", "december": "décembre"
}
df_pollution["mois"] = df_pollution["mois"].map(mois_en_fr)

# === 6. Moyenne mensuelle pollution
df_pollution_grouped = df_pollution.groupby(["mois", "polluant"])["valeur"].mean().reset_index()
df_pollution_pivot = df_pollution_grouped.pivot(index="mois", columns="polluant", values="valeur").reset_index()

# === 7. Fusion pollution avec le dataset principal
df = df.merge(df_pollution_pivot, on="mois", how="left")

# === 8. Sélection des colonnes pour la corrélation
selected_columns = [
    "nb_moyen_sportifs_par_jour",
    "duree_moyenne_minutes",
    "stress_score",
    "bien_etre_score",
    "Temp (°C)",
    "Point de rosée (°C)",
    "Hum. rel (%)",
    "Hauteur de précip. (mm)",
    "Vit. du vent (km/h)",
    "Pression à la station (kPa)",
    "PM", "NO2", "O3", "CO", "SO2"
]
selected_columns = [col for col in selected_columns if col in df.columns]
df_corr = df[selected_columns]

# === 9. Matrice de corrélation
corr_matrix = df_corr.corr()

# === 10. Corrélations fortes uniquement
corr_pairs = corr_matrix.unstack().reset_index()
corr_pairs.columns = ['Variable 1', 'Variable 2', 'Corrélation']
corr_strong = corr_pairs[
    (corr_pairs['Variable 1'] != corr_pairs['Variable 2']) &
    (corr_pairs['Corrélation'].abs() >= 0.5)
].drop_duplicates(subset=['Corrélation'])
corr_strong = corr_strong.reindex(corr_strong["Corrélation"].abs().sort_values(ascending=False).index)

# === 11. Affichage
print("\n📋 Vérification du nombre de valeurs non-nulles dans les colonnes météo et pollution :\n")
print(df_corr.notna().sum())

print("\n📊 Moyennes météo mensuelles :")
print(df_meteo_avg.head(12))

print("\n✅ Corrélations fortes détectées (|ρ| ≥ 0.5) :\n")
print(corr_strong)

# === 12. Heatmap
plt.figure(figsize=(14, 9))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Corrélations : Activité physique, Météo, Pollution et Santé mentale - Québec 2023")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()
