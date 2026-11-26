from backend.agents.routing_agent import routing_agent


test_state = {
    "complaint_id": 1,
    "category": "Road Damage",
    "severity": "High",
    "decision": "approved"
}

result = routing_agent(test_state)

print("\nGAARD Routing Result")
print("--------------------")

for key, value in result.items():
    print(f"{key}: {value}")