import os
from flow import fordFulkerson

REGIONAL_START = "[Regions]"
HOSPTIAL_START = "[Hospitals]"
AMBULANCE_START = "[Ambulatory Service]"

def extractFile(filename):
	edges = []
	vertexNames = ["Epicenter", ]
	flowDemanded = 0
	with open(filename, "r") as fp:
		section = -1
		for line in fp:
			line = line.strip()
			print(line)
			if(not line):
				continue

			if(line == REGIONAL_START):
				section = 0
			elif(line == HOSPTIAL_START):
				section = 1
			elif(line == AMBULANCE_START):
				section = 2
			elif(section == 0):
				regionName, regionCasualties = line.split(",")
				regionCasualties = int(regionCasualties)
				vertex = len(vertexNames)
				vertexNames.append(regionName)
				flowDemanded += regionCasualties
				edges.append([0, vertex, regionCasualties])
			elif(section == 1):
				regionName, bedsAvailable = line.split(",")
				bedsAvailable = int(bedsAvailable)
				vertex = len(vertexNames)
				vertexNames.append(regionName)
				edges.append([vertex, -2, bedsAvailable])
			elif(section == 2):
				ambName, fromRegion, toHospital, cap = line.split(",")
				cap = int(cap)
				vertex = len(vertexNames)
				vertexNames.append(ambName)
				srcInd = -1
				if(fromRegion.strip() in vertexNames):
					srcInd = vertexNames.index(fromRegion.strip())
				dstInd = -1
				if(toHospital.strip() in vertexNames):
					dstInd = vertexNames.index(toHospital.strip())
				edges.append([srcInd, vertex, cap])
				edges.append([vertex, dstInd, cap])

	vertexNames.append("Safety")
	sinkVertex = len(vertexNames)-1
	for i, e in enumerate(edges):
		if(e[1] == -2):
			edges[i][1] = sinkVertex

	return (len(vertexNames), flowDemanded, edges, vertexNames)


vNum, fDemanded, edges, names = extractFile("survival.csv")
print(fordFulkerson(vNum, edges, 0, vNum-1))
