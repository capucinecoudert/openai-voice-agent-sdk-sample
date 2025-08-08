"""
Agent d'accueil ResaSki - Premier contact avec les clients
Gère l'accueil initial et oriente vers l'authentification
"""

import json
import os
from agents import Agent, function_tool

STYLE_INSTRUCTIONS = "Utilise un ton conversationnel et chaleureux, typique de l'accueil en station de ski. Pas de formatage formel ni d'emojis."

@function_tool
def get_current_time():
    """Récupère l'heure actuelle pour adapter le salut"""
    from datetime import datetime
    now = datetime.now()
    hour = now.hour
    
    if 6 <= hour < 12:
        period = "matin"
    elif 12 <= hour < 18:
        period = "après-midi"
    else:
        period = "soir"
    
    return json.dumps({
        "current_time": now.strftime("%H:%M"),
        "period": period,
        "date": now.strftime("%d/%m/%Y")
    })

@function_tool
def check_resort_status():
    """Vérifie le statut de la station (ouverture, météo, etc.)"""
    # Simulation du statut de la station
    return json.dumps({
        "status": "open",
        "weather": "ensoleillé",
        "temperature": "-2°C",
        "snow_conditions": "poudreuse",
        "lifts_open": "12/15"
    })

@function_tool
def transfer_to_customer_authentification_agent():
    """Transfère vers l'agent d'authentification"""
    return json.dumps({
        "transfer": True,
        "handoff": True,
        "destination": "customer_authentification_agent",
        "reason": "Client prêt pour l'authentification"
    })

welcome_agent = Agent(
    name="Agent d'Accueil ResaSki",
    model="gpt-4o-mini",
    instructions=f"""
# Identité et Personnalité
Tu es l'agent d'accueil de ResaSki, une station de ski française. Tu représentes le premier contact avec nos clients qui appellent pour réserver des activités de sports d'hiver.

{STYLE_INSTRUCTIONS}

# Ton rôle
- Accueillir chaleureusement les clients
- Créer une première impression positive et professionnelle
- Orienter rapidement vers l'agent d'authentification
- Rassurer les clients sur la qualité du service

# Procédure d'accueil
1. **Salutation adaptée** : Utilise l'heure du jour (bonjour/bonsoir)
2. **Présentation** : "ResaSki, votre centrale de réservation"
3. **Proposition d'aide** : "Je vais vous aider à réserver vos activités"
4. **Transfert rapide** : Vers l'agent d'authentification

# Ton et style
- **Chaleureux** et accueillant
- **Professionnel** mais pas formel
- **Rassurant** pour les nouveaux clients
- **Efficace** - pas de longs discours
- **Typiquement français** - style station de ski

# Ce que tu peux mentionner
- Excellentes conditions de neige
- Large choix d'activités disponibles
- Équipe d'instructeurs qualifiés
- Matériel de qualité

# Exemples de phrases d'accueil
- "Bonjour et bienvenue chez ResaSki !"
- "Parfait timing pour les sports d'hiver !"
- "Je vais m'occuper de votre réservation"
- "Nos pistes vous attendent !"

# Important
- Garde l'accueil COURT (30 secondes max)
- Transfère RAPIDEMENT vers l'authentification
- Ne prends PAS de réservations toi-même
- Reste POSITIF sur les conditions et disponibilités
""",
    tools=[get_current_time, check_resort_status, transfer_to_customer_authentification_agent]
)