import streamlit as st
import pandas as pd
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Prédiction Prix BTP Cameroun", page_icon="🏗️", layout="centered")

st.title("🏗️ Application BTP - Simulateur & Prédiction")
st.markdown("Sélectionnez un matériau, ajustez ses prix historiques, et observez la prédiction à 6 mois en temps réel.")

# 1. Base de données complète pour plusieurs matériaux (Yaoundé)
@st.cache_data
def charger_donnees():
    return pd.DataFrame({
        'Date': ['2025-01-01', '2025-02-01', '2025-03-01', '2025-04-01', '2025-05-01', '2025-06-01'] * 3,
        'Materiaux': ['Ciment (sac 50kg)'] * 6 + ['Acier à béton (tonne)'] * 6 + ['Bitume (tonne)'] * 6,
        'Prix_FCFA': [
            4500, 4550, 4600, 4650, 4700, 4750,  # Ciment
            450000, 455000, 460000, 465000, 470000, 475000,  # Acier
            650000, 655000, 660000, 665000, 670000, 675000   # Bitume
        ]
    })

df_global = charger_donnees()

# 2. Barre latérale : Choix du matériau et filtres de simulation
st.sidebar.header("⚙️ Paramètres de Simulation")

# Choix du matériau par l'utilisateur
liste_materiaux = df_global['Materiaux'].unique()
materiau_choisi = st.sidebar.selectbox("Choisissez un matériau :", liste_materiaux)

# Filtrer les données selon le matériau sélectionné
df_materiau = df_global[df_global['Materiaux'] == materiau_choisi].copy()

st.sidebar.markdown("---")
st.sidebar.subheader("Modifier les prix historiques (FCFA)")

# Création dynamique de curseurs ou champs pour modifier chaque mois
prix_modifies = []
for index, row in df_materiau.iterrows():
    nouveau_prix = st.sidebar.number_input(
        f"{row['Date']}", 
        min_value=100, 
        max_value=2000000, 
        value=int(row['Prix_FCFA']),
        step=100 if "Ciment" in materiau_choisi else 5000,
        key=f"prix_{index}"
    )
    prix_modifies.append(nouveau_prix)

# Application des modifications de l'utilisateur
df_materiau['Prix_FCFA'] = prix_modifies

# 3. Affichage des données du matériau sélectionné
st.subheader(f"📊 Données pour : {materiau_choisi}")
st.dataframe(df_materiau, use_container_width=True)

# 4. Modélisation et Prédiction automatique (Régression linéaire)
df_materiau['Mois_Index'] = np.arange(len(df_materiau))
X = df_materiau['Mois_Index']
y = df_materiau['Prix_FCFA']

a, b = np.polyfit(X, y, 1)

# Calcul des 6 mois futurs
mois_futurs = np.array([len(df_materiau), len(df_materiau)+1, len(df_materiau)+2, len(df_materiau)+3, len(df_materiau)+4, len(df_materiau)+5])
noms_futurs = ['Juil 2025', 'Août 2025', 'Sep 2025', 'Oct 2025', 'Nov 2025', 'Déc 2025']
prix_predits = a * mois_futurs + b

df_pred = pd.DataFrame({
    'Période': noms_futurs,
    'Prix Estimé (FCFA)': [int(p) for p in prix_predits]
})

# Affichage des prédictions
st.subheader("🔮 Prédiction des Prix (6 Prochains Mois)")
st.dataframe(df_pred, use_container_width=True)

# Indicateur de tendance
if a > 0:
    st.warning(f"📈 Tendance à la hausse : Le prix augmente en moyenne de **{int(a)} FCFA** par mois.")
else:
    st.success(f"📉 Tendance à la baisse ou stable.")

# 5. Graphique interactif
st.subheader("📈 Courbe d'Évolution et de Prévision")
chart_data = pd.DataFrame({
    'Mois': list(df_materiau['Date']) + noms_futurs,
    'Prix': list(df_materiau['Prix_FCFA']) + list(prix_predits)
})
st.line_chart(chart_data.set_index('Mois'))