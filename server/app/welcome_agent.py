"""
Agent d'accueil ResaSki - Premier contact avec les clients
Gère l'accueil initial et oriente vers l'authentification
"""

import json
import os
from agents import Agent, function_tool
from datetime import datetime
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

STYLE_INSTRUCTIONS = "Professionnel mais chaleureux et accueillant. Parler clairement et à un rythme modéré. Être patient et rassurer sur la simplicité du processus."

@function_tool
def get_vendor_info():
    """Récupère les informations de base du vendeur (nom de l'école) pour personnaliser l'accueil"""
    import requests
    
    try:
        base_url = os.getenv("NEXT_PUBLIC_API_BASE_URL")
        vendor_id = int(os.getenv("NEXT_PUBLIC_VENDOR_ID", "4"))
        
        print(f'🔍 DEBUG - get_vendor_info called')
        print(f'📥 Input vendor_id: {vendor_id}')
        print(f'🏫 Fetching vendor info for ID: {vendor_id}')
        
        full_url = f"{base_url}/vendors/{vendor_id}"
        print(f'🌐 Full URL: {full_url}')
        
        response = requests.get(
            full_url,
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true'
            },
            timeout=30
        )
        
        print(f'📡 Response status: {response.status_code}')
        
        if response.status_code != 200:
            raise Exception(f"HTTP error! status: {response.status_code}")
        
        result = response.json()
        print(f'📄 API response: {json.dumps(result, indent=2)}')
        
        if result and result.get('name'):
            print('✅ Vendor info retrieved successfully')
            return json.dumps({
                "success": True,
                "vendor_name": result['name'],
                "vendor_info": result,
                "message": f"Informations récupérées pour l'école : {result['name']}"
            })
        else:
            print('❌ No vendor name found in response')
            return json.dumps({
                "success": False,
                "vendor_name": "notre école",
                "message": "Impossible de récupérer le nom de l'école, utilisation du nom générique"
            })
            
    except Exception as e:
        print(f'💥 Error in get_vendor_info: {e}')
        return json.dumps({
            "success": False,
            "vendor_name": "notre école",
            "message": f"Erreur lors de la récupération des informations : {str(e)}"
        })

@function_tool
def get_current_time():
    """Récupère l'heure actuelle pour adapter le salut"""
    now = datetime.now()
    hour = now.hour
    
    if 6 <= hour < 12:
        period = "matin"
        greeting = "Bonjour"
    elif 12 <= hour < 18:
        period = "après-midi"
        greeting = "Bonjour"
    else:
        period = "soir"
        greeting = "Bonsoir"
    
    return json.dumps({
        "current_time": now.strftime("%H:%M"),
        "period": period,
        "greeting": greeting,
        "date": now.strftime("%d/%m/%Y")
    })

@function_tool
def transfer_to_customer_identification_agent():
    """Transfère vers l'agent d'identification des clients pour démarrer le processus de réservation"""
    return json.dumps({
        "transfer": True,
        "handoff": True,
        "destination": "Agent d'Authentification ResaSki",  # Nom exact de l'agent
        "reason": "Client prêt pour l'identification et le processus de réservation"
    })

@function_tool
def transfer_to_information_desk_agent():
    """Transfère vers l'agent d'information pour plus de détails sur l'école et les services"""
    return json.dumps({
        "transfer": True,
        "handoff": True,
        "destination": "Agent d'Information ResaSki",  # Nom exact de l'agent
        "reason": "Client souhaite plus d'informations avant de commencer la réservation"
    })

welcome_agent = Agent(
    name="Agent d'Accueil ResaSki",
    model="gpt-4o-mini",
    instructions=f"""
# Identité et Mission
Vous êtes l'agent d'accueil virtuel de notre école de ski/centre d'activités ResaSki. Vous représentez le premier contact avec nos clients.

{RECOMMENDED_PROMPT_PREFIX}
{STYLE_INSTRUCTIONS}

# COMPORTEMENT AU LANCEMENT - PROCÉDURE STRICTE :

## 1. RÉCUPÉRATION IMMÉDIATE DES INFOS
- **APPELER IMMÉDIATEMENT** `get_vendor_info()` dès le début de la conversation
- Récupérer le nom de l'école pour personnaliser l'accueil

## 2. ACCUEIL PERSONNALISÉ
Une fois le nom de l'école obtenu :
- Utiliser `get_current_time()` pour adapter le salut (Bonjour/Bonsoir)
- Dire : "[Bonjour/Bonsoir] et bienvenue dans l'école [nom de l'école] ! Je suis l'assistant de réservation automatique."

## 3. PRÉSENTATION DU PROCESSUS DE RÉSERVATION
Expliquer clairement le processus en 5 étapes :

"Voici comment se déroule le processus de réservation :
1. Je vais d'abord vous identifier ou créer votre profil client
2. Puis, nous sélectionnerons ensemble un cours selon vos critères  
3. Ensuite, nous sélectionnerons les profils des participants
4. Nous procéderons à l'inscription au cours choisi
5. Finalement, vous recevrez un lien de paiement par email pour finaliser

Souhaitez-vous commencer le processus de réservation ou souhaitez-vous d'abord plus d'informations sur notre école et nos services ?"

## 4. ACTIONS SELON LA RÉPONSE

### SI "OUI" ou équivalent :
- Utiliser `transfer_to_customer_identification_agent()`
- Dire : "Parfait ! Je vous transfère vers notre service d'identification."

### SI "NON" ou demandes d'informations :
- Utiliser `transfer_to_information_desk_agent()`  
- Dire : "Je vous transfère vers notre service d'information."

### SI INCERTAIN ou questions sur le processus :
- Réexpliquer brièvement le processus
- Rassurer sur la simplicité
- Redemander : "Souhaitez-vous que nous commencions ?"

# COLLECTE D'INFORMATIONS OPTIONNELLE
- Si la personne donne son prénom, l'utiliser pour personnaliser
- Exemple : "Parfait [Prénom] ! Commençons le processus."

# RÈGLES IMPORTANTES
- **TOUJOURS** appeler `get_vendor_info()` en premier
- **TOUJOURS** présenter les 5 étapes du processus
- **ÊTRE PATIENT** et rassurer sur la simplicité
- **TRANSFÉRER RAPIDEMENT** selon la réponse
- Utiliser un **ton chaleureux** mais professionnel
- **NE PAS** prendre de réservations directement

# PHRASES D'EXEMPLE
- "Bonjour et bienvenue chez [Nom École] !"
- "Le processus est très simple et guidé"
- "Pas d'inquiétude, je vais vous accompagner"
- "Souhaitez-vous que nous commencions ?"

# GESTION DES CAS PARTICULIERS
- Si erreur de récupération du nom → utiliser "notre école de ski"
- Si client pressé → rassurer sur la rapidité du processus
- Si client hésitant → expliquer les avantages de la réservation guidée
""",
    tools=[
        get_vendor_info,
        get_current_time,
        # transfer_to_customer_identification_agent,
        # transfer_to_information_desk_agent
    ]
)

# Export explicite
__all__ = ["welcome_agent"]