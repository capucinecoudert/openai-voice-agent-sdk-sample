"""
Agent d'information générale ResaSki
Renseigne sur l'école, les sports proposés, la météo et les services pratiques
"""

import json
import os
import requests
from agents import Agent, function_tool
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

STYLE_INSTRUCTIONS = "Ton professionnel mais amical, chaleureux, patient et passionné de sports de montagne. Utiliser des phrases courtes et un rythme modéré."

@function_tool
def get_vendor_info(vendor_id: int = None):
    """Récupère les informations générales du vendor (nom, localisation, zip_code, etc.)"""
    try:
        base_url = os.getenv("NEXT_PUBLIC_API_BASE_URL")
        vendor_id = vendor_id or int(os.getenv("NEXT_PUBLIC_VENDOR_ID", "4"))
        
        print(f'🏫 DEBUG - get_vendor_info called for vendor_id: {vendor_id}')
        
        url = f"{base_url}/vendors/{vendor_id}"
        print(f'🌐 URL: {url}')
        
        response = requests.get(
            url,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            },
            timeout=30
        )
        
        print(f'📡 Response status: {response.status_code}')
        
        if not response.ok:
            return json.dumps({
                "success": False, 
                "message": "Impossible de récupérer les informations de l'école."
            })
        
        data = response.json()
        print(f'📄 Vendor data received: {json.dumps(data, indent=2)}')
        
        return json.dumps({
            "success": True, 
            "vendor": data,
            "message": f"Informations récupérées pour {data.get('name')}" 
        })
 
        
    except Exception as e:
        print(f'💥 Error in get_vendor_info: {e}')
        return json.dumps({
            "success": False, 
            "message": f"Erreur lors de la récupération des informations : {str(e)}"
        })

@function_tool
def get_vendor_sports(vendor_id: int = None):
    """Liste tous les sports proposés par le vendor"""
    try:
        base_url = os.getenv("NEXT_PUBLIC_API_BASE_URL")
        vendor_id = vendor_id or int(os.getenv("NEXT_PUBLIC_VENDOR_ID", "4"))
        
        print(f'🎿 DEBUG - get_vendor_sports called for vendor_id: {vendor_id}')
        
        url = f"{base_url}/sports?vendor_id={vendor_id}"
        print(f'🌐 URL: {url}')
        
        response = requests.get(
            url,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            },
            timeout=30
        )
        
        print(f'📡 Response status: {response.status_code}')
        
        if not response.ok:
            return json.dumps({
                "success": False, 
                "message": "Impossible de récupérer la liste des sports."
            })
        
        data = response.json()
        print(f'📄 Sports data received: {json.dumps(data, indent=2)}')
        
        # Extraire les noms des sports pour faciliter les recherches
        sport_names = []
        if isinstance(data, list):
            sport_names = [sport.get('name', sport.get('sport_name', '')) for sport in data if sport.get('name') or sport.get('sport_name')]
        
        return json.dumps({
            "success": True, 
            "sports": data,
            "sport_names": sport_names,
            "count": len(data) if isinstance(data, list) else 0,
            "message": f"{len(sport_names)} sports proposés dans notre école"
        })
        
    except Exception as e:
        print(f'💥 Error in get_vendor_sports: {e}')
        return json.dumps({
            "success": False, 
            "message": f"Erreur lors de la récupération des sports : {str(e)}"
        })


@function_tool
def transfer_to_customer_authentification_agent():
    """Transfère vers l'agent d'identification pour démarrer le processus de réservation"""
    return json.dumps({
        "transfer": True,
        "handoff": True,
        "destination": "Agent d'Authentification ResaSki", 
        "reason": "Client prêt à commencer le processus de réservation"
    })

information_desk_agent = Agent(
    name="Agent d'Information ResaSki",
    model="gpt-4o-mini",
    instructions=f"""
# Personnalité et Mission
Vous êtes l'agent d'information ResaSki, chaleureux, patient et passionné de sports de montagne. 
Vous connaissez parfaitement l'école, ses activités et la vie en station.
{RECOMMENDED_PROMPT_PREFIX}
{STYLE_INSTRUCTIONS}

# Votre rôle principal
- Informer sur l'école, les sports proposés, la météo locale
- Répondre aux questions pratiques sur l'équipement et services
- Orienter vers les bons agents selon les besoins

# PROCÉDURE DE PRISE EN CHARGE

## 1. Accueil informationnel
- "Je peux vous renseigner sur nos activités, la météo, l'équipement ou tout autre aspect pratique."
- "Que souhaitez-vous savoir ?"

## 2. Traitement des demandes courantes

### Informations sur l'école
- Utiliser `get_vendor_info()` pour nom, localisation, services
- Présenter de façon chaleureuse et accueillante

### Sports et activités
- Utiliser `get_vendor_sports()` pour lister tous les sports disponibles
- Présenter les sports de manière organisée et attrayante
- Mentionner les sports populaires en premier (Ski Alpin, Snowboard)

### Questions pratiques
- Accès : donner les informations de localisation
- Contact : email, téléphone, horaires

## 3. Orientation vers d'autres agents

### Si demande de réservation
- "Pour effectuer une réservation, je vous transfère vers notre service spécialisé"
- Utiliser `transfer_to_customer_authentification_agent()`

# Exemples de réponses types

## Sports disponibles (utiliser les données API réelles)
"Nous proposons une large gamme d'activités de montagne :

**Sports de glisse principaux :**
- Ski Alpin (cours tous niveaux)
- Snowboard (du débutant à l'expert)
- Ski Nordique

**Activités outdoor :**
- Raquettes à neige
- Randonnée Nordique
- Trail et VTT

**Spécialités :**
- Biathlon
- Télémark
- Cascade de glace

Et bien d'autres activités ! Quel sport vous intéresse le plus ?"

## Localisation
"Notre école ESI De Métabief se situe au 9 Place Xavier Authier, à Métabief (25370). 
Nous sommes facilement accessibles depuis le centre station.
Téléphone : +33 3 81 49 25 11
Email : metabief@ecoledeski.fr"

# RÈGLES IMPORTANTES
- **TOUJOURS** utiliser les vraies données de l'API vendor et sports
- **PRÉSENTER** les sports de manière attractive et organisée
- **ÊTRE PATIENT** et rassurer les clients
- **ORIENTER** efficacement vers les bons services
- Utiliser un **ton passionné** pour les sports de montagne
- **PERSONNALISER** selon les informations vendor récupérées

# Gestion des cas particuliers
- Si erreur API : "Un instant, je vérifie ces informations pour vous..."
- Si sport non disponible : proposer des alternatives disponibles
- Si question hors périmètre : orienter vers l'agent approprié
- Si client pressé : aller à l'essentiel puis orienter

# IMPORTANT : Transférer vers l'authentification
Dès qu'un client exprime le souhait de réserver :
"Parfait ! Je vous transfère maintenant vers notre agent de réservation pour commencer votre authentification."
""",
    tools=[
        get_vendor_info,
        get_vendor_sports,
        transfer_to_customer_authentification_agent
    ]
)

# Export explicite
__all__ = ["information_desk_agent"]