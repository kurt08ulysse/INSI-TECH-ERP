# mairie_data.py - Référentiel des Tarifs et Services Municipaux

# 1. TAXES & REDEVANCES (Fiscalité Locale)
# 1. TAXES & REDEVANCES (Fiscalité Locale)
TAXES = {
    "PROPRETE": {
        "personne_morale": {"label": "Taxe Propreté (Personne Morale)", "prix": 50000},
        "personne_physique": {"label": "Taxe Propreté (Personne Physique)", "prix": 25000},
    },
    "PUBLICITE": {
        "standard": {"label": "Taxe Publicité (Standard 12k)", "prix": 12000},
        "premium": {"label": "Taxe Publicité (Grand Format 15k)", "prix": 15000},
    },
    "ENVIRONNEMENT": {
        "pollution": {"label": "Taxe sur la Pollution", "prix": 50000}, # Valeur par défaut
        "nuisance_sonore": {"label": "Taxe Nuisance Sonore", "prix": 25000}, # Valeur par défaut
    },
    "OCCUPATION_DOMAINE": {
        "box_grand_entreprise": {"label": "Grand Box (Entreprise)", "prix": 150000},
        "box_grand_commercant": {"label": "Grand Box (Commerçant)", "prix": 100000},
        "box_moyen": {"label": "Box Moyen", "prix": 35000},
        "box_petit": {"label": "Petit Box", "prix": 30000},
        "etal": {"label": "Étal de marché", "prix": 6500},
    },
    "DIVERS": {
        "pompes_funebres": {"label": "Taxe Pompes Funèbres", "prix": 10000},
        "transport": {"label": "Taxe Transport (Personnes/Marchandises)", "prix": 5000},
        "pylones": {"label": "Taxe Pylônes Téléphonie", "prix": 500000},
        "terrassement": {"label": "Taxe Terrassement", "prix": 20000},
        "loyers": {"label": "Taxe Loyers", "prix": 5000},
    }
}

# 2. FORMULAIRES & ACTES (État Civil / Administratif)
DOCUMENTS = {
    "ETAT_CIVIL": [
        "Certificat de résidence (adulte)",
        "Certificat d'hébergement",
        "Certificat de transfert de corps",
        "Certificat de célibat",
        "Certificat de coutume",
        "Certificat de non remariage",
        "Procuration",
        "Certificat de concubinage",
        "Certificat de fiançailles",
        "Copie intégrale d'acte de naissance",
        "Transcription d'acte de naissance",
    ],
    "VOYAGE": [
        "Autorisation parentale de voyager",
        "Autorisation maritale de voyager",
    ],
    "PROFESSIONNEL": [
        "Autorisation provisoire d'exercer",
        "Attestation de pouvoirs",
    ],
    "JURIDIQUE_POLICE": [
        "Procès verbal de recherche infructueuse",
        "Procès verbal de recherche fructueuse",
        "Certificat de conformité",
        "Certificat de non conformité",
    ],
    "VEHICULES": [
        "Certificat de vente (véhicule)",
        "Attestation de cessation",
        "Attestation de cession",
    ]
}

# 3. LOCATIONS (Patrimoine)
LOCATIONS = {
    "TRANSPORT": {"label": "Location Transport/Bus", "prix_unitaire": 30000},
    "BUREAUX": {"label": "Location Bureaux", "prix_unitaire": 50000},
    "SALLES": {"label": "Location Salle de Réunion", "prix_unitaire": 25000},
}

def get_all_services():
    """Retourne une liste plate pour affichage dans les menus."""
    services = []
    # Aplatir Taxes
    for cat, items in TAXES.items():
        for key, details in items.items():
            services.append({"type": "TAXE", "categorie": cat, "nom": details['label'], "prix": details['prix']})
    
    # Aplatir Documents (Prix fictifs par défaut si non spécifiés, ex: 1000 FCFA)
    for cat, items in DOCUMENTS.items():
        for item in items:
            services.append({"type": "ACTE", "categorie": cat, "nom": item, "prix": 2000}) # Prix par défaut actes
            
    # Aplatir Locations
    for key, details in LOCATIONS.items():
        services.append({"type": "LOCATION", "categorie": "PATRIMOINE", "nom": details['label'], "prix": details['prix_unitaire']})
        
    return services
