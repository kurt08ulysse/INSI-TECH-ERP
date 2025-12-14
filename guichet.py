# guichet.py - Interface du Guichet Unique Mairie

import streamlit as st
import datetime
import mairie_data
import database as db
import random
import time

import services

def show_guichet_page():
    """Affiche la page principale du Guichet Unique."""
    st.title("🏛️ Guichet Unique Municipal")
    
    tab1, tab2, tab3 = st.tabs(["📜 État Civil & Actes", "💰 Taxes & Impôts", "🔑 Locations & Services"])
    
    with tab1:
        show_etat_civil()
        
    with tab2:
        show_taxes()
        
    with tab3:
        show_locations()

def show_etat_civil():
    """Onglet délivrance des actes d'état civil."""
    st.header("Délivrance d'Actes Administratifs")
    
    # Sélection du type d'acte
    categories = list(mairie_data.DOCUMENTS.keys())
    cat_choisie = st.selectbox("Catégorie d'acte", categories, format_func=lambda x: x.replace('_', ' '))
    
    actes_dispo = mairie_data.DOCUMENTS[cat_choisie]
    acte_choisi = st.selectbox("Type de document", actes_dispo)
    
    st.divider()
    
    # Formulaire Citoyen
    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Nom du demandeur")
        prenom = st.text_input("Prénom")
    with col2:
        cni = st.text_input("Numéro CNI / NIP")
        telephone = st.text_input("Téléphone")
        
    prix = 2000 # Prix par défaut ou configurable
    st.info(f"💵 Coût de l'acte : **{prix} FCFA**")
    
    if st.button("🖨️ Délivrer et Encaisser", key="btn_acte"):
        if not nom or not cni:
            st.error("Veuillez remplir les informations du demandeur.")
        else:
            with st.spinner("Traitement en cours..."):
                time.sleep(1) # Simulation
                
                # APPEL SERVICE
                tx_hash = services.process_guichet_payment(
                    type_acte=f"ACTE - {acte_choisi}",
                    montant=prix,
                    demandeur=f"{nom} {prenom} ({cni})",
                    infos_add=""
                )
                
                st.success(f"✅ Acte délivré avec succès !")
                st.toast(f"Paiement reçu : {prix} FCFA")
                
                # Affichage Reçu
                st.markdown(f"""
                <div style="border: 1px solid #ccc; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: black;">
                    <h3 style="text-align: center;">MAIRIE DE VENISE - REÇU DE PAIEMENT</h3>
                    <p><strong>Date :</strong> {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p><strong>Objet :</strong> {acte_choisi}</p>
                    <p><strong>Demandeur :</strong> {nom.upper()} {prenom}</p>
                    <p><strong>Montant :</strong> {prix} FCFA</p>
                    <hr>
                    <p style="font-size: 0.8em; text-align: center;">Preuve Blockchain : {tx_hash}</p>
                    <p style="font-size: 0.8em; text-align: center; color: green;">Enregistré en Base de Données</p>
                </div>
                """, unsafe_allow_html=True)

def show_taxes():
    """Onglet paiement des taxes."""
    st.header("Encaissement des Taxes")
    
    type_taxe = st.selectbox("Type de Taxe", list(mairie_data.TAXES.keys()))
    
    sous_categories = mairie_data.TAXES[type_taxe]
    
    choix_taxe = st.selectbox("Catégorie", list(sous_categories.keys()), format_func=lambda x: sous_categories[x]['label'])
    
    details_taxe = sous_categories[choix_taxe]
    prix = details_taxe['prix']
    
    st.write(f"Description : {details_taxe['label']}")
    
    col1, col2 = st.columns(2)
    with col1:
        contribuable = st.text_input("Nom Contribuable / Entité")
    with col2:
        ref_fiscale = st.text_input("Référence Fiscale / N° Box")
        
    montant_a_payer = st.number_input("Montant à payer", value=prix, min_value=0)
    
    if st.button("💳 Encaisser Taxe", key="btn_taxe"):
        if not contribuable:
            st.error("Nom du contribuable requis.")
        else:
            # APPEL SERVICE
            tx_hash = services.process_guichet_payment(
                type_acte=f"TAXE - {details_taxe['label']}",
                montant=montant_a_payer,
                demandeur=f"{contribuable} ({ref_fiscale})",
                infos_add=""
            )
            
            st.success("Paiement enregistré et sécurisé !")
            st.balloons()

def show_locations():
    """Onglet locations."""
    st.header("Réservation & Location")
    
    # 1. Sélection Ressource
    ressource_type = st.selectbox("Type de Ressource", list(mairie_data.LOCATIONS.keys()), format_func=lambda x: mairie_data.LOCATIONS[x]['label'])
    
    infos = mairie_data.LOCATIONS[ressource_type]
    prix_unitaire = infos['prix_unitaire']
    
    st.info(f"Tarif : **{prix_unitaire} FCFA / jour**")
    
    # 2. Formulaire Réservation
    with st.form("form_reservation"):
        col1, col2 = st.columns(2)
        with col1:
            demandeur = st.text_input("Nom de l'organisation / Demandeur")
            date_debut = st.date_input("Date de début", min_value=datetime.date.today())
        with col2:
            duree = st.number_input("Durée (jours)", min_value=1, value=1)
            total = prix_unitaire * duree
            st.metric("Total à payer", f"{total:,.0f} FCFA")
            
        submitted = st.form_submit_button("📅 Réserver et Payer")
        
        if submitted:
            if not demandeur:
                st.error("Nom du demandeur requis.")
            else:
                # APPEL SERVICE
                tx_hash = services.process_reservation(
                    ressource=infos['label'],
                    demandeur=demandeur,
                    date_debut=date_debut,
                    duree=duree,
                    montant=total
                )
                
                st.success("✅ Réservation confirmée et payée !")
                st.balloons()
                
                # Reçu
                st.markdown(f"""
                <div style="border: 1px solid #ccc; padding: 20px; border-radius: 10px; background-color: #f9f9f9; color: black;">
                    <h3 style="text-align: center;">MAIRIE DE VENISE - TICKET DE RÉSERVATION</h3>
                    <p><strong>Ressource :</strong> {infos['label']}</p>
                    <p><strong>Période :</strong> Du {date_debut} ({duree} jours)</p>
                    <p><strong>Client :</strong> {demandeur}</p>
                    <p><strong>Montant Payé:</strong> {total} FCFA</p>
                    <hr>
                    <p style="font-size: 0.8em; text-align: center; color: green;">Validé sur Blockchain & DB</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📅 Planning des Réservations")
    
    # Affichage du planning (récupéré depuis la DB)
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT ressource, demandeur, date_debut, duree_jours, statut FROM reservations ORDER BY date_creation DESC")
    rows = c.fetchall()
    conn.close()
    
    if rows:
        data = [dict(row) for row in rows]
        # Petit reformatage pour l'affichage
        for d in data:
            d['date_debut'] = str(d['date_debut'])
        st.dataframe(data, use_container_width=True)
    else:
        st.info("Aucune réservation en cours.")
