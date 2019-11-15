# def computeFlow(g, s, t):

# Each edge has a dest and a weight
class Node():
	def __init__(self, ind):
		self.edges = []
		self.index = ind
	def getAvailableEdges(self, ignore=[]):
		return [e for e in self.edges if e[1] > 0 and not(e[0] in ignore)]
	def addEdge(self, edge):
		if(edge[0] >= 0 and edge[1] >= 0 and edge[2] >= 0)
		self.edges.append(edge)
	def setEdge(self, edge):
		for i,e in enumerate(self.edges):
			if(edge[0] == e[0]):
				self.edges[i] = edge
				break
	def getEdgeWeight(self, dst):
		for i,w in self.edges:
			if(i == dst):
				return w
		return -1
	def setEdgeWeight(self, dst, weight, diff=False):
		modifiedWeight = weight
		if(diff):
			currentWeight = self.getEdgeWeight(dst)
			modifiedWeight = max(0, currentWeight-weight)
		self.setEdge([dst, modifiedWeight])

	def __str__(self):
		return "Node %03d: %s" % (self.index, self.edges)

def createGraph(vertexCount, edges, reverse=False):
	nodes = [Node(n) for n in range(vertexCount)]
	for source, dest, weight in edges:
		nodes[source].addEdge([dest, weight])
		if(reverse):
			nodes[dest].addEdge([source, 0])
	return nodes

def targetedBFS(nodes, start, end, build=[], weights=[]):
	build = build + [start]
	if(start == end):
		return (build, min(weights))
	else:
		availableEdges = nodes[start].getAvailableEdges(ignore=build)
		for (dest, weight) in availableEdges:
			return targetedBFS(nodes, dest, end, build, weights + [weight])

def fordFulkerson(vertexNum, edges, source, sink):
	residual = createGraph(vertexNum, edges, reverse=True)

	flow = 0

	targetResults = targetedBFS(residual, source, sink)
	while(targetResults):
		print("HI")
		path, minWeight = targetResults
		flow += minWeight
		for src, dst in zip(path[:-1], path[1:]):
			residual[src].setEdgeWeight(dst, minWeight, diff=True)
			residual[dst].setEdgeWeight(src, -minWeight, diff=True)
			targetResults = targetedBFS(residual, source, sink)



	[print(x) for x in residual]
	return flow
