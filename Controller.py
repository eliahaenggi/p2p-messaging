import sys
import socket


def startController(filepath):
    nameDict, connectionDict = readFile(filepath)
    socketDict = connectionDict(nameDict)


def readFile(filepath):
    nameDict = {}  # node names as key, (ip, port) as value
    connectionDict = {}  # (name, name) as key, number as value
    f = open(filepath, "r")
    lines = (f.readlines())
    nodeline = lines[0]
    nodelist = nodeline.split("|")
    for node in nodelist:
        node = node.split(",")
        nameDict[node[0]] = (node[1], int(node[2]))
    for connection in lines[1:]:
        connection = connection.split(",")
        connectionDict[(connection[0], connection[1])] = int(connection[2])
    return nameDict, connectionDict


def connectNodes(nameDict):
    socketDict = {}  # node names as key, socket as value
    portOffset = 0  # Offset to have different ports, counted up every loop
    for node in nameDict.keys():
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.bind(("", 8080 + portOffset))  # Bind socket
        clientSocket.connect(nameDict[node])
        socketDict[node] = clientSocket
        portOffset += 1
    return socketDict


def main():
    if len(sys.argv) == 2:
        filepath = sys.argv[1]
        startController(filepath)
    else:
        print("Error, wrong arguments")


if __name__ == '__main__':
    main()
