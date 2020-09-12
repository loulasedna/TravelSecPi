import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
def plot_graph(nodes, edges, labels=False, node_size=False,
               node_color='r', arrows=False, alpha=0.1):
    """nodes: list of nodes. Used as labels if labels=True
       edges: list of edges. Edges are tuples.
       node_size: size or list of sizes
       node_color: color or list of colors
    """
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    nx.draw(G, with_labels=labels, node_color=node_color,
            node_size=node_size, arrows=arrows, alpha=alpha)

# g=nx.Graph()

# for i in range(1,21):
#     g.add_node("a{}".format(str(i)))
#     g.add_edge("a{}".format(str(i)),"a{}".format(str(i-1)))
#     for j in range(1,21):
#         g.add_node("b{}{}".format(str(i),str(j)))
#         g.add_edge("a{}".format(str(i)),"b{}{}".format(str(i),str(j)))

#         for k in range(1,11):
#             g.add_node("c{}{}{}".format(str(i),str(j),str(k)))
#             g.add_edge("b{}{}".format(str(i),str(j)),"c{}{}{}".format(str(i),str(j),str(k)))



# nx.draw(g,with_labels=True)
# plt.savefig(fname="simple_path.pdf",format='pdf') # save as png


# Node data
Stations = pd.DataFrame([['Station1', 2500],['Station2',1210],
                         ['Station3', 90],['Station4', 312],
                         ['Station5', 11],['Station6', 190]],
                        columns=['Station', 'Traffic'])
# Edge data
routes = pd.DataFrame([['Station1', 'Station2'],
                       ['Station1', 'Station4'],
                       ['Station1', 'Station5'],
                       ['Station2', 'Station3'],
                       ['Station2', 'Station5'],
                       ['Station2', 'Station6'],
                       ['Station3', 'Station5'],
                       ['Station4', 'Station1'],
                       ['Station4', 'Station2'],
                       ['Station4', 'Station6'],
                       ['Station5', 'Station6']],
                      columns=['start', 'stop'])
plot_graph(nodes=Stations['Station'],
           edges=[tuple(row) for row in routes.values],
           labels=True,
           node_color='orange',
           node_size=Stations['Traffic'],
           alpha=0.8)