# guichet_mairie.py - Interface guichet municipal RÉELLE
"""
Interface pour les agents municipaux pour enregistrer les paiements RÉELS:
- Taxes municipales
- Actes administratifs
- Locations
"""

import streamlit as st
import database_mairie as db
import services_mairie as services
from datetime import datetime, date

def show_guichet_page():
    """Affiche la page du guichet municipal."""

    st.title("🏛️ Guichet Municipal")
    st.markdown("### Enregistrement des paiements")

    # Sélection de l'agent (simplifié pour démo)
    agents_list = [
        {"id": 1, "nom": "KOUADIO Jean (Trésorier)"},
        {"id": 2, "nom": "TRAORE Aminata (État Civil)"},
        {"id": 3, "nom": "YAO Kouassi (Guichet)"}
    ]

    agent_selected = st.selectbox(
        "👤 Agent en service",
        options=[a['id'] for a in agents_list],
        format_func=lambda x: next(a['nom'] for a in agents_list if a['id'] == x)
    )

    st.markdown("---")

    # Onglets pour les différents services
    tab_taxes, tab_actes, tab_locations = st.tabs([
        "💰 Taxes Municipales",
        "📄 Actes Administratifs",
        "🏢 Locations"
    ])

    # ========== TAB TAXES ==========
    with tab_taxes:
        st.subheader("💰 Paiement de Taxes Municipales")

        taxes = db.get_taxes()

        # Grouper par nom de taxe
        taxes_grouped = {}
        for taxe in taxes:
            if taxe['nom_taxe'] not in taxes_grouped:
                taxes_grouped[taxe['nom_taxe']] = []
            taxes_grouped[taxe['nom_taxe']].append(taxe)

        col1, col2 = st.columns(2)

        with col1:
            taxe_nom = st.selectbox(
                "Type de taxe",
                options=list(taxes_grouped.keys())
            )

        with col2:
            # Afficher les catégories disponibles pour cette taxe
            categories = taxes_grouped[taxe_nom]
            categorie_selected = st.selectbox(
                "Catégorie",
                options=[c['categorie'] for c in categories]
            )

        # Récupérer la taxe complète
        taxe_complete = next(t for t in categories if t['categorie'] == categorie_selected)

        # Affichage du montant
        col3, col4 = st.columns(2)

        with col3:
            if taxe_complete['montant_fixe'] and taxe_complete['montant_fixe'] > 0:
                st.metric("Montant", f"{taxe_complete['montant_fixe']:,.0f} FCFA")
                montant_final = taxe_complete['montant_fixe']
                montant_custom = False
            elif taxe_complete['taux_pourcentage']:
                montant_base = st.number_input(
                    "Montant de base (ex: loyer mensuel)",
                    min_value=0,
                    value=100000,
                    step=10000
                )
                montant_final = (montant_base * taxe_complete['taux_pourcentage']) / 100
                st.metric("Montant calculé", f"{montant_final:,.0f} FCFA")
                montant_custom = True
            else:
                montant_final = st.number_input(
                    "Montant (taxe à définir)",
                    min_value=0,
                    value=0,
                    step=1000
                )
                montant_custom = True

        with col4:
            st.info(f"**Description:** {taxe_complete.get('description', 'N/A')}")

        # Informations du contribuable (REQUIS)
        st.markdown("#### 👤 Informations du commerçant/contribuable")
        col_info1, col_info2 = st.columns(2)

        with col_info1:
            contrib_nom = st.text_input("Nom du commerçant/contribuable *", key="taxe_nom")

        with col_info2:
            contrib_numero = st.text_input("Numéro de commerçant/contribuable *", key="taxe_num",
                                          help="Numéro d'identification fiscale ou de commerçant")

        # Mode de paiement
        st.markdown("#### 💳 Mode de paiement")
        col_pay1, col_pay2 = st.columns(2)

        with col_pay1:
            mode_paiement = st.selectbox(
                "Sélectionnez le mode de paiement *",
                ["Espèces", "Airtel Money", "MobiCash", "Virement Bancaire"],
                key="mode_paiement_taxe"
            )

        with col_pay2:
            if mode_paiement in ["Airtel Money", "MobiCash"]:
                numero_mobile = st.text_input(
                    f"Numéro {mode_paiement} *",
                    placeholder="Ex: +241 XX XX XX XX",
                    key="numero_mobile_taxe"
                )
            else:
                numero_mobile = None

        # Bouton de paiement
        if st.button("✅ Enregistrer le paiement", type="primary", use_container_width=True):
            # Validation des champs requis
            if not contrib_nom or not contrib_numero:
                st.error("❌ Veuillez renseigner le nom et le numéro du commerçant/contribuable")
            elif mode_paiement in ["Airtel Money", "MobiCash"] and not numero_mobile:
                st.error(f"❌ Veuillez saisir le numéro {mode_paiement}")
            else:
                try:
                    # Construire les informations de paiement mobile
                    payment_info = f"{mode_paiement}"
                    if numero_mobile:
                        payment_info += f" - {numero_mobile}"

                    if 'montant_base' in locals() and montant_custom:
                        tx_id = services.enregistrer_paiement_taxe(
                            taxe_id=taxe_complete['id'],
                            agent_id=agent_selected,
                            montant_base=montant_base,
                            nom_commercant=contrib_nom,
                            numero_commercant=contrib_numero,
                            mode_paiement=payment_info
                        )
                    else:
                        tx_id = services.enregistrer_paiement_taxe(
                            taxe_id=taxe_complete['id'],
                            agent_id=agent_selected,
                            montant_custom=montant_final if montant_custom else None,
                            nom_commercant=contrib_nom,
                            numero_commercant=contrib_numero,
                            mode_paiement=payment_info
                        )

                    st.success(f"✅ Paiement enregistré avec succès!")
                    st.balloons()
                    st.info(f"📝 Transaction ID: {tx_id}")
                    st.info(f"💰 Montant: {montant_final:,.0f} FCFA")
                    st.info(f"👤 Commerçant: {contrib_nom} - N°{contrib_numero}")
                    st.info(f"💳 Mode: {payment_info}")

                except Exception as e:
                    st.error(f"❌ Erreur lors de l'enregistrement: {str(e)}")

    # ========== TAB ACTES ==========
    with tab_actes:
        st.subheader("📄 Délivrance d'Actes Administratifs")

        formulaires = db.get_formulaires()

        col1, col2 = st.columns(2)

        with col1:
            formulaire_selected = st.selectbox(
                "Type d'acte",
                options=[f['id'] for f in formulaires],
                format_func=lambda x: next(f['nom_document'] for f in formulaires if f['id'] == x)
            )

        formulaire = next(f for f in formulaires if f['id'] == formulaire_selected)

        with col2:
            st.metric("Coût", f"{formulaire['cout_standard']:,.0f} FCFA")

        # Informations
        col3, col4 = st.columns(2)

        with col3:
            st.info(f"**Type:** {formulaire.get('type_personne', 'N/A')}")

        with col4:
            delai = formulaire.get('delai_traitement_jours', 1)
            st.info(f"**Délai de traitement:** {delai} jour(s)")

        # Informations du demandeur (REQUIS)
        st.markdown("#### 👤 Informations du demandeur")
        col_dem1, col_dem2 = st.columns(2)

        with col_dem1:
            demandeur_nom = st.text_input("Nom complet *", key="acte_nom")

        with col_dem2:
            demandeur_numero = st.text_input("Numéro d'identification *", key="acte_num",
                                            help="Numéro de CNI ou autre document d'identification")

        # Mode de paiement
        st.markdown("#### 💳 Mode de paiement")
        col_pay_acte1, col_pay_acte2 = st.columns(2)

        with col_pay_acte1:
            mode_paiement_acte = st.selectbox(
                "Sélectionnez le mode de paiement *",
                ["Espèces", "Airtel Money", "MobiCash", "Virement Bancaire"],
                key="mode_paiement_acte"
            )

        with col_pay_acte2:
            if mode_paiement_acte in ["Airtel Money", "MobiCash"]:
                numero_mobile_acte = st.text_input(
                    f"Numéro {mode_paiement_acte} *",
                    placeholder="Ex: +241 XX XX XX XX",
                    key="numero_mobile_acte"
                )
            else:
                numero_mobile_acte = None

        # Bouton de paiement
        if st.button("✅ Délivrer l'acte et enregistrer le paiement", type="primary", use_container_width=True, key="btn_acte"):
            # Validation des champs requis
            if not demandeur_nom or not demandeur_numero:
                st.error("❌ Veuillez renseigner le nom et le numéro d'identification du demandeur")
            elif mode_paiement_acte in ["Airtel Money", "MobiCash"] and not numero_mobile_acte:
                st.error(f"❌ Veuillez saisir le numéro {mode_paiement_acte}")
            else:
                try:
                    # Construire les informations de paiement mobile
                    payment_info_acte = f"{mode_paiement_acte}"
                    if numero_mobile_acte:
                        payment_info_acte += f" - {numero_mobile_acte}"

                    tx_id = services.enregistrer_paiement_acte(
                        formulaire_id=formulaire['id'],
                        agent_id=agent_selected,
                        nom_commercant=demandeur_nom,
                        numero_commercant=demandeur_numero,
                        mode_paiement=payment_info_acte
                    )

                    st.success(f"✅ Acte délivré et paiement enregistré!")
                    st.balloons()
                    st.info(f"📝 Transaction ID: {tx_id}")
                    st.info(f"💰 Montant: {formulaire['cout_standard']:,.0f} FCFA")
                    st.info(f"👤 Demandeur: {demandeur_nom} - N°{demandeur_numero}")
                    st.info(f"💳 Mode: {payment_info_acte}")
                    st.info(f"📅 Date de retrait estimée: {datetime.now().date() + timedelta(days=delai)}")

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

    # ========== TAB LOCATIONS ==========
    with tab_locations:
        st.subheader("🏢 Réservation et Location")

        locations = db.get_locations()

        col1, col2 = st.columns(2)

        with col1:
            location_selected = st.selectbox(
                "Type de location",
                options=[l['id'] for l in locations],
                format_func=lambda x: next(f"{l['type_location']} - {l['designation']}" for l in locations if l['id'] == x)
            )

        location = next(l for l in locations if l['id'] == location_selected)

        with col2:
            st.metric("Prix de base", f"{location['prix_base']:,.0f} FCFA / {location['frequence']}")

        # Détails
        col3, col4, col5 = st.columns(3)

        with col3:
            if location.get('capacite'):
                st.info(f"**Capacité:** {location['capacite']} personnes")

        with col4:
            st.info(f"**Statut:** {'Disponible' if location.get('disponible') else 'Indisponible'}")

        with col5:
            duree = st.number_input(
                f"Durée ({location['frequence']})",
                min_value=1,
                value=1
            )

        # Calcul montant total
        montant_total = services.calculer_montant_location(location['id'], duree)
        st.metric("💰 Montant Total", f"{montant_total:,.0f} FCFA")

        # Informations réservation (REQUIS)
        st.markdown("#### 📅 Détails de la réservation")
        col6, col7 = st.columns(2)

        with col6:
            demandeur = st.text_input("Nom du demandeur *", key="loc_demandeur")
            demandeur_numero = st.text_input("Numéro d'identification *", key="loc_num",
                                            help="Numéro de CNI ou autre document")

        with col7:
            date_debut = st.date_input(
                "Date de début",
                min_value=date.today(),
                value=date.today()
            )
            motif = st.text_area("Motif de la réservation")

        # Mode de paiement
        st.markdown("#### 💳 Mode de paiement")
        col_pay_loc1, col_pay_loc2 = st.columns(2)

        with col_pay_loc1:
            mode_paiement_loc = st.selectbox(
                "Sélectionnez le mode de paiement *",
                ["Espèces", "Airtel Money", "MobiCash", "Virement Bancaire"],
                key="mode_paiement_loc"
            )

        with col_pay_loc2:
            if mode_paiement_loc in ["Airtel Money", "MobiCash"]:
                numero_mobile_loc = st.text_input(
                    f"Numéro {mode_paiement_loc} *",
                    placeholder="Ex: +241 XX XX XX XX",
                    key="numero_mobile_loc"
                )
            else:
                numero_mobile_loc = None

        # Bouton de réservation
        if st.button("✅ Confirmer la réservation et enregistrer le paiement", type="primary", use_container_width=True, key="btn_loc"):
            # Validation
            if not demandeur or not demandeur_numero:
                st.error("❌ Veuillez saisir le nom et le numéro d'identification du demandeur")
            elif mode_paiement_loc in ["Airtel Money", "MobiCash"] and not numero_mobile_loc:
                st.error(f"❌ Veuillez saisir le numéro {mode_paiement_loc}")
            else:
                try:
                    # Construire les informations de paiement mobile
                    payment_info_loc = f"{mode_paiement_loc}"
                    if numero_mobile_loc:
                        payment_info_loc += f" - {numero_mobile_loc}"

                    tx_id = services.enregistrer_paiement_location(
                        location_id=location['id'],
                        duree=duree,
                        date_debut=date_debut.strftime('%Y-%m-%d'),
                        demandeur=demandeur,
                        agent_id=agent_selected,
                        nom_commercant=demandeur,
                        numero_commercant=demandeur_numero,
                        mode_paiement=payment_info_loc
                    )

                    st.success(f"✅ Réservation confirmée et paiement enregistré!")
                    st.balloons()
                    st.info(f"📝 Transaction ID: {tx_id}")
                    st.info(f"💰 Montant payé: {montant_total:,.0f} FCFA")
                    st.info(f"💳 Mode: {payment_info_loc}")
                    st.info(f"📅 Période: {date_debut.strftime('%d/%m/%Y')} ({duree} {location['frequence']})")

                except Exception as e:
                    st.error(f"❌ Erreur: {str(e)}")

    # Footer avec statistiques du jour
    st.markdown("---")
    st.subheader("📊 Statistiques du jour")

    rapport = services.get_rapport_journalier()

    col_stat1, col_stat2 = st.columns(2)

    with col_stat1:
        st.metric("Total Transactions", rapport['total_transactions'])

    with col_stat2:
        st.metric("Total Recettes", f"{rapport['total_recettes']:,.0f} FCFA")

    if rapport['par_categorie']:
        st.markdown("**Détail par catégorie:**")
        for cat, data in rapport['par_categorie'].items():
            st.write(f"- **{cat}:** {data['nombre']} transaction(s) - {data['total']:,.0f} FCFA")


# Import nécessaire pour les délais
from datetime import timedelta

# Fonction pour affichage standalone
if __name__ == "__main__":
    show_guichet_page()
