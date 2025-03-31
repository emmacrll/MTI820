import pandas as pd

# Charger les données brutes
df = pd.read_csv("bixi_deplacements_2022_2025.csv")

# Nettoyer les nombres avec des espaces ou caractères spéciaux
for col in ["deplacements_membre", "deplacements_occasionnel"]:
    df[col] = df[col].astype(str).str.replace(r"[^\d]", "", regex=True).astype(int)

# Créer une colonne total
df["total_deplacements"] = df["deplacements_membre"] + df["deplacements_occasionnel"]

# Optionnel : Trier les mois dans l’ordre chronologique
mois_ordre = ["janvier", "février", "mars", "avril", "mai", "juin",
              "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
df["mois"] = pd.Categorical(df["mois"], categories=mois_ordre, ordered=True)
df = df.sort_values(by=["année", "mois"])

# Sauvegarder le fichier nettoyé
df.to_csv("bixi_deplacements_nettoye.csv", index=False)
print("✅ Données nettoyées et sauvegardées dans bixi_deplacements_nettoye.csv")
