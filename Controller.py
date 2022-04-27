import sys
import socket


def startController(filepath):
    nameDict, connectionDict = readFile(filepath)
    sendNames(nameDict)
    sendNTU(nameDict, connectionDict)
    while True:
        getMessage(nameDict)


# Should read the input file and save nodes in nameDict and connections in connectionDict
def readFile(filepath):
    nameDict = {}  # node names as key, (ip, port) as value
    connectionDict = {}  # (name, name) as key, cost as value
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


# Send NTU to every peer. At the end all sockets are closed again
def sendNTU(nameDict, connectionDict):
    socketDict = connectToPeers(nameDict)
    iteration = 0  # Save number of iterations to get last peer to send update information
    for peer in nameDict.keys():
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
            message = message[:-1]  # Cut off last "|" of messages if peer is not last peer
        peerSocket = socketDict[peer]
        peerSocket.send(message.encode())
        peerSocket.close()


# Sends list of all peer names. First name is the name of the own peer
def sendNames(nameDict):
    socketDict = connectToPeers(nameDict)
    message = ""
    for peer in nameDict.keys():
        for peers in nameDict.keys():
            if peer != peers:
                message = message + "|" + peers
        message = peer + "|" + nameDict[peer][0] + "|" + nameDict[peer][1] + message
        peerSocket = socketDict[peer]
        peerSocket.send(message.encode())
        peerSocket.close()



# Connect with sockets to all peers, return Dict with all sockets
def connectToPeers(nameDict):
    socketDict = {}  # node names as key, socket as value
    portOffset = 0  # Offset to have different ports, counted up every loop
    for peer in nameDict.keys():
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.bind(("", 8080 + portOffset))  # Bind socket
        clientSocket.connect(nameDict[peer])
        socketDict[peer] = clientSocket
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
