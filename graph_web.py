import pandas as pd
import dash
from dash import dcc, html
import plotly.express as px
import sys
from process_version_ia import charger_donnees_calculées

### =======================================
### CALLBACK À PERSONNALISER PAR TOI
### =======================================
def get_biens_data_sample():
    """
    Retourne la liste des biens et les paramètres d'entrée.
    À remplacer par ta propre logique (lecture fichier, API, etc.)

    Returns:
        biens (list[dict]), apport_franck (float), apport_marine (float), duree_annees (int)
    """
    biens = [
        {
            "titre": "Maison Campagne",
            "prix_total": 300000,
            "mensuel_franck": 800,
            "mensuel_marine": 400,
        },
        {
            "titre": "Maison Bord de Mer",
            "prix_total": 400000,
            "mensuel_franck": 1000,
            "mensuel_marine": 800,
        },
    ]
    apport_franck = 30000
    apport_marine = 20000
    duree_annees = 25
    return biens, apport_franck, apport_marine, duree_annees

def get_biens_data():
    path = sys.argv[1]
    data = charger_donnees_calculées(path)

    biens = []
    maison_ref = {
        'titre': 'Maison de référence',
        'prix_total': data['maison_ref_prix'],
        'mensuel_franck': data['contributions'][0]['contrib_mensuelle_totale_franck'],
        'mensuel_marine': data['contributions'][0]['contrib_mensuelle_totale_marine'],
    }
    maison_reelle = {
        'titre': 'Maison réelle',
        'prix_total': data['maison_reelle_prix'],
        'mensuel_franck': data['contributions'][0]['contrib_mensuelle_totale_franck'],
        'mensuel_marine': data['contributions'][0]['contrib_mensuelle_totale_marine'],
    }
    biens = [maison_ref, maison_reelle]

    apport_franck = data['apport_franck']
    apport_marine = data['apport_marine']
    duree_annees = 25  # tu peux aussi extraire depuis data['credit']['années'] si tu veux

    return biens, apport_franck, apport_marine, duree_annees

### =======================================
### CALCUL DES DONNÉES
### =======================================
def calcul_repartition_biens(biens, apport_franck, apport_marine, duree_annees=25):
    rows = []
    nb_mois = duree_annees * 12

    for bien in biens:
        titre = bien["titre"]
        prix_total = bien["prix_total"]
        mensuel_franck = bien["mensuel_franck"]
        mensuel_marine = bien["mensuel_marine"]

        cum_franck = apport_franck
        cum_marine = apport_marine

        for mois in range(nb_mois + 1):
            if mois > 0:
                cum_franck += mensuel_franck
                cum_marine += mensuel_marine

            total_cum = cum_franck + cum_marine
            pct_franck = 100 * cum_franck / total_cum if total_cum else 0
            pct_marine = 100 * cum_marine / total_cum if total_cum else 0

            rows.append({
                "mois": mois,
                "bien": titre,
                "franck_valeur": cum_franck,
                "marine_valeur": cum_marine,
                "franck_pct": pct_franck,
                "marine_pct": pct_marine
            })

    return pd.DataFrame(rows)

### =======================================
### PRÉPARATION POUR LES GRAPHIQUES
### =======================================
def prepare_dataframes(df):
    df_pct = df.melt(
        id_vars=["mois", "bien"],
        value_vars=["franck_pct", "marine_pct"],
        var_name="personne",
        value_name="quote_part"
    )
    df_pct["personne"] = df_pct["personne"].map({
        "franck_pct": "Franck",
        "marine_pct": "Marine"
    })

    df_val = df.melt(
        id_vars=["mois", "bien"],
        value_vars=["franck_valeur", "marine_valeur"],
        var_name="personne",
        value_name="valeur"
    )
    df_val["personne"] = df_val["personne"].map({
        "franck_valeur": "Franck",
        "marine_valeur": "Marine"
    })

    return df_pct, df_val

### =======================================
### GRAPHIQUES DASH (1 ligne = 2 graphes par bien)
### =======================================
def bloc_graphiques_par_bien(titre_bien, df_pct, df_val):
    df_pct_bien = df_pct[df_pct["bien"] == titre_bien]
    df_val_bien = df_val[df_val["bien"] == titre_bien]

    fig_pct = px.area(
        df_pct_bien,
        x="mois",
        y="quote_part",
        color="personne",
        title=f"{titre_bien} – Quote-part (%)",
        labels={"quote_part": "Quote-part (%)", "mois": "Mois"}
    )
    fig_pct.update_yaxes(range=[0, 100])

    fig_val = px.line(
        df_val_bien,
        x="mois",
        y="valeur",
        color="personne",
        title=f"{titre_bien} – Montant cumulé (€)",
        labels={"valeur": "Montant (€)", "mois": "Mois"}
    )

    return html.Div([
        html.Div(dcc.Graph(figure=fig_pct), style={"width": "49%", "display": "inline-block"}),
        html.Div(dcc.Graph(figure=fig_val), style={"width": "49%", "display": "inline-block"}),
    ], style={"marginBottom": "40px"})

### =======================================
### APPLICATION DASH
### =======================================
def create_dash_app():
    biens, apport_franck, apport_marine, duree_annees = get_biens_data()
    df = calcul_repartition_biens(biens, apport_franck, apport_marine, duree_annees)
    df_pct, df_val = prepare_dataframes(df)

    app = dash.Dash(__name__)
    app.title = "Répartition Immo"

    app.layout = html.Div([
        html.H1("Répartition immobilière : Franck vs Marine"),
        *[bloc_graphiques_par_bien(b["titre"], df_pct, df_val) for b in biens]
    ], style={"maxWidth": "1200px", "margin": "auto"})

    return app

### =======================================
### LANCEMENT
### =======================================
if __name__ == "__main__":
    app = create_dash_app()
    app.run(debug=True)

