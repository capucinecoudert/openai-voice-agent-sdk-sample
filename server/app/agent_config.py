"""
Configuration principale des agents ResaSki
Import et configuration du système phoneAI
"""

import os
from agents import Agent
from .welcome_agent import welcome_agent
from .customer_authentification_agent import customer_authentification_agent

# Configuration des handoffs entre agents
welcome_agent.handoffs = [customer_authentification_agent]

# Agent de démarrage du système phoneAI
starting_agent = welcome_agent

# Export de l'agent de démarrage pour le serveur
__all__ = ["starting_agent"]