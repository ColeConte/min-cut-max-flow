# def computeFlow(g, s, t):

# Each edge has a dest and a weight
class Node():
	def __init__(self, ind):
		self.edges = []
		self.index = ind
	def getAvailableEdges(self):
		return [e for e in self.edges if e[1] > 0]
	def addEdge(self, edge):
		self.edges.append(edge)
	def __str__(self):
		return "Node %03d: %s" % (self.index, self.edges)


def createGraph(vertexCount, edges, reverse=False):
	nodes = [Node(n) for n in range(vertexCount)]
	for source, dest, weight in edges:
		if(reverse):
			nodes[dest].addEdge([source, 0])
		else:
			nodes[source].addEdge([dest, weight])
	return nodes

def targetedBFS(nodes, start, end, build=[], weights=[]):
	if(start == end):
		return (build + [start], min(weights))
	else:
		for [dest, weight] in nodes[start].getAvailableEdges():
			return targetedBFS(nodes, dest, end, build + [start], weights + [weight])

# def fulker


edges = [(4, 3, 10), (1, 2, 6), (2, 4, 10)]
nodes = createGraph(5, edges)
[print(x) for x in nodes]

print(targetedBFS(nodes, 1, 4))
