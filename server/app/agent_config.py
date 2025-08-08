import os
from agents import Agent
from .welcome_agent import welcome_agent
from .customer_authentification_agent import customer_authentification_agent
from .information_desk_agent import information_desk_agent
from .product_consultation_agent import product_consultation_agent

# ✅ DEBUG: Afficher les noms des agents
print(f"🔍 DEBUG - Agent names:")
print(f"   - Welcome: '{welcome_agent.name}'")
print(f"   - Auth: '{customer_authentification_agent.name}'")
print(f"   - Info: '{information_desk_agent.name}'")
print(f"   - Product: '{product_consultation_agent.name}'")

# Configuration des handoffs entre agents
welcome_agent.handoffs = [customer_authentification_agent, information_desk_agent]
information_desk_agent.handoffs = [customer_authentification_agent]  # ✅ AJOUT
customer_authentification_agent.handoffs = [product_consultation_agent]

print(f"✅ Handoffs configured:")
print(f"   - Welcome → {[agent.name for agent in welcome_agent.handoffs]}")
print(f"   - Info → {[agent.name for agent in information_desk_agent.handoffs]}")
print(f"   - Auth → {[agent.name for agent in customer_authentification_agent.handoffs]}")

# Agent de démarrage du système phoneAI
starting_agent = welcome_agent

# Export de l'agent de démarrage pour le serveur
__all__ = ["starting_agent"]