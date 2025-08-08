# Tester l'import direct
from app.welcome_agent import welcome_agent
print('Agent name:', welcome_agent.name)
print('Agent type:', type(welcome_agent))

# Tester l'import depuis agent_config
from app.agent_config import starting_agent
print('Starting agent name:', starting_agent.name)
print('Starting agent type:', type(starting_agent))


# Tester l'import depuis agent_config
from app.agent_config import customer_authentification_agent
print('Customer authentication agent name:', customer_authentification_agent.name)
print('Customer authentication agent type:', type(customer_authentification_agent))
