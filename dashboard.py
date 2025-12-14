# dashboard.py - Interface utilisateur Streamlit

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
from datetime import datetime
import time
import database as db

# Configuration de la page
st.set_page_config(
    page_title="📦 Gestion des Stocks IoT",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
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
    }
</style>
""", unsafe_allow_html=True)


def init_db():
    """Initialise la base de données si nécessaire."""
    db.init_database()


def show_metrics():
    """Affiche les métriques principales."""
    stats = db.get_statistics()
    
    # Calcul Recettes Mairie
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT SUM(montant) FROM transactions WHERE type LIKE 'TAXE%' OR type LIKE 'ACTE%'")
    res = c.fetchone()[0]
    recettes_mairie = res if res else 0
    conn.close()

    col1, col3, col4 = st.columns(3)
    col1.metric("🚨 Anomalies Recettes", f"{stats['incidents_critiques']}", delta="Urgent" if stats['incidents_critiques'] > 0 else "OK", delta_color="inverse")
    col3.metric("💰 Recettes Mairie", f"{recettes_mairie:,.0f} FCFA", delta="Positif")
    col4.metric("⚠️ Alertes Actives", f"{stats['alertes_pending']}", delta="À traiter" if stats['alertes_pending'] > 0 else None, delta_color="inverse")
    
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
    
    # Chart Pie Interactif
    fig = px.pie(
        df_grouped, 
        values='montant', 
        names='categorie', 
        title='Pourcentage des Recettes par Source',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    
    fig.update_traces(textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # Affichage tabulaire simple à côté ou en dessous
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
    """Génère un PDF à partir d'une liste de dictionnaires."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Titre
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Historique des Recettes - ERP Municipal", ln=True, align='C')
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Date", 1)
    pdf.cell(80, 10, "Libelle", 1)
    pdf.cell(40, 10, "Montant", 1)
    pdf.ln()
    
    # Table Body
    pdf.set_font("Arial", size=10)
    for row in data:
        date = str(row.get('date_creation', ''))[:19]
        libelle = str(row.get('type', ''))
        montant = f"{row.get('montant', 0):,.0f} FCFA"
        
        pdf.cell(50, 10, date, 1)
        pdf.cell(80, 10, libelle, 1)
        pdf.cell(40, 10, montant, 1)
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

        st.dataframe(
            df_recettes[['date_creation', 'type', 'montant', 'transaction_id']],
            column_config={
                "date_creation": "Date",
                "type": "Libellé",
                "montant": st.column_config.NumberColumn("Montant", format="%.0f FCFA"),
                "transaction_id": "Référence / Demandeur"
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
    
    # Graphique des transactions dans le temps (conservé de l'original)
    if 'date_creation' in df.columns:
        df['date'] = pd.to_datetime(df['date_creation'], format='mixed').dt.date
        daily = df.groupby('date')['montant'].sum().reset_index()
        
        fig = px.line(
            daily, x='date', y='montant',
            title="Paiements par Jour",
            markers=True
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Créer des onglets pour séparer l'Affichage Global et Recettes
    tab1, tab2 = st.tabs(["🌎 Tout", "📥 Recettes (Taxes & Actes)"])
    
    with tab1:
        # Code existant simplifié ou affichage global
        st.dataframe(
            df[['date_creation', 'type', 'montant', 'transaction_id', 'statut']],
            column_config={
                "montant": st.column_config.NumberColumn("Montant (FCFA)", format="%.0f FCFA"),
                "type": st.column_config.TextColumn("Type Opération"),
                "transaction_id": "Détails / Réf"
            },
            use_container_width=True
        )

    with tab2:
        # Filtrer Recettes (ce qui commence par TAXE ou ACTE)
        df_recettes = df[df['type'].str.contains("TAXE|ACTE", na=False)]
        
        st.metric("Total Recettes", f"{df_recettes['montant'].sum():,.0f} FCFA")
        
        st.dataframe(
            df_recettes[['date_creation', 'type', 'montant', 'transaction_id']],
            column_config={
                "montant": st.column_config.NumberColumn("Montant (FCFA)", format="%.0f FCFA"),
                "transaction_id": "Contribuable / Demandeur"
            },
            use_container_width=True
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


def show_simulation():
    """Simulation des recettes et gestion des services."""
    st.subheader("💰 Simulation Recettes & Services")
    
    # Onglets : Simulation Flux et Gestion Services
    tab_sim, tab_stocks, tab_manage = st.tabs(["💸 Recettes (Simulation)", "📦 Stocks (Simulation)", "📋 Gestion Services"])
    
    with tab_sim:
        st.markdown("##### Simuler des encaissements aléatoires")
        
        col1, col2 = st.columns(2)
        with col1:
            nb_sim = st.slider("Nombre de transactions à générer", 1, 50, 5)
        
        with col2:
            st.info("Ceci simule une journée d'activité au guichet.")
            
        # Initialization de l'état si nécessaire
        if 'simulation_done' not in st.session_state:
            st.session_state.simulation_done = False
            st.session_state.montant_genere = 0

        if st.button("⚡ SIMULER LES ENCAISSEMENTS"):
            with st.spinner("Simulation de la blockchain en cours..."):
                # APPEL AU SERVICE (Business Logic)
                total = services.simulate_daily_revenue(nb_sim)
                
                # Mise à jour de l'état
                st.session_state.simulation_done = True
                st.session_state.montant_genere = total
                
                time.sleep(1)
                st.rerun()

        # Affichage du résultat persistant
        if st.session_state.simulation_done:
            st.success(f"✅ Simulation terminée ! Recettes générées : {st.session_state.montant_genere:,.0f} FCFA")
            if st.button("🗑️ Effacer résultat"):
                st.session_state.simulation_done = False
                st.rerun()
            st.balloons()

    with tab_stocks:
        st.markdown("##### Simuler une consommation critique")
        st.warning("⚠️ Attention : Cette action va réduire les stocks aléatoirement pour simuler l'activité chantier.")
        
        if st.button("📉 SIMULER CONSOMMATION MATÉRIEL", type="primary"):
             with st.spinner("Consommation en cours..."):
                 nb_critiques = services.simulate_stock_consumption(10)
                 time.sleep(1)
                 st.rerun()
                 
        if 'stock_sim_msg' not in st.session_state:
             st.session_state.stock_sim_msg = None
             
    with tab_manage:
        st.write("Gestion des Tarifs (Modifiable)")
        
        conn = db.get_connection()
        
        st.markdown("**Taxes & Redevances**")
        df_taxes = pd.read_sql_query("SELECT * FROM taxes", conn)
        # Éditeur de données pour les Taxes
        edited_taxes = st.data_editor(
            df_taxes, 
            num_rows="dynamic", 
            key="editor_taxes",
            use_container_width=True
        )
        
        if st.button("💾 Sauvegarder Taxes"):
            db.update_all_taxes(edited_taxes)
            st.success("Taxes mises à jour !")
            time.sleep(1)
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("**Formulaires & Actes**")
        df_docs = pd.read_sql_query("SELECT * FROM formulaires", conn)
        # Éditeur de données pour les Documents
        edited_docs = st.data_editor(
            df_docs, 
            num_rows="dynamic", 
            key="editor_docs",
            use_container_width=True
        )
        
        if st.button("💾 Sauvegarder Actes"):
            db.update_all_formulaires(edited_docs)
            st.success("Actes mis à jour !")
            time.sleep(1)
            st.rerun()
        
        conn.close()


from streamlit_autorefresh import st_autorefresh
import log_stream
import agents
import envoi_email
import guichet
import services
import ai_forecast

def show_console():
    """Affiche la console IA en temps réel."""
    st.markdown("### 🤖 Console IA & Blockchain (Live)")
    
    # Conteneur scrollable (style terminal)
    logs = log_stream.get_logs()
    
    log_html = '<div style="background-color:#1E1E1E; color:#00FF00; padding:10px; border-radius:5px; height:200px; overflow-y:scroll; font-family:monospace; font-size:12px;">'
    for log in reversed(logs): # Plus récent en haut
        color = "#00FF00"
        if log['level'] == "WARNING": color = "orange"
        if log['level'] == "ERROR": color = "red"
        
        log_html += f'<div style="color:{color};">[{log["source"]}] {log["message"]}</div>'
    log_html += '</div>'
    
    st.markdown(log_html, unsafe_allow_html=True)
    
    # Boutons d'action directe
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚡ FORCER SIMULATION RUPTURE"):
            # Simulation d'un scénario complet
            st.toast("Simulation rupture lancée...", icon="🚨")
            log_stream.add_log("INFO", "USER", "Déclenchement manuel simulation rupture 'FER'")
            envoi_email.envoyer_email("fer", 5) # Stock bas -> Négociation
            st.rerun()
            
    with col2:
        if st.button("🧹 Vider les logs"):
            log_stream.clear_logs()
            st.rerun()


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


def main():
    """Point d'entrée principal."""
    # Auto-refresh toutes les 2 secondes pour effet "Live"
    count = st_autorefresh(interval=2000, limit=None, key="fizzbuzzcounter")

    init_db()
    
    # Header
    st.markdown('<div class="main-header">INSI-TECH GESTION INTELLIGENTE DE STOCK</div>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:

        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "🏛️ Guichet Mairie", "🧠 Prédictions IA", "Historique Recettes", "Historique Transactions", "🚨 Alertes", "🎮 Console IA"]
        )
        
        st.markdown("---")

        
        st.markdown("---")
        
        # AUTO PILOT TOGGLE
        auto_pilot = st.toggle("🤖 Mode Auto-Pilote", value=False, help="Simule de l'activité automatiquement toutes les 2s")
        
        if st.button("🔄 Rafraîchir"):
            st.rerun()

    # LOGIQUE AUTO-PILOTE
    if auto_pilot:
        # Probabilité d'action à chaque refresh (toutes les 2s)
        
        # 70% de chance d'une transaction financière pour que ça bouge !
        if random.random() < 0.7:
            services.simulate_daily_revenue(1)
    
    # Contenu principal
    # Console visible partout en bas (ou sur page dédiée ?)
    # Pour l'instant, on l'affiche sur l'onglet Dashboard en bas pour l'effet "Wow" immédiat
    # Ou mieux : sur une page dédiée "Console IA" ou en bas de tout.
    
    if page != "🏛️ Guichet Mairie":
        show_metrics()
        st.markdown("---")
    
    if page == "📊 Dashboard":
        show_revenue_distribution()
        st.markdown("---")

    elif page == "🏛️ Guichet Mairie":
        guichet.show_guichet_page()
    elif page == "🧠 Prédictions IA":
        show_predictions()
    elif page == "Historique Recettes":
        show_revenue_history()
    elif page == "Historique Transactions":
        show_transactions()
    elif page == "🚨 Alertes":
        show_alerts()
    elif page == "🎮 Console IA": # Page focus console
        show_console()
        show_simulation()
    
    # Footer
    # ...


if __name__ == "__main__":
    main()
