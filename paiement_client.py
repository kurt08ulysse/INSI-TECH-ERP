# paiement_client.py - Interface de paiement en ligne pour les citoyens
"""
Interface simplifiée permettant aux citoyens/commerçants de payer leurs taxes en ligne
via mobile money (Airtel Money, MobiCash)
"""

import streamlit as st
import database_mairie as db
import services_mairie as services
from datetime import datetime, date, timedelta

def show_paiement_client_page():
    """Affiche la page de paiement en ligne pour les clients."""

    st.title("💳 Paiement en Ligne")
    st.markdown("### Payez vos taxes municipales en toute simplicité")

    # Message d'information
    st.info("🔒 Paiement sécurisé via mobile money - Recevez votre reçu instantanément")

    st.markdown("---")

    # Onglets pour différents types de paiement
    tab_taxes, tab_actes, tab_loyers = st.tabs([
        "💰 Payer une Taxe",
        "📄 Payer un Acte",
        "🏠 Payer un Loyer"
    ])

    # ========== TAB TAXES ==========
    with tab_taxes:
        st.subheader("💰 Paiement de Taxe Municipale")

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
                "Sélectionnez la taxe à payer",
                options=list(taxes_grouped.keys()),
                key="client_taxe"
            )

        with col2:
            # Afficher les catégories disponibles
            categories = taxes_grouped[taxe_nom]
            categorie_selected = st.selectbox(
                "Catégorie",
                options=[c['categorie'] for c in categories],
                key="client_cat"
            )

        # Récupérer la taxe complète
        taxe_complete = next(t for t in categories if t['categorie'] == categorie_selected)

        # Affichage du montant
        st.markdown("### 💵 Montant à payer")

        if taxe_complete['montant_fixe'] and taxe_complete['montant_fixe'] > 0:
            montant_final = taxe_complete['montant_fixe']
            st.success(f"## {montant_final:,.0f} FCFA")
        elif taxe_complete['taux_pourcentage']:
            montant_base = st.number_input(
                "Montant de base (ex: loyer mensuel)",
                min_value=0,
                value=100000,
                step=10000,
                key="client_base"
            )
            montant_final = (montant_base * taxe_complete['taux_pourcentage']) / 100
            st.success(f"## {montant_final:,.0f} FCFA")
        else:
            montant_final = 0
            st.warning("Montant à définir - Veuillez contacter la mairie")

        st.info(f"**Description:** {taxe_complete.get('description', 'N/A')}")

        st.markdown("---")

        # Informations du payeur
        st.markdown("### 👤 Vos informations")
        col_info1, col_info2 = st.columns(2)

        with col_info1:
            nom_payeur = st.text_input(
                "Nom complet *",
                placeholder="Ex: TSHISEKEDI Jean",
                key="client_nom_taxe"
            )

        with col_info2:
            numero_contribuable = st.text_input(
                "Numéro de contribuable/commerçant *",
                placeholder="Ex: C12345",
                help="Votre numéro d'identification fiscale",
                key="client_num_taxe"
            )

        # Mode de paiement (Mobile Money uniquement)
        st.markdown("### 💳 Mode de paiement")
        st.info("ℹ️ Seuls les paiements mobiles sont acceptés en ligne")

        # Afficher les logos avec boutons radio
        st.markdown("**Choisissez votre opérateur :**")

        # Créer deux colonnes pour les logos
        col_op1, col_op2 = st.columns(2)

        with col_op1:
            st.markdown("""
                <div style='background-color: #E4002B; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;'>
                    <p style='color: white; font-size: 20px; font-weight: bold; margin: 0;'>📱 Airtel Money</p>
                </div>
            """, unsafe_allow_html=True)

        with col_op2:
            st.markdown("""
                <div style='background-color: #0066CC; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;'>
                    <p style='color: white; font-size: 20px; font-weight: bold; margin: 0;'>💰 MobiCash</p>
                </div>
            """, unsafe_allow_html=True)

        # Boutons de sélection
        mode_paiement = st.radio(
            "Sélectionnez l'opérateur :",
            ["Airtel Money", "MobiCash"],
            key="client_mode_taxe",
            horizontal=True
        )

        # Afficher le champ de numéro après sélection
        st.markdown(f"**📱 Numéro {mode_paiement} :**")
        numero_mobile = st.text_input(
            f"Entrez votre numéro {mode_paiement}",
            placeholder="+241 XX XX XX XX",
            key="client_tel_taxe",
            help=f"Votre numéro {mode_paiement} à débiter"
        )

        st.markdown("---")

        # Bouton de paiement
        if st.button("🔒 PAYER MAINTENANT", type="primary", use_container_width=True, key="btn_pay_taxe"):
            # Validation
            if not nom_payeur or not numero_contribuable:
                st.error("❌ Veuillez renseigner votre nom et numéro de contribuable")
            elif not numero_mobile:
                st.error(f"❌ Veuillez saisir votre numéro {mode_paiement}")
            elif montant_final <= 0:
                st.error("❌ Montant invalide")
            else:
                try:
                    # Construire les informations de paiement
                    payment_info = f"{mode_paiement} - {numero_mobile}"

                    # Enregistrer le paiement (sans agent_id car paiement en ligne)
                    if taxe_complete['taux_pourcentage'] and 'montant_base' in locals():
                        tx_id = services.enregistrer_paiement_taxe(
                            taxe_id=taxe_complete['id'],
                            agent_id=None,  # Paiement en ligne
                            montant_base=montant_base,
                            nom_commercant=nom_payeur,
                            numero_commercant=numero_contribuable,
                            mode_paiement=payment_info
                        )
                    else:
                        tx_id = services.enregistrer_paiement_taxe(
                            taxe_id=taxe_complete['id'],
                            agent_id=None,  # Paiement en ligne
                            nom_commercant=nom_payeur,
                            numero_commercant=numero_contribuable,
                            mode_paiement=payment_info
                        )

                    st.success("✅ PAIEMENT ENREGISTRÉ AVEC SUCCÈS!")
                    st.balloons()

                    # Afficher les détails du paiement
                    st.markdown("---")
                    st.markdown("### 📝 Détails de votre paiement")

                    col_recu1, col_recu2 = st.columns(2)

                    with col_recu1:
                        st.info(f"**Transaction ID:** {tx_id}")
                        st.info(f"**Montant:** {montant_final:,.0f} FCFA")
                        st.info(f"**Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

                    with col_recu2:
                        st.info(f"**Contribuable:** {nom_payeur}")
                        st.info(f"**N° Contribuable:** {numero_contribuable}")
                        st.info(f"**Mode:** {payment_info}")

                    st.success("📧 Un reçu a été envoyé à votre numéro mobile")

                except Exception as e:
                    st.error(f"❌ Erreur lors du paiement: {str(e)}")

    # ========== TAB ACTES ==========
    with tab_actes:
        st.subheader("📄 Paiement d'Acte Administratif")

        formulaires = db.get_formulaires()

        col1, col2 = st.columns(2)

        with col1:
            formulaire_selected = st.selectbox(
                "Type d'acte",
                options=[f['id'] for f in formulaires],
                format_func=lambda x: next(f['nom_document'] for f in formulaires if f['id'] == x),
                key="client_acte"
            )

        formulaire = next(f for f in formulaires if f['id'] == formulaire_selected)

        with col2:
            st.markdown("### 💵 Montant")
            st.success(f"## {formulaire['cout_standard']:,.0f} FCFA")

        st.info(f"**Délai de traitement:** {formulaire.get('delai_traitement_jours', 1)} jour(s)")

        st.markdown("---")

        # Informations du demandeur
        st.markdown("### 👤 Vos informations")
        col_dem1, col_dem2 = st.columns(2)

        with col_dem1:
            demandeur_nom = st.text_input(
                "Nom complet *",
                placeholder="Ex: KABILA Marie",
                key="client_nom_acte"
            )

        with col_dem2:
            demandeur_numero = st.text_input(
                "Numéro CNI/Passeport *",
                placeholder="Ex: 1234567890",
                key="client_num_acte"
            )

        # Mode de paiement
        st.markdown("### 💳 Mode de paiement")
        st.info("ℹ️ Seuls les paiements mobiles sont acceptés en ligne")

        # Afficher les logos avec boutons radio
        st.markdown("**Choisissez votre opérateur :**")

        # Créer deux colonnes pour les logos
        col_op_a1, col_op_a2 = st.columns(2)

        with col_op_a1:
            st.markdown("""
                <div style='background-color: #E4002B; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;'>
                    <p style='color: white; font-size: 20px; font-weight: bold; margin: 0;'>📱 Airtel Money</p>
                </div>
            """, unsafe_allow_html=True)

        with col_op_a2:
            st.markdown("""
                <div style='background-color: #0066CC; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;'>
                    <p style='color: white; font-size: 20px; font-weight: bold; margin: 0;'>💰 MobiCash</p>
                </div>
            """, unsafe_allow_html=True)

        # Boutons de sélection
        mode_paiement_acte = st.radio(
            "Sélectionnez l'opérateur :",
            ["Airtel Money", "MobiCash"],
            key="client_mode_acte",
            horizontal=True
        )

        # Afficher le champ de numéro après sélection
        st.markdown(f"**📱 Numéro {mode_paiement_acte} :**")
        numero_mobile_acte = st.text_input(
            f"Entrez votre numéro {mode_paiement_acte}",
            placeholder="+241 XX XX XX XX",
            key="client_tel_acte",
            help=f"Votre numéro {mode_paiement_acte} à débiter"
        )

        st.markdown("---")

        # Bouton de paiement
        if st.button("🔒 PAYER MAINTENANT", type="primary", use_container_width=True, key="btn_pay_acte"):
            # Validation
            if not demandeur_nom or not demandeur_numero:
                st.error("❌ Veuillez renseigner votre nom et numéro d'identification")
            elif not numero_mobile_acte:
                st.error(f"❌ Veuillez saisir votre numéro {mode_paiement_acte}")
            else:
                try:
                    # Construire les informations de paiement
                    payment_info_acte = f"{mode_paiement_acte} - {numero_mobile_acte}"

                    # Enregistrer le paiement
                    tx_id = services.enregistrer_paiement_acte(
                        formulaire_id=formulaire['id'],
                        agent_id=None,  # Paiement en ligne
                        nom_commercant=demandeur_nom,
                        numero_commercant=demandeur_numero,
                        mode_paiement=payment_info_acte
                    )

                    st.success("✅ PAIEMENT ENREGISTRÉ AVEC SUCCÈS!")
                    st.balloons()

                    # Afficher les détails
                    st.markdown("---")
                    st.markdown("### 📝 Détails de votre paiement")

                    delai = formulaire.get('delai_traitement_jours', 1)
                    date_retrait = datetime.now().date() + timedelta(days=delai)

                    col_recu1, col_recu2 = st.columns(2)

                    with col_recu1:
                        st.info(f"**Transaction ID:** {tx_id}")
                        st.info(f"**Montant:** {formulaire['cout_standard']:,.0f} FCFA")
                        st.info(f"**Date:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")

                    with col_recu2:
                        st.info(f"**Demandeur:** {demandeur_nom}")
                        st.info(f"**N° Document:** {demandeur_numero}")
                        st.info(f"**Mode:** {payment_info_acte}")

                    st.success(f"📅 **Date de retrait estimée:** {date_retrait.strftime('%d/%m/%Y')}")
                    st.info("📧 Un reçu a été envoyé à votre numéro mobile")

                except Exception as e:
                    st.error(f"❌ Erreur lors du paiement: {str(e)}")

    # ========== TAB LOYERS ==========
    with tab_loyers:
        st.subheader("🏠 Paiement de Loyer")

        locations = db.get_locations()

        if not locations:
            st.warning("Aucune location disponible actuellement.")
        else:
            # Sélection de la location
            col1, col2 = st.columns(2)

            with col1:
                location_selected = st.selectbox(
                    "Type de location",
                    options=[loc['id'] for loc in locations],
                    format_func=lambda x: next(f"{loc['type_location']} - {loc['designation']}" for loc in locations if loc['id'] == x),
                    key="client_location"
                )

            location = next(loc for loc in locations if loc['id'] == location_selected)

            with col2:
                st.markdown("### 💵 Prix de base")
                st.success(f"## {location['prix_base']:,.0f} FCFA / {location['frequence']}")

            st.info(f"**Description:** {location.get('description', 'N/A')}")
            st.info(f"**Capacité:** {location.get('capacite', 'N/A')} personnes")

            st.markdown("---")

            # Durée et date
            col_dur1, col_dur2 = st.columns(2)

            with col_dur1:
                duree = st.number_input(
                    f"Durée ({location['frequence']})",
                    min_value=1,
                    value=1,
                    step=1,
                    key="client_duree",
                    help=f"Nombre de {location['frequence'].lower()}"
                )

            with col_dur2:
                date_debut = st.date_input(
                    "Date de début",
                    value=date.today(),
                    key="client_date_debut",
                    help="Date de début de la location"
                )

            # Calcul du montant total
            montant_total = location['prix_base'] * duree
            st.markdown("### 💰 Montant Total")
            st.success(f"## {montant_total:,.0f} FCFA")

            st.markdown("---")

            # Informations du locataire
            st.markdown("### 👤 Vos informations")
            col_loc1, col_loc2 = st.columns(2)

            with col_loc1:
                locataire_nom = st.text_input(
                    "Nom complet *",
                    placeholder="Ex: KABILA Pierre",
                    key="client_nom_loyer"
                )

            with col_loc2:
                locataire_numero = st.text_input(
                    "Numéro CNI/Passeport *",
                    placeholder="Ex: 1234567890",
                    key="client_num_loyer"
                )

            # Mode de paiement
            st.markdown("### 💳 Mode de paiement")
            st.info("ℹ️ Seuls les paiements mobiles sont acceptés en ligne")

            # Afficher les logos avec boutons radio
            st.markdown("**Choisissez votre opérateur :**")

            # Créer deux colonnes pour les logos
            col_op_l1, col_op_l2 = st.columns(2)

            with col_op_l1:
                st.markdown("""
                    <div style='background-color: #E4002B; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;'>
                        <p style='color: white; font-size: 20px; font-weight: bold; margin: 0;'>📱 Airtel Money</p>
                    </div>
                """, unsafe_allow_html=True)

            with col_op_l2:
                st.markdown("""
                    <div style='background-color: #0066CC; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 10px;'>
                        <p style='color: white; font-size: 20px; font-weight: bold; margin: 0;'>💰 MobiCash</p>
                    </div>
                """, unsafe_allow_html=True)

            # Boutons de sélection
            mode_paiement_loyer = st.radio(
                "Sélectionnez l'opérateur :",
                ["Airtel Money", "MobiCash"],
                key="client_mode_loyer",
                horizontal=True
            )

            # Afficher le champ de numéro après sélection
            st.markdown(f"**📱 Numéro {mode_paiement_loyer} :**")
            numero_mobile_loyer = st.text_input(
                f"Entrez votre numéro {mode_paiement_loyer}",
                placeholder="+241 XX XX XX XX",
                key="client_tel_loyer",
                help=f"Votre numéro {mode_paiement_loyer} à débiter"
            )

            st.markdown("---")

            # Bouton de paiement
            if st.button("🔒 PAYER MAINTENANT", type="primary", use_container_width=True, key="btn_pay_loyer"):
                # Validation
                if not locataire_nom or not locataire_numero:
                    st.error("❌ Veuillez renseigner votre nom et numéro d'identification")
                elif not numero_mobile_loyer:
                    st.error(f"❌ Veuillez saisir votre numéro {mode_paiement_loyer}")
                else:
                    try:
                        # Construire les informations de paiement
                        payment_info_loyer = f"{mode_paiement_loyer} - {numero_mobile_loyer}"

                        # Enregistrer le paiement de location
                        tx_id = services.enregistrer_paiement_location(
                            location_id=location['id'],
                            duree=duree,
                            date_debut=date_debut.strftime('%Y-%m-%d'),
                            demandeur=locataire_nom,
                            agent_id=None,  # Paiement en ligne
                            nom_commercant=locataire_nom,
                            numero_commercant=locataire_numero,
                            mode_paiement=payment_info_loyer
                        )

                        st.success("✅ PAIEMENT ENREGISTRÉ AVEC SUCCÈS!")
                        st.balloons()

                        # Afficher les détails
                        st.markdown("---")
                        st.markdown("### 📝 Détails de votre paiement")

                        # Calculer date de fin
                        if 'Jour' in location['frequence']:
                            date_fin = date_debut + timedelta(days=duree)
                        elif 'Mois' in location['frequence']:
                            date_fin = date_debut + timedelta(days=duree * 30)
                        elif 'Heure' in location['frequence']:
                            date_fin = date_debut  # Même jour
                        else:
                            date_fin = date_debut + timedelta(days=duree)

                        col_recu1, col_recu2 = st.columns(2)

                        with col_recu1:
                            st.info(f"**Transaction ID:** {tx_id}")
                            st.info(f"**Montant:** {montant_total:,.0f} FCFA")
                            st.info(f"**Date paiement:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                            st.info(f"**Durée:** {duree} {location['frequence'].lower()}")

                        with col_recu2:
                            st.info(f"**Locataire:** {locataire_nom}")
                            st.info(f"**N° Document:** {locataire_numero}")
                            st.info(f"**Mode:** {payment_info_loyer}")
                            st.info(f"**Location:** {location['type_location']}")

                        st.success(f"📅 **Période:** Du {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}")
                        st.info("📧 Un reçu a été envoyé à votre numéro mobile")

                    except Exception as e:
                        st.error(f"❌ Erreur lors du paiement: {str(e)}")


# Pour test standalone
if __name__ == "__main__":
    show_paiement_client_page()
