import json
import flow

def extractFromJson(inpt, isFile=False):
	jsonObj = inpt
	if(isFile):
		with open(inpt) as json_input:
			jsonObj = json.load(json_input)

	edges = []
	vertexNames = ["Epicenter"]
	flowDemanded = 0

	for hospital, bedsAvailable in jsonObj["hospitals"]:
		vertex = len(vertexNames)
		vertexNames.append(hospital)
		edges.append([vertex, -2, bedsAvailable])
	for region, injured in jsonObj["regions"]:
		vertex = len(vertexNames)
		vertexNames.append(region)
		edges.append([0, vertex, injured])
		flowDemanded += injured
	for ambulance, region, hospital, capacity in jsonObj["ambulances"]:
		vertex = len(vertexNames)
		vertexNames.append(ambulance)
		srcInd = vertexNames.index(region) if region in vertexNames else -1
		dstInd = vertexNames.index(hospital) if hospital in vertexNames else -1
		edges.append([srcInd, vertex, capacity])
		edges.append([vertex, dstInd, capacity])

	sinkVertex = len(vertexNames)
	vertexNames.append("Safety")
	for i, e in enumerate(edges):
		if(e[1] == -2):
			edges[i][1] = sinkVertex

	return (len(vertexNames), flowDemanded, edges, vertexNames)


def computeFromJson(inpt, isFile=False, printData=True):
	vNum, fDemanded, edges, names = __extractFromJson(inpt, isFile = isFile)
	flowSupplied, pathing = flow.fordFulkerson(vNum, edges, 0, vNum-1)
	if(printData):
		if(fDemanded == flowSupplied):
			print("Ambulatory Network can sustain all injured.")
			print("Quickly use the following routes")
		else:
			print("Ambulatory Network *cannot* sustain all injured.")
			print("To minimize loss of life, triage and use the following routes: ")

		for (injured, path) in pathing:
			print("Send %05d Injured Along: " % injured, end="")
			for i, route in enumerate(path[1:-1]):
				print("%s" % (names[route]), end="")
				if(i < len(path)-3):
					print(" -> ", end="")
			print()

	pathList = []
	for (injured, path) in pathing:
		pathList.append({
			"capacity": injured,
			"path": [names[route] for route in path[1:-1]]
		})

	return {
		"flow": {
			"demanded": fDemanded,
			"supplied": flowSupplied
		},
		"path": pathList
	}

#print(computeFromJson("survival.json", isFile=True))
