import pickle
import json

with open('agent2-2.pkl', 'rb') as f:
    states_value = pickle.load(f)


with open('agent2-1.json', 'w') as f:
    json.dump(states_value, f)