from wicked21st.graph import load_graph
from wicked21st.project import Projects

graph_def = load_graph("map20210812.mm")

projects_def = Projects(graph_def)

print("\n".join(projects_def.names))
