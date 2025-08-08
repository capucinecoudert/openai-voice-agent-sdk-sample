"""
Agent d'authentification client ResaSki
Gère l'identification et la création de comptes clients
"""

import json
import os
import requests
import phonenumbers
from phonenumbers import carrier, geocoder
from agents import Agent, function_tool
import urllib.parse

@function_tool
def normalize_phone_number(phone_input: str, country_code: str = None):
    """
    Normalise un numéro de téléphone avec gestion des préfixes internationaux
    """
    try:
        # Nettoyer l'input de base
        clean_input = phone_input.replace(" ", "").replace("-", "").replace(".", "").replace("(", "").replace(")", "")
        
        print(f"📱 Processing: '{phone_input}' → '{clean_input}'")
        
        # Cas 1: Numéro avec préfixe international explicite (+XX)
        if clean_input.startswith("+"):
            try:
                parsed = phonenumbers.parse(clean_input, None)
                if phonenumbers.is_valid_number(parsed):
                    normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                    country = geocoder.description_for_number(parsed, "fr")
                    
                    return json.dumps({
                        "success": True,
                        "normalized": normalized,
                        "original": phone_input,
                        "country": country,
                        "country_code": f"+{parsed.country_code}",
                        "message": f"Numéro normalisé: {normalized} ({country})"
                    })
                else:
                    return json.dumps({
                        "success": False,
                        "error": "invalid_number",
                        "message": "Ce numéro de téléphone n'est pas valide."
                    })
            except phonenumbers.NumberParseException:
                return json.dumps({
                    "success": False,
                    "error": "parse_error",
                    "message": "Format de numéro invalide. Exemple: +33 7 81 60 23 52"
                })
        
        # Cas 2: Numéro sans préfixe - utiliser le pays fourni ou demander
        else:
            if country_code:
                try:
                    # Convertir le code pays en région (ex: +33 → FR, +41 → CH)
                    country_code_num = country_code.replace("+", "")
                    region = None
                    
                    # Mapping des codes principaux
                    country_mapping = {
                        "33": "FR",  # France
                        "41": "CH",  # Suisse
                        "32": "BE",  # Belgique
                        "39": "IT",  # Italie
                        "49": "DE",  # Allemagne
                        "34": "ES",  # Espagne
                        "1": "US",   # USA/Canada
                        "44": "GB",  # UK
                    }
                    
                    region = country_mapping.get(country_code_num)
                    
                    if region:
                        # Préfixer avec le code pays si nécessaire
                        full_number = f"+{country_code_num}{clean_input}"
                        parsed = phonenumbers.parse(full_number, None)
                        
                        if phonenumbers.is_valid_number(parsed):
                            normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                            country_name = geocoder.description_for_number(parsed, "fr")
                            
                            return json.dumps({
                                "success": True,
                                "normalized": normalized,
                                "original": phone_input,
                                "country": country_name,
                                "country_code": f"+{parsed.country_code}",
                                "message": f"Numéro normalisé: {normalized} ({country_name})"
                            })
                    
                    return json.dumps({
                        "success": False,
                        "error": "unsupported_country",
                        "message": f"Code pays {country_code} non supporté ou invalide."
                    })
                    
                except Exception as e:
                    return json.dumps({
                        "success": False,
                        "error": "normalization_error",
                        "message": f"Erreur lors de la normalisation: {str(e)}"
                    })
            else:
                # Pas de code pays fourni - essayer France par défaut, sinon demander
                try:
                    # Essai avec France par défaut
                    if clean_input.startswith("0"):
                        # Format français local
                        full_number = f"+33{clean_input[1:]}"
                        parsed = phonenumbers.parse(full_number, None)
                        
                        if phonenumbers.is_valid_number(parsed):
                            normalized = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                            
                            return json.dumps({
                                "success": True,
                                "normalized": normalized,
                                "original": phone_input,
                                "country": "France",
                                "country_code": "+33",
                                "assumed_country": True,
                                "message": f"Numéro français normalisé: {normalized}"
                            })
                    
                    # Si ça ne marche pas, demander le pays
                    return json.dumps({
                        "success": False,
                        "error": "country_needed",
                        "message": "Je n'arrive pas à identifier le pays. Quel est votre indicatif pays ? (ex: +33 pour France, +41 pour Suisse)",
                        "common_codes": {
                            "+33": "France",
                            "+41": "Suisse", 
                            "+32": "Belgique",
                            "+39": "Italie",
                            "+49": "Allemagne",
                            "+1": "USA/Canada",
                            "+44": "Royaume-Uni"
                        }
                    })
                    
                except Exception:
                    return json.dumps({
                        "success": False,
                        "error": "country_needed",
                        "message": "Format non reconnu. Pouvez-vous me donner votre numéro avec l'indicatif pays ? (ex: +33 7 81 60 23 52)"
                    })
                    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": "general_error",
            "message": f"Erreur lors du traitement: {str(e)}"
        })

@function_tool
def search_customers_by_phone(phone_number: str):
    """Recherche client par numéro de téléphone normalisé"""
    base_url = os.getenv("NEXT_PUBLIC_API_BASE_URL")
    vendor_id = os.getenv("NEXT_PUBLIC_VENDOR_ID")
    
    # ✅ AJOUT : Validation des variables d'environnement
    if not base_url:
        return json.dumps({
            "error": True,
            "message": "Variable NEXT_PUBLIC_API_BASE_URL non définie"
        })
    
    if not vendor_id:
        return json.dumps({
            "error": True,
            "message": "Variable NEXT_PUBLIC_VENDOR_ID non définie"
        })
    
    try:
        print(f"🔍 [DEBUG] Searching for phone: {phone_number}")
        print(f"🌐 [DEBUG] API URL: {base_url}/customers/search-by-phone")
        print(f"🏢 [DEBUG] Vendor ID: {vendor_id}")
        
        # ✅ Construction de l'URL et des paramètres
        url = f"{base_url}/customers/search-by-phone"
        params = {
            "vendor_id": vendor_id, 
            "phone": phone_number
        }
        
        print(f"📡 [DEBUG] Full URL before request: {url}")
        print(f"📊 [DEBUG] Params: {params}")
        
        response = requests.get(
            url,
            params=params,
            headers={"ngrok-skip-browser-warning": "true"},
            timeout=30
        )
        
        print(f"📡 [DEBUG] Actual URL called: {response.url}")
        print(f"📡 [DEBUG] Response status: {response.status_code}")
        print(f"📄 [DEBUG] Response headers: {dict(response.headers)}")
        print(f"📄 [DEBUG] Raw response text: {response.text}")
        
        # ✅ Vérification explicite du statut
        if response.status_code == 404:
            print("❌ [DEBUG] 404 - No customer found")
            return json.dumps({
                "found": False, 
                "phone_number": phone_number,
                "message": f"Aucun client trouvé avec le numéro {phone_number} (404)"
            })
        
        if response.status_code != 200:
            print(f"❌ [DEBUG] Unexpected status code: {response.status_code}")
            return json.dumps({
                "error": True,
                "message": f"Erreur API: status {response.status_code}"
            })
            
        # ✅ Parsing de la réponse JSON
        try:
            data = response.json()
            print(f"✅ [DEBUG] JSON parsed successfully: {data}")
        except json.JSONDecodeError as e:
            print(f"❌ [DEBUG] JSON parsing error: {e}")
            return json.dumps({
                "error": True,
                "message": f"Erreur parsing JSON: {str(e)}"
            })
        
        # ✅ Traitement de la réponse
        if isinstance(data, list):
            print(f"📋 [DEBUG] Response is a list with {len(data)} items")
            
            if len(data) == 0:
                print("📋 [DEBUG] Empty list - no customers found")
                return json.dumps({
                    "found": False, 
                    "phone_number": phone_number,
                    "message": f"Aucun client trouvé avec le numéro {phone_number} (liste vide)"
                })
            
            elif len(data) == 1:
                # ✅ Un seul client trouvé
                customer = data[0]
                print(f"👤 [DEBUG] Single customer found: {customer}")
                
                return json.dumps({
                    "found": True,
                    "single_match": True,
                    "customer": {
                        "id": customer.get("id"),
                        "first_name": customer.get("first_name"),
                        "last_name": customer.get("last_name"),
                        "email": customer.get("email"),
                        "phone": customer.get("phone", phone_number)
                    },
                    "message": f"Client trouvé: {customer.get('first_name')} {customer.get('last_name')} ({customer.get('email')})"
                })
            
            else:
                # ✅ Plusieurs clients
                print(f"👥 [DEBUG] Multiple customers found: {len(data)}")
                customers_list = []
                for customer in data:
                    customers_list.append({
                        "id": customer.get("id"),
                        "first_name": customer.get("first_name"),
                        "last_name": customer.get("last_name"),
                        "email": customer.get("email"),
                        "phone": customer.get("phone", phone_number)
                    })
                
                return json.dumps({
                    "found": True,
                    "multiple_matches": True,
                    "count": len(data),
                    "customers": customers_list,
                    "message": f"Plusieurs comptes trouvés avec ce numéro ({len(data)} comptes). Je vais avoir besoin de votre email pour vous identifier précisément.",
                    "action_required": "ask_email"
                })
        
        elif isinstance(data, dict):
            print(f"📄 [DEBUG] Response is a dict: {data}")
            return json.dumps({
                "found": True,
                "single_match": True,
                "customer": {
                    "id": data.get("id"),
                    "first_name": data.get("first_name"),
                    "last_name": data.get("last_name"),
                    "email": data.get("email"),
                    "phone": data.get("phone", phone_number)
                },
                "message": f"Client trouvé: {data.get('first_name')} {data.get('last_name')} ({data.get('email')})"
            })
        
        else:
            print(f"❌ [DEBUG] Unexpected data type: {type(data)}")
            return json.dumps({
                "found": False, 
                "phone_number": phone_number,
                "message": f"Format de réponse inattendu: {type(data)}"
            })
            
    except requests.Timeout:
        print("❌ [DEBUG] Request timeout")
        return json.dumps({
            "error": True, 
            "message": "Délai d'attente dépassé. Veuillez réessayer."
        })
    except requests.RequestException as e:
        print(f"❌ [DEBUG] Request exception: {e}")
        return json.dumps({
            "error": True, 
            "message": f"Erreur de connexion: {str(e)}"
        })
    except Exception as e:
        print(f"❌ [DEBUG] Unexpected exception: {e}")
        import traceback
        traceback.print_exc()
        return json.dumps({
            "error": True, 
            "message": f"Erreur inattendue: {str(e)}"
        })

@function_tool
def search_customer_by_email(email: str):
    """Recherche client par email validé"""
    base_url = os.getenv("NEXT_PUBLIC_API_BASE_URL")
    vendor_id = os.getenv("NEXT_PUBLIC_VENDOR_ID")
    
    try:
        clean_email = email.lower().strip()
        
        response = requests.get(
            f"{base_url}/customers/search-by-email",
            params={"vendor_id": vendor_id, "email": clean_email},
            headers={"ngrok-skip-browser-warning": "true"},
            timeout=30
        )
        
        if response.status_code == 404:
            return json.dumps({
                "found": False,
                "email": clean_email,
                "message": "Aucun client trouvé avec cet email"
            })
            
        response.raise_for_status()
        customer = response.json()
        
        return json.dumps({
            "found": True,
            "customer": {
                "id": customer.get("id"),
                "first_name": customer.get("first_name"),
                "last_name": customer.get("last_name"),
                "email": customer.get("email"),
                "phone": customer.get("phone")
            },
            "message": f"Client trouvé: {customer.get('first_name')} {customer.get('last_name')}"
        })
        
    except requests.RequestException as e:
        return json.dumps({"error": True, "message": f"Erreur de connexion: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": True, "message": f"Erreur: {str(e)}"})

@function_tool
def validate_email_format(email: str):
    """Valide le format d'un email épelé"""
    import re
    
    # Nettoyer l'email épelé
    clean_email = email.replace(" ", "").replace("point", ".").replace("arobase", "@").lower()
    
    # Validation format email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = re.match(email_pattern, clean_email) is not None
    
    return json.dumps({
        "valid": is_valid,
        "cleaned_email": clean_email,
        "original": email
    })

@function_tool
def create_customer(vendor_id: str, first_name: str, last_name: str, email: str, phone_number: str, date_of_birth: str):
    """Crée un nouveau client avec toutes les informations collectées"""
    base_url = os.getenv("NEXT_PUBLIC_API_BASE_URL")
    
    try:
        customer_data = {
            "vendor_id": int(vendor_id),
            "first_name": first_name.strip().title(),
            "last_name": last_name.strip().upper(),
            "email": email.lower().strip(),
            "phone_number": phone_number.replace(" ", "").replace("-", ""),
            "date_of_birth": date_of_birth
        }
        
        response = requests.post(
            f"{base_url}/customers/",
            json=customer_data,
            headers={"ngrok-skip-browser-warning": "true"},
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        return json.dumps({
            "success": True,
            "customer_id": result.get("customer", {}).get("id"),
            "customer": result.get("customer"),
            "message": f"Compte créé pour {customer_data['first_name']} {customer_data['last_name']}"
        })
        
    except requests.RequestException as e:
        return json.dumps({"error": True, "message": f"Erreur de création: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": True, "message": f"Erreur: {str(e)}"})

@function_tool
def transfer_to_product_consultation(customer_id: str, customer_info: str):
    """Transfère vers l'agent de consultation produits"""
    return json.dumps({
        "transfer": True,
        "destination": "product_consultation_agent",
        "customer_id": customer_id,
        "customer_info": customer_info,
        "reason": "Client authentifié, prêt pour la consultation produits"
    })

customer_authentification_agent = Agent(
    name="Agent d'Authentification ResaSki",
    model="gpt-4o-mini",
    instructions="""
PRISE DE RELAIS AUTOMATIQUE
Dès que tu prends le relais de l'agent d'accueil, tu dois IMMÉDIATEMENT commencer par :

"Parfait ! Je vais maintenant m'occuper de votre authentification. Pour commencer, quel est votre numéro de téléphone ?"

# IMPORTANT
- NE PAS attendre que le client demande quelque chose
- NE PAS dire "Que puis-je faire pour vous ?"
- PRENDRE L'INITIATIVE immédiatement
- COMMENCER par demander le numéro de téléphone


# Identité et Mission
Tu es l'agent d'authentification de ResaSki. Tu gères l'identification des clients internationaux.

# Procédure de collecte du numéro de téléphone

## 1. Demande initiale
- "Quel est votre numéro de téléphone ?"
- Accepte TOUS les formats : 
  - Français: "07 81 60 23 52" ou "0781602352"
  - International: "+41 7 81 60 23 52" ou "+33781602352"
  - Autres pays: "+1 555 123 4567"

## 2. Normalisation automatique
- Utilise `normalize_phone_number` pour traiter le numéro
- Gère automatiquement les différents préfixes internationaux

## 3. Gestion des cas spéciaux

### Cas A: Numéro avec préfixe international (+XX)
- Normalisation automatique
- Confirmation: "J'ai normalisé votre numéro: +33781602352 (France)"

### Cas B: Numéro sans préfixe
- Si format français (commence par 0): assume France (+33)
- Sinon: demande le code pays
- "Quel est votre indicatif pays ? Par exemple +33 pour France, +41 pour Suisse"

### Cas C: Code pays inconnu ou invalide
- Propose une liste des codes courants
- "Voici les codes les plus courants: +33 (France), +41 (Suisse), +32 (Belgique)..."

## 4. Confirmation et recherche
- Confirme toujours le numéro normalisé
- Utilise `search_customers_by_phone` avec le numéro au format E164
- Exemple: "+33781602352"

## 5. Gestion d'erreurs
- Format invalide: "Ce format n'est pas reconnu, pouvez-vous le donner avec l'indicatif pays ?"
- Pays non supporté: "Ce code pays n'est pas dans notre système, essayez un autre numéro"
- Erreur réseau: "Problème de connexion, un instant..."

# Règles importantes
- **TOUJOURS** normaliser au format E164 (+XXXXXXXXXXXX)
- **ACCEPTER** tous les formats internationaux
- **DEMANDER** le code pays si nécessaire
- **CONFIRMER** le numéro normalisé avant recherche
- Être **patient** avec les formats non standards

# Exemples de gestion
- Input: "07 81 60 23 52" → Output: "+33781602352"
- Input: "+41 7 81 60 23 52" → Output: "+41781602352"  
- Input: "781602352" → Demander: "Quel indicatif pays ?"

# Codes pays courants
- +33: France
- +41: Suisse
- +32: Belgique
- +39: Italie
- +49: Allemagne
- +1: USA/Canada
- +44: Royaume-Uni
""",
    tools=[
        normalize_phone_number,
        search_customers_by_phone,
        search_customer_by_email, 
        validate_email_format,
        create_customer,
        transfer_to_product_consultation
    ]
)

