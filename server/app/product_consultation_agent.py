"""
Agent de consultation produits ResaSki
Conseille et présente les activités disponibles
"""

import json
import os
from agents import Agent, function_tool

@function_tool
def get_available_products(customer_id: str):
    """Récupère les produits disponibles pour le client"""
    return json.dumps({
        "success": True,
        "products": [
            {"id": 1, "name": "Cours de ski débutant", "price": 45},
            {"id": 2, "name": "Cours de snowboard", "price": 50},
            {"id": 3, "name": "Location matériel", "price": 25}
        ]
    })

product_consultation_agent = Agent(
    name="Agent de Consultation Produits ResaSki",
    model="gpt-4o-mini",
    instructions="""
# Mission
Tu aides les clients authentifiés à choisir leurs activités et services.

# Prise de relais
Quand tu prends le relais, commence par :
"Parfait ! Maintenant que vous êtes identifié, voyons ensemble quelles activités vous intéressent."

# Ton rôle
- Présenter les activités disponibles
- Conseiller selon les besoins
- Préparer la réservation
""",
    tools=[get_available_products]
)

__all__ = ["product_consultation_agent"]