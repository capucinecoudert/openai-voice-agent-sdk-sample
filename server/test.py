# Tester l'import direct
from app.information_desk_agent import information_desk_agent
from app.customer_authentification_agent import customer_authentification_agent

print('Info agent name:', information_desk_agent.name)
print('Auth agent name:', customer_authentification_agent.name)

# Vérifier les handoffs
print('Info agent handoffs:', [agent.name for agent in information_desk_agent.handoffs])

# Tester la fonction de transfert
from app.information_desk_agent import transfer_to_customer_authentification_agent
result = transfer_to_customer_authentification_agent()
print('Transfer function result:', result)
