# ai_forecast.py - Module de prédiction IA pour les stocks

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import random

# Génération de données historiques simulées (car on n'a pas encore assez d'historique réel)
def generate_fake_history(matiere, days=90):
    """Génère un historique de consommation cohérent pour une matière."""
    dates = [datetime.now() - timedelta(days=i) for i in range(days)]
    dates.reverse()
    
    # Simulation: stock qui baisse (consommation) et remonte (réapprovisionnement)
    stock_levels = []
    current_stock = 100
    daily_consumption_base = random.uniform(2, 8) # Consommation moyenne par jour
    
    data = []
    
    for date in dates:
        # Variation aléatoire de la consommation
        consumption = max(0, np.random.normal(daily_consumption_base, 1.5))
        
        current_stock -= consumption
        
        # Réapprovisionnement si stock bas
        if current_stock < 15:
            current_stock += random.randint(50, 100)
            
        data.append({
            "date": date,
            "stock": current_stock,
            "consumption": consumption,
            "matiere": matiere
        })
        
    return pd.DataFrame(data)


def predict_stock_depletion(matiere):
    """
    Prédit la date de rupture de stock pour une matière donnée.
    Utilise une régression linéaire sur les 30 derniers jours.
    """
    # 1. Obtenir/Générer les données
    df = generate_fake_history(matiere)
    
    # On prend les 30 derniers jours pour la tendance récente
    recent_df = df.tail(30).copy()
    
    # Préparer les données pour Scikit-Learn
    # X = jours écoulés depuis le début de la période récente
    recent_df['days_passed'] = (recent_df['date'] - recent_df['date'].min()).dt.days
    
    X = recent_df[['days_passed']]
    y = recent_df['stock']
    
    # 2. Entraîner le modèle
    model = LinearRegression()
    model.fit(X, y)
    
    # 3. Prédire quand le stock sera à 0
    # y = ax + b  =>  0 = ax + b  =>  x = -b / a
    slope = model.coef_[0]
    intercept = model.intercept_
    
    if slope >= 0:
        return {
            "days_until_empty": float('inf'),
            "predicted_date": None,
            "status": "STABLE", # Le stock monte ou stagne
            "slope": slope,
            "history": df
        }
        
    days_until_zero = -intercept / slope
    
    # Date actuelle (relative aux données d'entraînement)
    current_day_index = recent_df['days_passed'].max()
    remaining_days = days_until_zero - current_day_index
    
    if remaining_days < 0:
        predicted_date = datetime.now() # Déjà en rupture théorique
    else:
        predicted_date = datetime.now() + timedelta(days=remaining_days)
        
    return {
        "days_until_empty": max(0, round(remaining_days, 1)),
        "predicted_date": predicted_date,
        "status": "CRITICAL" if remaining_days < 7 else "OK",
        "slope": slope,
        "history": df
    }

def get_revenue_history(days=90):
    """
    Récupère l'historique des recettes (Taxes + Actes) depuis la base de données.
    Si pas assez de données, génère une simulation réaliste.
    """
    # Import local pour éviter boucle
    import database as db
    
    conn = db.get_connection()
    c = conn.cursor()
    
    # Récupérer les transactions de type TAXE ou ACTE
    c.execute('''
        SELECT date(date_creation) as day, SUM(montant) as total 
        FROM transactions 
        WHERE type LIKE 'TAXE%' OR type LIKE 'ACTE%'
        GROUP BY day 
        ORDER BY day ASC
    ''')
    rows = c.fetchall()
    conn.close()
    
    df = pd.DataFrame(rows, columns=['date', 'revenue'])
    
    # Si pas assez de données (moins de 3 jours), on complète avec de la simulation
    # Sinon on utilise les vraies données
    if len(df) < 3:
        # Toujours ajouter les vraies données si elles existent
        real_data = df.to_dict('records') if not df.empty else []
        
        dates = [datetime.now().date() - timedelta(days=i) for i in range(days)]
        dates.reverse()
        
        simulated_data = []
        for d in dates:
            # Recette aléatoire entre 5000 et 25000 FCFA avec tendance
            base = 15000
            noise = random.randint(-5000, 10000)
            trend = (days - len(simulated_data)) * 50
            
            simulated_data.append({
                "date": d,
                "revenue": max(2000, base + noise + trend)
            })
        
        # Fusionner simulation et vraies données
        combined = simulated_data + real_data
        return pd.DataFrame(combined)
        
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df

def predict_revenue():
    """Prédit les recettes futures."""
    df = get_revenue_history()
    
    # Préparation données
    df['date'] = pd.to_datetime(df['date'])
    df['days_passed'] = (df['date'] - df['date'].min()).dt.days
    
    X = df[['days_passed']]
    y = df['revenue']
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Prédiction sur 30 jours futurs
    last_day = df['days_passed'].max()
    future_days = np.array(range(last_day + 1, last_day + 31)).reshape(-1, 1)
    future_revenue = model.predict(future_days)
    
    future_dates = [df['date'].max() + timedelta(days=i) for i in range(1, 31)]
    
    future_df = pd.DataFrame({
        "date": future_dates,
        "revenue": future_revenue,
        "type": "PREDICTION"
    })
    
    df['type'] = "HISTORIQUE"
    
    # Tendance
    slope = model.coef_[0]
    trend = "HAUSSIERE" if slope > 0 else "BAISSIERE"
    
    return {
        "history": df,
        "forecast": future_df,
        "trend": trend,
        "slope": slope,
        "expected_revenue_30d": future_revenue.sum()
    }
