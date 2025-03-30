import pandas as pd
import os
import glob

input_folder = "METEO MONTREAL"
output_folder = "METEO_NETTOYE"
os.makedirs(output_folder, exist_ok=True)

# Mots-clés pour repérer les colonnes
mots_cles = [
    "temp", "rosée", "hum. rel", "précip", "vent (km/h)", "pression"
]

weather_files = glob.glob(os.path.join(input_folder, "*.csv"))

for file_path in weather_files:
    try:
        df = pd.read_csv(file_path, encoding="ISO-8859-1")
        colonnes_trouvees = []

        for col in df.columns:
            col_clean = col.lower().replace("√", "").replace("¬", "").replace("©", "").strip()
            if any(mot in col_clean for mot in mots_cles):
                colonnes_trouvees.append(col)

        if not colonnes_trouvees:
            raise ValueError("Aucune colonne cible détectée.")

        df_filtré = df[colonnes_trouvees].copy()

        # Conversion des valeurs vers float
        for col in df_filtré.columns:
            df_filtré[col] = pd.to_numeric(df_filtré[col].astype(str).str.replace(",", "."), errors="coerce")

        # Remplir les NaN avec moyenne
        df_filtré = df_filtré.fillna(df_filtré.mean(numeric_only=True))

        # Sauvegarder
        out_path = os.path.join(output_folder, os.path.basename(file_path))
        df_filtré.to_csv(out_path, index=False)
        print(f"✅ Fichier nettoyé : {os.path.basename(file_path)} | Colonnes : {list(df_filtré.columns)}")

    except Exception as e:
        print(f"❌ Erreur dans {file_path} : {e}")
