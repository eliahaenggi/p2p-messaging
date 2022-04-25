import sys
import socket


def startController(filepath):
    nameDict, connectionDict = readFile(filepath)
    sendNTU(nameDict, connectionDict)


# Should read the input file and save nodes in nameDict and connections in connectionDict
def readFile(filepath):
    nameDict = {}  # node names as key, (ip, port) as value
    connectionDict = {}  # (name, name) as key, number as value
    f = open(filepath, "r")
    lines = (f.readlines())
    peers = lines[0]
    peerlist = peers.split("|")
    for peer in peerlist:
        peer = peer.split(",")
        nameDict[peer[0]] = (peer[1], int(peer[2]))
    for connection in lines[1:]:
        connection = connection.split(",")
        connectionDict[(connection[0], connection[1])] = int(connection[2])
    return nameDict, connectionDict


# Should first initialize sockets for every peer and afterwards send NTU to every peer. At the end all sockets are
# closed again
def sendNTU(nameDict, connectionDict):
    socketDict = {}  # node names as key, socket as value
    portOffset = 0  # Offset to have different ports, counted up every loop
    for peer in nameDict.keys():
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.bind(("", 8080 + portOffset))  # Bind socket
        clientSocket.connect(nameDict[peer])
        socketDict[peer] = clientSocket
        portOffset += 1
    iteration = 0  # Save number of iterations to get last peer to send update information
    for peer in nameDict.keys():
        message = peer + "|"
        for peerPairs in connectionDict.keys():
            if peerPairs[0] == peer:
                message = message + peerPairs[1] + "," + nameDict[peerPairs[1]][0] + "," + nameDict[peerPairs[1]][1]
                message = message + "," + connectionDict[peerPairs] + "|"
            if peerPairs[1] == peer:
                message = message + peerPairs[0] + "," + nameDict[peerPairs[0]][0] + "," + nameDict[peerPairs[0]][1]
                message = message + "," + connectionDict[peerPairs] + "|"
        iteration += 1
        if iteration >= len(nameDict):
            message = message + "-update"
        else:
            message = message[:-1]  # Cut off last "|" of all not last peers
        peerSocket = socketDict[peer]
        peerSocket.send(message.encode())
        peerSocket.close()


def main():
    if len(sys.argv) == 2:
        filepath = sys.argv[1]
        startController(filepath)
    else:
        print("Error, wrong arguments")


if __name__ == '__main__':
    main()
