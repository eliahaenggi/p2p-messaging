import sys
import socket
import select
import time
import numpy as np

BUFSIZE = 512
peerName = ""
connectionDict = {}  # Dictionary of connections, name as key, ((ip, port), number) as value
peerNameList = []
global forwardingTable


def startPeer(address, port):
    serverSocket = setupServerSocket(address, port)
    while True:
        receiveMessage(serverSocket)


# Used to receive NTU's from the controller and NU's from other peers. New socket is used for every message
def receiveMessage(serverSocket):
    global forwardingTable
    serverSocket.listen()
    receivedNames = False  # If True initialize forwardingTable
    receivedConnections = False  # If True write connections on diagonal of forwardingTable
    clientSocket, clientAddress = serverSocket.accept()
    sockets_list = [clientSocket]
    while True:
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
                            for connection in connectionDict.keys():
                                message = ""
                                # TODO send NU to other peers
                            continue
                        if "," in peer:  # Connection update if message is split with ","
                            peer = peer.split(",")
                            connectionDict[peer[0]] = ((peer[1], peer[2]), peer[3])  # Update connection
                            receivedConnections = True
                        else:
                            if len(peerNameList) == 0:  # First element of list is own name
                                peerName = peer
                            peerNameList.append(peer)  # Name list if no "," in message
                            receivedNames = True
                if receivedNames:  # Initialize forwarding table if names received
                    receivedNames = False
                    numPeers = len(peerNameList)
                    forwardingTable = np.matrix(np.ones((numPeers, numPeers)) * np.inf)
                if receivedConnections:  # Setup numbers for connected peers (should be called after receivedNames)
                    receivedConnections = False
                    iterations = 0
                    for peer in peerNameList:
                        if peer in connectionDict.keys():
                            forwardingTable[iterations][iterations] = connectionDict[peer][1]
                        iterations += 1
                # TODO If received NU from other peer update forwarding-table and send NU to connections
                clientSocket.close()
                return
        time.sleep(0.01)


def setupServerSocket(address, port):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((address, port))
    return serverSocket


def main():
    if len(sys.argv) == 3:
        address = sys.argv[1]
        port = int(sys.argv[2])
        startPeer(address, port)
    else:
        print("Error, wrong arguments")


if __name__ == '__main__':
    main()
