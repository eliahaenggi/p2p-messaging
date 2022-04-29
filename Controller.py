import sys
import socket

nameDict = {}
connectionDict = {}


def startController():
    while True:
        getMessages()


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
        message = ""
        for peerPairs in connectionDict.keys():
            if peerPairs[0] == peer:
                message = message + peerPairs[1] + "," + nameDict[peerPairs[1]][0] + "," + str(nameDict[peerPairs[1]][1])
                message = message + "," + str(connectionDict[peerPairs]) + "|"
            if peerPairs[1] == peer:
                message = message + peerPairs[0] + "," + nameDict[peerPairs[0]][0] + "," + str(nameDict[peerPairs[0]][1])
                message = message + "," + str(connectionDict[peerPairs]) + "|"
        iteration += 1
        if iteration >= len(nameDict):
            message = message + "-update"
        peerSocket = socketDict[peer]
        print("[Controller:] " + message + "\n")
        peerSocket.send(message.encode())
        peerSocket.close()


# Sends list of all peer names. First name is the name of the own peer
def sendNames(nameDict):
    socketDict = connectToPeers(nameDict)
    for peer in nameDict.keys():
        message = ""
        for peers in nameDict.keys():
            if peer != peers:
                message = message + "|" + peers
        message = "-n|" + peer + message
        peerSocket = socketDict[peer]
        print("[Controller:] " + message + "\n")
        peerSocket.send(message.encode())
        peerSocket.close()


def getMessages():
    global nameDict, connectionDict
    if "-f" in input("Write -f to specify a filepath, then write -m to specify a message:\n"):
        filepath = input("Enter the filepath:\n")
        nameDict, connectionDict = readFile(filepath)
        sendNames(nameDict)
        sendNTU(nameDict,connectionDict)
    if "-m" in input("Write -f to specify a filepath, then write -m to specify a message:\n"):
        sender = input("which peer should send a message?\n")
        receiver = input("who should be the receiver?\n")
        message = input("what should the message be?\n")
        sendMessage(nameDict, sender, receiver, message)


def sendMessage(nameDict, sender, receiver, message):
    if sender not in nameDict.keys():
        print("Unknown sender")
        return
    elif receiver not in nameDict.keys():
        print("Unknown receiver")
        return
    else:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect(nameDict[sender])
        sendMessage = receiver + "^" + message
        print("[Controller:] " + sendMessage + "\n")
        clientSocket.send(sendMessage.encode())
        clientSocket.close()


# Connect with sockets to all peers, return Dict with all sockets
def connectToPeers(nameDict):
    socketDict = {}  # node names as key, socket as value
    portOffset = 0  # Offset to have different ports, counted up every loop
    for peer in nameDict.keys():
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect(nameDict[peer])
        socketDict[peer] = clientSocket
        portOffset += 1
    return socketDict


def main():
    if len(sys.argv) == 1:
        startController()
    else:
        print("Error, wrong arguments")


if __name__ == '__main__':
    main()
