# dashboard.py - Interface utilisateur Streamlit pour Système Municipal

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import database_mairie as db
import services_mairie as services
import guichet_mairie as guichet
import paiement_client
import ia_surveillance

# Configuration de la page avec support mobile
st.set_page_config(
    page_title="🏛️ Système de Gestion Municipale",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="auto"  # Auto-collapse sur mobile
)

# Meta viewport pour mobile
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

# Style CSS personnalisé avec support mobile et optimisations de performance
st.markdown("""
<style>
    /* Optimisations globales de performance */
    * {
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }

    html {
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
    }

    body {
        overflow-x: hidden;
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .alert-critical {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .alert-success {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    /* Cacher le bouton Deploy */
    .stDeployButton {
        display: none;
    }
    .stButton>button {
        width: 100%;
        transition: all 0.2s ease;
        -webkit-tap-highlight-color: rgba(0,0,0,0.1);
    }

    /* OPTIMISATIONS MOBILE */
    @media only screen and (max-width: 768px) {
        /* Performance: désactiver les animations complexes sur mobile */
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }

        /* Touch optimization */
        button, a, input, select {
            touch-action: manipulation;
            -webkit-tap-highlight-color: rgba(0,0,0,0.1);
        }

        /* Header plus petit sur mobile */
        .main-header {
            font-size: 1.5rem !important;
            margin-bottom: 1rem !important;
            line-height: 1.2;
        }

        /* Metriques adaptées */
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.8rem !important;
        }

        [data-testid="stMetricDelta"] {
            font-size: 0.7rem !important;
        }

        /* Réduire padding sur mobile */
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 0.5rem !important;
            max-width: 100% !important;
        }

        /* Sidebar plus compacte */
        [data-testid="stSidebar"] {
            min-width: 250px !important;
        }

        /* Boutons plus gros pour toucher */
        .stButton>button {
            padding: 0.75rem 1rem !important;
            font-size: 0.9rem !important;
            min-height: 48px !important;
            touch-action: manipulation;
        }

        /* Tables responsive avec scroll horizontal fluide */
        [data-testid="stDataFrame"] {
            font-size: 0.75rem !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }

        /* Graphiques Plotly responsive */
        .js-plotly-plot {
            width: 100% !important;
            touch-action: pan-x pan-y !important;
        }

        /* Colonnes stackées sur mobile */
        [data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 0.5rem;
            flex: 1 1 100% !important;
        }

        /* Tabs plus compacts */
        [data-testid="stTabs"] button {
            font-size: 0.8rem !important;
            padding: 0.5rem !important;
            min-height: 44px !important;
        }

        /* Alertes plus compactes */
        .alert-critical, .alert-success {
            padding: 0.75rem !important;
            font-size: 0.85rem !important;
        }

        /* Caption plus petite */
        .stCaption {
            font-size: 0.7rem !important;
        }

        /* Markdown plus lisible */
        .stMarkdown h3 {
            font-size: 1.1rem !important;
        }

        .stMarkdown h4 {
            font-size: 1rem !important;
        }

        .stMarkdown h5 {
            font-size: 0.9rem !important;
        }

        /* Sliders plus faciles à manipuler */
        [data-testid="stSlider"] {
            padding: 1rem 0 !important;
        }

        /* Radio buttons plus espacés et touchables */
        [data-testid="stRadio"] label {
            padding: 0.75rem 0 !important;
            font-size: 0.9rem !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
        }

        /* Data editor responsive */
        [data-testid="stDataFrameResizable"] {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }

        /* Optimiser les inputs */
        input, select, textarea {
            font-size: 16px !important; /* Évite le zoom automatique sur iOS */
            min-height: 44px !important;
        }

        /* Carte optimisée */
        .mapboxgl-canvas {
            touch-action: pan-x pan-y !important;
        }

        /* Optimisation graphiques Plotly sur mobile */
        .plotly {
            width: 100% !important;
        }

        /* Réduire hauteur des graphiques sur mobile */
        .js-plotly-plot .plotly {
            max-height: 400px !important;
        }
    }

    /* Pour très petits écrans (téléphones en portrait) */
    @media only screen and (max-width: 480px) {
        .main-header {
            font-size: 1.2rem !important;
            padding: 0.5rem !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1rem !important;
        }

        .stButton>button {
            font-size: 0.85rem !important;
            padding: 0.5rem !important;
        }

        /* Encore plus compact */
        .block-container {
            padding: 0.25rem !important;
        }

        /* Carte plus petite sur très petits écrans */
        .js-plotly-plot .plotly {
            max-height: 350px !important;
        }

        /* Titres h2 plus petits */
        h2 {
            font-size: 1rem !important;
            line-height: 1.3 !important;
        }
    }
</style>
""", unsafe_allow_html=True)


def init_db():
    """Initialise la base de données si nécessaire."""
    db.init_database()


def activer_surveillance_ia():
    """Active la surveillance IA et génère des alertes de test si nécessaire."""
    try:
        # Vérifier s'il y a déjà des alertes
        alertes_existantes = db.get_pending_alertes()

        # Si aucune alerte, créer des alertes de démonstration
        if not alertes_existantes:
            # Alerte 1: Stock critique
            db.create_alerte(
                titre="Stock formulaires CNI faible",
                description="Il ne reste que 12 formulaires de CNI en stock",
                type_alerte="STOCK_CRITIQUE",
                montant=12,
                niveau="URGENT"
            )

            # Alerte 2: Gros paiement
            db.create_alerte(
                titre="Transaction importante détectée",
                description="Paiement de 450,000 FCFA reçu pour taxe foncière",
                type_alerte="GROS_PAIEMENT",
                montant=450000,
                niveau="INFO"
            )

            # Alerte 3: Anomalie de taxe
            db.create_alerte(
                titre="Montant suspect - Taxe habitation",
                description="Taxe de 500 FCFA enregistrée (attendu: environ 50,000 FCFA)",
                type_alerte="ANOMALIE_TAXE",
                montant=500,
                niveau="URGENT"
            )

            # Alerte 4: Recette faible
            db.create_alerte(
                titre="Baisse anormale des recettes",
                description="Recettes du jour: 35,000 FCFA (moyenne: 180,000 FCFA) - Baisse de 81%",
                type_alerte="RECETTE_FAIBLE",
                montant=35000,
                niveau="ATTENTION"
            )

        # Lancer la surveillance quotidienne (en mode silencieux pour ne pas ralentir l'app)
        # ia_surveillance.lancer_surveillance_quotidienne()

    except Exception as e:
        # Ne pas bloquer l'app si la surveillance échoue
        pass


def show_metrics():
    """Affiche les métriques principales pour la mairie."""
    stats = db.get_statistics()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "💰 Recettes du Jour",
        f"{stats['recettes_jour']:,.0f} FCFA",
        delta=f"{stats['nb_transactions_jour']} transaction(s)"
    )

    col2.metric(
        "📅 Recettes du Mois",
        f"{stats['recettes_mois']:,.0f} FCFA"
    )

    col3.metric(
        "📊 Recettes Annuelles",
        f"{stats['recettes_annee']:,.0f} FCFA"
    )

    col4.metric(
        "🚨 Alertes",
        f"{stats['alertes_pending']}",
        delta="Urgent" if stats['incidents_critiques'] > 0 else None,
        delta_color="inverse"
    )

    st.caption(f"🕐 Dernière MAJ: {datetime.now().strftime('%H:%M:%S')}")


def show_revenue_distribution():
    """Affiche la répartition des recettes municipales."""
    st.subheader("📊 Répartition des Recettes Mairie")
    
    transactions = db.get_all_transactions()
    if not transactions:
        st.info("Aucune donnée financière disponible.")
        return

    df = pd.DataFrame(transactions)
    
    # Filtrer uniquement les recettes (Taxes, Actes, Locations...)
    # On considère tout ce qui a un montant > 0 et status COMPLETE comme recette potentielle
    df_recettes = df[(df['montant'] > 0) & (df['statut'] == 'COMPLETE')]
    
    if df_recettes.empty:
        st.info("Pas encore de recettes validées.")
        return
        
    # Catégorisation simplifiée
    def categorize(t):
        if "TAXE" in t: return "Taxes & Impôts"
        if "ACTE" in t: return "Actes Administratifs"
        if "LOCATION" in t: return "Locations"
        return "Divers"
        
    df_recettes['categorie'] = df_recettes['type'].apply(categorize)
    
    # Agrégation par catégorie
    df_grouped = df_recettes.groupby('categorie')['montant'].sum().reset_index()
    
    # Calcul des pourcentages
    total = df_grouped['montant'].sum()
    df_grouped['percent'] = (df_grouped['montant'] / total) * 100
    
    # Chart Pie Interactif centré
    fig = px.pie(
        df_grouped,
        values='montant',
        names='categorie',
        title='Pourcentage des Recettes par Source',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )

    fig.update_traces(textinfo='percent+label')

    # Centrer le graphique avec layout amélioré
    fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},  # Centrer le titre
        showlegend=True,
        legend=dict(
            orientation="h",  # Légende horizontale
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=80, b=80, l=50, r=50),  # Marges équilibrées
        height=500
    )

    # Utiliser des colonnes pour centrer le graphique
    col_left, col_chart, col_right = st.columns([1, 3, 1])

    with col_chart:
        st.plotly_chart(fig, use_container_width=True)

    # Affichage tabulaire simple centré aussi
    col_left2, col_table, col_right2 = st.columns([1, 2, 1])

    with col_table:
        st.dataframe(
            df_grouped[['categorie', 'montant', 'percent']],
            column_config={
                "categorie": "Source",
                "montant": st.column_config.NumberColumn("Montant Total", format="%.0f FCFA"),
                "percent": st.column_config.NumberColumn("Part (%)", format="%.1f %%")
            },
            use_container_width=True,
            hide_index=True
        )


from fpdf import FPDF
import base64

def export_to_pdf(data):
    """Génère un PDF à partir d'une liste de dictionnaires avec informations clients."""
    pdf = FPDF(orientation='L')  # Landscape pour plus de colonnes
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Titre
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt="Historique des Recettes - ERP Municipal", ln=True, align='C')
    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(35, 8, "Date", 1)
    pdf.cell(50, 8, "Libelle", 1)
    pdf.cell(30, 8, "Montant", 1)
    pdf.cell(45, 8, "Nom Client", 1)
    pdf.cell(35, 8, "N° CNI/Contrib", 1)
    pdf.cell(55, 8, "Paiement/Tel", 1)
    pdf.cell(30, 8, "N° Recu", 1)
    pdf.ln()

    # Table Body
    pdf.set_font("Arial", size=7)
    for row in data:
        date = str(row.get('date_creation', ''))[:16]
        libelle = str(row.get('type', ''))[:25]
        montant = f"{row.get('montant', 0):,.0f}"
        nom_client = str(row.get('nom_commercant', ''))[:20]
        numero_client = str(row.get('numero_commercant', ''))[:15]
        mode_paiement = str(row.get('mode_paiement', ''))[:25]
        numero_recu = str(row.get('numero_recu', ''))[:15]

        pdf.cell(35, 6, date, 1)
        pdf.cell(50, 6, libelle, 1)
        pdf.cell(30, 6, montant, 1)
        pdf.cell(45, 6, nom_client, 1)
        pdf.cell(35, 6, numero_client, 1)
        pdf.cell(55, 6, mode_paiement, 1)
        pdf.cell(30, 6, numero_recu, 1)
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1')
def show_revenue_history():
    """Affiche l'historique des recettes (anciennement contrats)."""
    st.subheader("💰 Historique des Recettes")
    
    # On récupère les transactions de type Recette (Taxe ou Acte)
    transactions = db.get_all_transactions()
    recettes = [t for t in transactions if "TAXE" in t['type'] or "ACTE" in t['type']]
    
    # Statistiques des Recettes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_recettes = sum(t['montant'] for t in recettes)
        st.metric("💵 Total Recettes", f"{total_recettes:,.0f} FCFA")
    
    with col2:
        nb_transactions = len(recettes)
        st.metric("🧾 Nombre d'Encaissements", nb_transactions)
    
    with col3:
        avg_panier = total_recettes / nb_transactions if nb_transactions > 0 else 0
        st.metric("📊 Panier Moyen", f"{avg_panier:,.0f} FCFA")
    
    st.subheader("Détails des Encaissements")

    if recettes:
        df_recettes = pd.DataFrame(recettes)
        # Trier par date décroissante (si pas déjà fait)
        if 'date_creation' in df_recettes.columns:
            df_recettes = df_recettes.sort_values(by='date_creation', ascending=False)

            # S'assurer que les colonnes existent
            if 'nom_commercant' not in df_recettes.columns:
                df_recettes['nom_commercant'] = ''
            if 'numero_commercant' not in df_recettes.columns:
                df_recettes['numero_commercant'] = ''
            if 'mode_paiement' not in df_recettes.columns:
                df_recettes['mode_paiement'] = ''

            # Construire une colonne de référence lisible (numéro de reçu seulement)
            def make_ref(r):
                nr = r['numero_recu'] if 'numero_recu' in r and r['numero_recu'] else ''
                return nr

            df_recettes['reference'] = df_recettes.apply(make_ref, axis=1)

            st.dataframe(
                df_recettes[['date_creation', 'type', 'montant', 'nom_commercant', 'numero_commercant', 'mode_paiement', 'reference']],
                column_config={
                    "date_creation": "Date",
                    "type": "Libellé",
                    "montant": st.column_config.NumberColumn("Montant", format="%.0f FCFA"),
                    "nom_commercant": "Nom Client",
                    "numero_commercant": "N° CNI/Contribuable",
                    "mode_paiement": "Mode Paiement / Téléphone",
                    "reference": "N° Reçu"
                },
                use_container_width=True,
                hide_index=True
            )
        
        # Bouton Export PDF Direct
        pdf_bytes = export_to_pdf(recettes)
        st.download_button(
            label="📄 Télécharger le Tableau en PDF",
            data=pdf_bytes,
            file_name=f"recettes_mairie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime='application/pdf'
        )


def show_transactions():
    """Affiche l'historique des transactions."""
    st.subheader("💰 Historique des Transactions & Recettes")

    transactions = db.get_all_transactions()

    if not transactions:
        st.info("Aucune transaction enregistrée.")
        return

    df = pd.DataFrame(transactions)

    # Graphique interactif amélioré des transactions dans le temps
    if 'date_creation' in df.columns:
        df['date'] = pd.to_datetime(df['date_creation'], format='mixed').dt.date

        # Agréger par jour: somme des montants ET nombre de transactions
        daily = df.groupby('date').agg({
            'montant': 'sum',
            'id': 'count'
        }).reset_index()
        daily.columns = ['date', 'montant_total', 'nb_transactions']

        # Créer un graphique combiné (barres + ligne)
        fig = go.Figure()

        # Barres pour les montants
        fig.add_trace(go.Bar(
            x=daily['date'],
            y=daily['montant_total'],
            name='Montant Total',
            marker_color='#4CAF50',
            hovertemplate='<b>%{x}</b><br>' +
                         'Montant: %{y:,.0f} FCFA<br>' +
                         '<extra></extra>'
        ))

        # Ligne pour le nombre de transactions (axe secondaire)
        fig.add_trace(go.Scatter(
            x=daily['date'],
            y=daily['nb_transactions'],
            name='Nombre de Transactions',
            mode='lines+markers',
            line=dict(color='#FF9800', width=3),
            marker=dict(size=8, symbol='diamond'),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>' +
                         'Transactions: %{y}<br>' +
                         '<extra></extra>'
        ))

        # Mise en page améliorée
        fig.update_layout(
            title={
                'text': '📊 Évolution des Recettes & Nombre de Transactions',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'color': '#1E88E5'}
            },
            xaxis_title='Date',
            yaxis_title='Montant Total (FCFA)',
            yaxis2=dict(
                title='Nombre de Transactions',
                overlaying='y',
                side='right',
                showgrid=False
            ),
            height=500,
            hovermode='x unified',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='rgba(128,128,128,0.2)'
            )
        )

        # Afficher le graphique avec configuration interactive complète
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': f'transactions_{datetime.now().strftime("%Y%m%d")}',
                'height': 600,
                'width': 1200,
                'scale': 2
            }
        })

    # Créer des onglets pour séparer l'Affichage Global et Recettes
    tab1, tab2 = st.tabs(["🌎 Tout", "📥 Recettes (Taxes & Actes)"])
    
    with tab1:
        # S'assurer que les colonnes existent
        if 'nom_commercant' not in df.columns:
            df['nom_commercant'] = ''
        if 'numero_commercant' not in df.columns:
            df['numero_commercant'] = ''
        if 'mode_paiement' not in df.columns:
            df['mode_paiement'] = ''
        if 'numero_recu' not in df.columns:
            df['numero_recu'] = ''

        st.dataframe(
            df[['date_creation', 'type', 'montant', 'nom_commercant', 'numero_commercant', 'mode_paiement', 'numero_recu', 'statut']],
            column_config={
                "date_creation": "Date",
                "type": st.column_config.TextColumn("Type Opération"),
                "montant": st.column_config.NumberColumn("Montant (FCFA)", format="%.0f FCFA"),
                "nom_commercant": "Nom Client",
                "numero_commercant": "N° CNI/Contribuable",
                "mode_paiement": "Mode Paiement / Téléphone",
                "numero_recu": "N° Reçu",
                "statut": "Statut"
            },
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        # Filtrer Recettes (ce qui commence par TAXE ou ACTE)
        df_recettes = df[df['type'].str.contains("TAXE|ACTE", na=False)]

        st.metric("Total Recettes", f"{df_recettes['montant'].sum():,.0f} FCFA")

        # S'assurer que les colonnes existent
        if 'nom_commercant' not in df_recettes.columns:
            df_recettes['nom_commercant'] = ''
        if 'numero_commercant' not in df_recettes.columns:
            df_recettes['numero_commercant'] = ''
        if 'mode_paiement' not in df_recettes.columns:
            df_recettes['mode_paiement'] = ''
        if 'numero_recu' not in df_recettes.columns:
            df_recettes['numero_recu'] = ''

        st.dataframe(
            df_recettes[['date_creation', 'type', 'montant', 'nom_commercant', 'numero_commercant', 'mode_paiement', 'numero_recu']],
            column_config={
                "date_creation": "Date",
                "type": "Type",
                "montant": st.column_config.NumberColumn("Montant (FCFA)", format="%.0f FCFA"),
                "nom_commercant": "Nom Client",
                "numero_commercant": "N° CNI/Contribuable",
                "mode_paiement": "Mode Paiement / Téléphone",
                "numero_recu": "N° Reçu"
            },
            use_container_width=True,
            hide_index=True
        )
        

    



def show_alerts():
    """Affiche les alertes."""
    st.subheader("🚨 Alertes")
    
    alertes = db.get_pending_alertes()
    
    if not alertes:
        st.success("✅ Aucune alerte active")
        return
    
    # Bouton de suppression global
    if st.button("✅ Tout marquer comme traité", type="primary"):
        db.mark_all_alertes_treated()
        st.rerun()
    
    for alerte in alertes:
        # Couleur selon type
        if alerte['type'] == 'STOCK_CRITIQUE':
            color_border = "red"
            icon = "🚨"
            provenance = "Détection automatique seuil critique"
            valeur_lbl = f"{alerte['quantite']} unités"
        elif alerte['type'] == 'GROS_PAIEMENT':
            color_border = "#4CAF50" # Vert
            icon = "💰"
            provenance = "Transaction importante détectée"
            valeur_lbl = f"{alerte['quantite']} FCFA"
        elif alerte['type'] == 'ANOMALIE_TAXE':
            color_border = "#9C27B0" # Violet
            icon = "🕵️"
            provenance = "Montant suspect détecté (Normes non respectées)"
            valeur_lbl = f"{alerte['quantite']} FCFA"
        elif alerte['type'] == 'RETARD_PAIEMENT':
            color_border = "#FF9800" # Orange Foncé
            icon = "⏳"
            provenance = "Retard de paiement détecté par l'IA"
            valeur_lbl = f"En attente"
        elif alerte['type'] == 'RECETTE_FAIBLE':
            color_border = "#FF5722" # Orange Vif
            icon = "📉"
            provenance = "Baisse anormale des recettes détectée"
            valeur_lbl = f"{alerte['quantite']} FCFA (Total Jour)"
        elif alerte['type'] == 'CRITIQUE_FINANCIER':
            color_border = "#D50000" # Rouge Sang
            icon = "📛"
            provenance = "TENTATIVE DE FRAUDE / ERREUR CRITIQUE"
            valeur_lbl = "ECHEC TRANSACTION"
        else:
            color_border = "orange"
            icon = "⚠️"
            provenance = "Système"
            valeur_lbl = f"{alerte['quantite']}"
        
        container = st.container()
        container.markdown(f"""
        <div style="border: 1px solid {color_border}; padding: 10px; border-radius: 5px; margin-bottom: 10px; border-left: 5px solid {color_border};">
            <h4 style="margin: 0;">{icon} {alerte['matiere']}</h4>
            <div style="display: flex; justify_content: space-between;">
                <span><strong>Info:</strong> {valeur_lbl}</span>
                <span style="color: #666; font-size: 0.8em;">{alerte['date_creation']}</span>
            </div>
            <div style="font-size: 0.9em; margin-top: 5px;">
                <em>Provenance : {provenance}</em>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if container.button(f"✅ Marquer comme traité", key=f"treat_{alerte['id']}"):
            db.mark_alerte_treated(alerte['id'])
            st.rerun()


from streamlit_autorefresh import st_autorefresh
import ai_forecast


def show_predictions():
    """Affiche les prédictions IA."""
    st.subheader("🧠 Prédictions Financières (IA)")
    
    st.markdown("### 🔮 Prévisions des Recettes Municipales")
    
    # On se concentre uniquement sur les recettes comme demandé
    forecast = ai_forecast.predict_revenue()
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.metric("Tendance", forecast['trend'], delta=f"{forecast['slope']:.2f}")
    
    with col_f2:
        st.metric("Recettes attendues (30j)", f"{forecast['expected_revenue_30d']:,.0f} FCFA")
        
    with col_f3:
        st.caption("Basé sur une régression linéaire des transactions (Taxes & Actes).")
        
    # Graphique Finance
    hist = forecast['history']
    pred = forecast['forecast']
    
    fig_fin = go.Figure()
    
    # Historique
    fig_fin.add_trace(go.Bar(
        x=hist['date'], y=hist['revenue'],
        name='Recettes Réelles',
        marker_color='#4CAF50'
    ))
    
    # Prédiction
    fig_fin.add_trace(go.Scatter(
        x=pred['date'], y=pred['revenue'],
        mode='lines+markers', name='Prévision IA',
        line=dict(color='#FFC107', width=3, dash='dot')
    ))
    
    fig_fin.update_layout(
        title="Projection des Recettes",
        xaxis_title="Date",
        yaxis_title="Montant (FCFA)",
        height=450,
        hovermode="x unified"
    )
    
    st.plotly_chart(fig_fin, use_container_width=True)


def show_marches_map():
    """Affiche la cartographie des marchés municipaux de Franceville."""
    # Titre responsive
    st.markdown("""
    <h2 style='text-align: center; color: #1E88E5; font-size: clamp(1rem, 4vw, 1.5rem); margin-bottom: 1rem;'>
    🗺️ Cartographie des Marchés - Franceville, Gabon
    </h2>
    """, unsafe_allow_html=True)

    # Récupérer les données des marchés
    marches = db.get_all_marches()

    if not marches:
        st.info("Aucun marché enregistré pour le moment.")
        return

    # Convertir en DataFrame
    df_marches = pd.DataFrame(marches)

    # Statistiques globales
    stats = db.get_marches_stats()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🏪 Nombre de Marchés", stats['total_marches'])

    with col2:
        st.metric("🛒 Total Étals/Box", f"{stats['total_etals']:,.0f}")

    with col3:
        st.metric("💰 Tarif Moyen", f"{stats['tarif_moyen']:,.0f} FCFA")

    st.markdown("---")

    # Créer la carte avec Plotly - Centrée sur Franceville, Gabon
    # Franceville: -1.6332°S, 13.5833°E

    # Préparer les informations de hover personnalisées
    hover_texts = []
    for _, row in df_marches.iterrows():
        hover_text = f"<b>{row['nom_marche']}</b><br>"
        hover_text += f"📍 Quartier: {row['quartier']}<br>"
        hover_text += f"🛒 Étals: {row['nombre_etals']}<br>"
        hover_text += f"💰 Tarif: {row['tarif_etal_jour']:,.0f} FCFA<br>"
        hover_text += f"📅 {row['jours_ouverture']}<br>"
        hover_text += f"🕐 {row['horaires']}"
        hover_texts.append(hover_text)

    # Créer la figure avec des marqueurs bien visibles
    fig = go.Figure()

    # Ajouter les marqueurs des marchés avec une taille fixe et visible
    fig.add_trace(go.Scattermapbox(
        lat=df_marches['latitude'],
        lon=df_marches['longitude'],
        mode='markers',  # Seulement les marqueurs, pas de texte pour éviter superposition
        marker=dict(
            size=25,  # Taille augmentée pour meilleure visibilité
            color='#FF4444',  # Rouge vif
            opacity=0.95,
            symbol='circle'
        ),
        hovertext=hover_texts,
        hoverinfo='text',
        name='Marchés de Franceville'
    ))

    # Configuration de la carte (OpenStreetMap)
    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=-1.6332, lon=13.5833),  # Centre sur Franceville, Gabon
            zoom=13
        ),
        height=500,  # Hauteur réduite pour meilleure compatibilité mobile
        margin={"r": 0, "t": 10, "l": 0, "b": 0},  # Marges réduites
        showlegend=False,  # Masquer la légende pour plus d'espace
        # Activer les interactions (zoom, pan, etc.)
        dragmode='zoom',
        hovermode='closest'
    )

    # Activer tous les boutons de contrôle
    config = {
        'scrollZoom': True,  # Zoom avec la molette
        'displayModeBar': True,  # Afficher la barre d'outils
        'displaylogo': False,  # Masquer le logo Plotly
        'modeBarButtonsToAdd': ['zoom2d', 'pan2d', 'zoomIn2d', 'zoomOut2d', 'resetScale2d']
    }

    st.plotly_chart(fig, use_container_width=True, config=config)

    # Détails des marchés sous forme de tableau
    st.markdown("### 📋 Liste détaillée des marchés")

    # Préparer le tableau
    df_display = df_marches[[
        'nom_marche', 'quartier', 'nombre_etals', 'tarif_etal_jour',
        'type_marche', 'jours_ouverture', 'horaires'
    ]].copy()

    df_display.columns = [
        'Nom du Marché', 'Quartier', 'Nb Étals', 'Tarif (FCFA)',
        'Type', 'Jours Ouverture', 'Horaires'
    ]

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tarif (FCFA)": st.column_config.NumberColumn(
                format="%d FCFA"
            )
        }
    )

    # Section informations détaillées par marché
    st.markdown("### 📍 Informations détaillées")

    selected_marche = st.selectbox(
        "Sélectionnez un marché pour plus de détails:",
        df_marches['nom_marche'].tolist()
    )

    if selected_marche:
        marche_info = df_marches[df_marches['nom_marche'] == selected_marche].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**🏪 {marche_info['nom_marche']}**")
            st.markdown(f"📍 **Adresse:** {marche_info['adresse']}")
            st.markdown(f"🏘️ **Quartier:** {marche_info['quartier']}")
            st.markdown(f"📅 **Jours:** {marche_info['jours_ouverture']}")
            st.markdown(f"🕐 **Horaires:** {marche_info['horaires']}")

        with col2:
            st.markdown(f"🛒 **Nombre d'étals/box:** {marche_info['nombre_etals']}")
            st.markdown(f"💰 **Tarif:** {marche_info['tarif_etal_jour']:,.0f} FCFA")
            st.markdown(f"🏷️ **Type:** {marche_info['type_marche']}")
            st.markdown(f"📌 **Coordonnées GPS:** {marche_info['latitude']}, {marche_info['longitude']}")

        if marche_info['description']:
            st.info(f"ℹ️ **Description:** {marche_info['description']}")


def main():
    """Point d'entrée principal."""
    # Auto-refresh toutes les 5 secondes pour meilleure performance mobile
    count = st_autorefresh(interval=5000, limit=None, key="fizzbuzzcounter")

    init_db()
    activer_surveillance_ia()  # Activer la surveillance et créer alertes de démo

    # Header
    st.markdown('<div class="main-header">🏛️ SYSTÈME DE GESTION MUNICIPALE</div>',
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:

        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "🗺️ Cartographie Marchés", "💳 Paiement en Ligne", "🏛️ Guichet Mairie", "💰 Historique Recettes", "📜 Historique Transactions", "🚨 Alertes"]
        )
        
        st.markdown("---")

        
        st.markdown("---")

        # Refresh button removed to avoid accidental page reloads
    
    # Contenu principal
    # Console visible partout en bas (ou sur page dédiée ?)
    # Pour l'instant, on l'affiche sur l'onglet Dashboard en bas pour l'effet "Wow" immédiat
    # Ou mieux : sur une page dédiée "Console IA" ou en bas de tout.
    
    if page not in ["🏛️ Guichet Mairie", "💳 Paiement en Ligne"]:
        show_metrics()
        st.markdown("---")
    
    if page == "📊 Dashboard":
        show_revenue_distribution()
        st.markdown("---")

    elif page == "🗺️ Cartographie Marchés":
        show_marches_map()

    elif page == "💳 Paiement en Ligne":
        paiement_client.show_paiement_client_page()
    elif page == "🏛️ Guichet Mairie":
        guichet.show_guichet_page()
    elif page == "💰 Historique Recettes":
        show_revenue_history()
    elif page == "📜 Historique Transactions":
        show_transactions()
    elif page == "🚨 Alertes":
        show_alerts()
    
    # Footer
    # ...


if __name__ == "__main__":
    main()
