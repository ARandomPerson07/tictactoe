from tictactoe_graph import get_boards
import dash
import dash_cytoscape as cyto
from dash.dependencies import Input, Output
import networkx as nx
import ast

G = get_boards()
def get_subgraph(G, node):
    descendants = nx.descendants(G, node)
    descendants.add(node)
    subgraph = G.subgraph(descendants).copy()
    return subgraph

pos = nx.multipartite_layout(G, subset_key='level', scale = 5, align="horizontal")

x_spacing = 1
y_spacing = 4

for node, (x, y) in pos.items():
    pos[node] = (x * x_spacing, y * y_spacing)

def nodeToLabel(node):
    return f"{node[:3]}\n{node[3:6]}\n{node[6:9]}"

level_colors = {
    0: "#1f77b4",  # Muted blue
    1: "#ff7f0e",  # Safety orange
    2: "#2ca02c",  # Cooked asparagus green
    3: "#d62728",  # Brick red
    4: "#9467bd",  # Muted purple
    5: "#8c564b",  # Chestnut brown
    6: "#e377c2",  # Raspberry yogurt pink
    7: "#7f7f7f",  # Middle gray
    8: "#bcbd22",  # Curry yellow-green
    9: "#17becf"   # Blue-teal
}


def nx_to_cyto_elements(G, pos=None):
    """
    Converts a NetworkX graph into Cytoscape elements.
    If pos is provided, it is assumed to be a dict mapping nodes to (x, y) positions.
    """
    elements = []
    # Create node elements
    for node in G.nodes():
        node_element = {
            'data': {'id': str(node), 'label': nodeToLabel(node), 
                     'node_color' : level_colors[G.nodes[node].get('level', None)]}
        }
        if pos and node in pos:
            # NetworkX layout functions typically return coordinates in a small range (like 0 to 1)
            # Multiply to scale them up to pixel coordinates.
            x, y = pos[node]
            node_element['position'] = {'x': x * 3000, 'y': y * 2000}
        elements.append(node_element)
    
    # Create edge elements
    for source, target in G.edges():
        source_level = G.nodes[source].get('level', None)
        # Get the color from our mapping; use a default color if the level isn't defined.
        color = level_colors.get(source_level, '#CCCCCC')
        #print(f"got color {color} for edge")
        elements.append({
            'data': {'source': str(source), 'target': str(target), 'line_color': color}
        })
    
    return elements

# Convert the full graph G into Cytoscape elements with the custom positions.
full_elements = nx_to_cyto_elements(G, pos)


app = dash.Dash(__name__)

default_stylesheet = [
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',      # Use the node's label
                    'text-valign': 'center',       # Vertical alignment: center inside the node
                    'text-halign': 'center',       # Horizontal alignment: center inside the node
                    'background-color': 'data(node_color)', # Example background color
                    'color': '#333333',            # Font color
                    'font-size': '16px',           # Font size (adjust as needed)
                    'width': '100px',    # Adjust size as needed
                    'height': '100px',   # Adjust size as needed
                    'text-wrap' : 'wrap',
                    # You can also adjust padding or node dimensions if needed
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'line-color': 'data(line_color)'
                }
            }
        ]

app.layout = dash.html.Div([
    dash.html.Button("Back", id="back-button", n_clicks=0),
    cyto.Cytoscape(
        id='cytoscape',
        elements=full_elements,
        style={'width': '100%', 'height': '600px'},
        stylesheet=default_stylesheet,
        layout={'name': 'preset'}  # or any layout you prefer
    )
])

xdic = {
    0 : 1,
    1 : 0.85,
    2 : 0.5,
    3 : 0.65,
    4 : 0.4,
    5 : 0.2,
    6 : 0.2,
    7 : 0.2,
    8 : 0.2
}

ydic = {
    0 : 4,
    1 : 2.5,
    2 : 2.2,
    3 : 1.6,
    4 : 0.6,
    5 : 0.3,
    6 : 0.15,
    7 : 0.15,
    8 : 0.05
}

sizdic = {
    0 : (16, 100),
    1 : (28, 150),
    2 : (28, 150),
    3 : (36, 200),
    4 : (44, 275),
    5 : (44, 275),
    6 : (44, 275),
    7 : (44, 275),
    8 : (44, 275),
    
}

def build_stylesheet(level):
    # Base style for all nodes and edges
    stylesheet = [
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',      # Use the node's label
                    'text-valign': 'center',       # Vertical alignment: center inside the node
                    'text-halign': 'center',       # Horizontal alignment: center inside the node
                    'background-color': 'data(node_color)', # Example background color
                    'color': '#333333',            # Font color
                    'font-size': f'{sizdic[level][0]}px',           # Font size (adjust as needed)
                    'width': f'{sizdic[level][1]}px',    # Adjust size as needed
                    'height': f'{sizdic[level][1]}px',   # Adjust size as needed
                    'text-wrap' : 'wrap',
                    # You can also adjust padding or node dimensions if needed
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'target-arrow-shape': 'triangle',
                    'line-color': 'data(line_color)'
                }
            }
        ]
    return stylesheet


@app.callback(
    Output('cytoscape', 'elements'),
    Output('cytoscape', 'stylesheet'),
    Input('cytoscape', 'tapNodeData'),
    Input('back-button', 'n_clicks')
)
def update_graph(nodeData, n_clicks):
    ctx = dash.callback_context

    # If nothing has triggered the callback yet, return the full graph
    if not ctx.triggered:
        return full_elements, default_stylesheet

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # If the back button was clicked, display the full graph.
    if triggered_id == 'back-button':
        return full_elements, default_stylesheet

    # If a node was clicked, update the graph to show the subgraph.
    if nodeData:
        clicked_node = nodeData['id']
        # Note: Convert the string id back to its original type if necessary.
        nodeId = ast.literal_eval(clicked_node)
        sub_G = get_subgraph(G, nodeId)

        # Recompute positions for the subgraph.
        sub_pos = nx.multipartite_layout(sub_G, subset_key='level', scale=5, align="horizontal")
        level = G.nodes[nodeId]['level']
        print("level", level)
        x_spacing = xdic[level]
        y_spacing = ydic[level]
        print(x_spacing, y_spacing)
        for node, (x, y) in sub_pos.items():
            sub_pos[node] = (x * x_spacing, y * y_spacing)

        # compute the stylesheet
        new_stylesheet = build_stylesheet(level)

        return nx_to_cyto_elements(sub_G, pos=sub_pos), new_stylesheet

    # Fallback: return the full graph.
    return full_elements


if __name__ == '__main__':
    app.run_server(debug=True)