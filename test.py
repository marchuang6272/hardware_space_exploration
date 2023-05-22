from pyvis.network import Network
import json
import webbrowser

# Create an empty graph
graph = Network(directed=True, width="100%", height="100%", bgcolor="#2a3950")
# Set options for background color, node color, and edge color
options = {
    "nodes": {"color": {"background": "#016171"}, "borderWidth": 0},
    "edges": {"color": "#00e0c6"},
}

# Convert options dictionary to JSON string
options_str = json.dumps(options)

# Set the options using the JSON string
graph.set_options(options_str)

# Add nodes with rounded rectangle shape
graph.add_node(
    1, label="Node 1\nYour boy", shape="box", shapeProperties={"borderRadius": 10}
)
graph.add_node(
    "dance", label="Node 2", shape="box", shapeProperties={"borderRadius": 10}
)
graph.add_node(3, label="Node 3", shape="box", shapeProperties={"borderRadius": 10})
graph.add_node(4, label="Node 4", shape="box", shapeProperties={"borderRadius": 10})

# Add edges with longer length
graph.add_edge(1, "dance", length=200)
graph.add_edge("dance", 3, length=200)
graph.add_edge(3, 4, length=200)
graph.add_edge(4, 1, length=200)
# Generate the HTML
# html = graph.write_html("graph.html")
# webbrowser.open("file:///home/marcanthony/Research/python_automation/graph.html")

graph.show("graph.html")
