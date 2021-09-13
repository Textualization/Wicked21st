from wicked21st.graph import load_graph
from wicked21st.policy import Policies

graph_def = load_graph("map20210812.mm")

policies_def = Policies(graph_def)

print("\n".join(policies_def.names))
