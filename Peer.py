import sys
import socket
import select
import time
import numpy as np

BUFSIZE = 512
peerName = ""
connectionDict = {}  # Dictionary of connections, name as key, ((ip, port), number) as value
peerNameList = []
forwardingTable = np.matrix(1, 1)
ip = None
port = None


def startPeer(address, port):
    serverSocket = setupServerSocket(address, port)
    while True:
        receiveMessage(serverSocket)


# Used to receive NTU's from the controller and NU's from other peers. New socket is used for every message
def receiveMessage(serverSocket):
    global forwardingTable, port, ip
    serverSocket.listen()
    receivedConnections = False
    clientSocket, clientAddress = serverSocket.accept()
    sockets_list = [clientSocket]
    read, write, exception = select.select(sockets_list, [], [])
    for sock in read:
        if sock == clientSocket:
            message = clientSocket.recv(BUFSIZE).decode()
            if not message:
                print("Connection closed")
                clientSocket.close()
            if "|" in message:  # Message from Controller about connection (of the form ...|name,ip,port,number|...)
                peers = message.split("|")
                for peer in peers:
                    if "-update" in peer:  # -update if peer is last to be informed
                        updateString = getUpdateString()
                        for connection in connectionDict:
                            updateSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            updateSocket.bind(ip, port)
                            updateSocket.connect(connectionDict[connection][0])
                            updateSocket.send(updateString.encode())
                            updateSocket.close()
                        continue
                    if "," in peer:  # Connection update if message is split with ","
                        peer = peer.split(",")
                        connectionDict[peer[0]] = ((peer[1], peer[2]), peer[3])
                        receivedConnections = True
                    else:
                        if len(peerNameList) == 0:  # First element of list is own name
                            peerName = peer
                        elif ip is None:
                            ip = peer
                        elif port is None:
                            port = int(peer)
                        else:
                            peerNameList.append(peer)
                        receivedNames = True
            if receivedConnections:
                forwardingTable = np.matrix(np.ones(len(peerNameList), len(connectionDict)) * sys.maxsize)
                for connection in connectionDict.keys():
                    forwardingTable[peerNameList.index(connection)][connectionDict.keys().index(connection)] = \
                    connectionDict[connection][1]
                receivedConnections = False
            if "~" in message:
                items = message.split("~")
                name = items[0]
                connectionIndex = connectionDict.keys().index(items[0])
                items = items[1:]
                receivedUpdate = False  # Check if forwardingTable is updated
                for item in items:
                    tokens = item.split(",")
                    nameIndex = peerNameList.index(tokens[0])
                    if forwardingTable[nameIndex][connectionIndex] > int(tokens[1]) + connectionDict[name][1]:
                        forwardingTable[nameIndex][connectionIndex] = int(tokens[1]) + connectionDict[name][1]
                        receivedUpdate = True
                if receivedUpdate:  # Send updates only if updates received
                    updateString = getUpdateString()
                    for connection in connectionDict:
                        updateSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        updateSocket.bind(ip, port)
                        updateSocket.connect(connectionDict[connection][0])
                        updateSocket.send(updateString.encode())
                        updateSocket.close()
            if "^" in message:  # Received message
                oldMessage = message
                message = message.split("^")
                print(peerName + " received: " + message[1])
                if message[0] == peerName:
                    print("Message received: " + message[1])
                    return
                nameIndex = peerNameList.index(message[0])
                bestConnection = None
                minValue = sys.maxsize
                for i in range(len(connectionDict)):
                    if forwardingTable[nameIndex][i] < minValue:  #if there is another connection that is as small, then we take the one that was first detected.
                        minValue = forwardingTable[nameIndex][i]
                        bestConnection = connectionDict.keys()[i]
                sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sendSocket.bind(ip, port)
                sendSocket.connect(connectionDict[bestConnection][0])
                sendSocket.send(oldMessage.encode())
                sendSocket.close()
            clientSocket.close()
            return
    time.sleep(0.01)


def setupServerSocket(address, port):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((address, port))
    return serverSocket


def getUpdateString():
    message = peerName + "~"
    minValue = sys.maxsize
    for i in range(len(peerNameList)):
        for j in range(len(connectionDict)):
            if minValue > forwardingTable[i][j]:
                minValue = forwardingTable[i][j]
        message = message + peerNameList[i] + "," + minValue + "~"
    return message[:-1]


def main():
    if len(sys.argv) == 3:
        address = sys.argv[1]
        port = int(sys.argv[2])
        startPeer(address, port)
    else:
        print("Error, wrong arguments")


if __name__ == '__main__':
    main()
