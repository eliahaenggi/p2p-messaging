import sys
import socket
import select
import time

BUFSIZE = 512
peerName = None
connectionDict = {}  # Dictionary of connections, name as key, ((ip, port), cost) as value
peerNameList = []  # List of all peers (excluding the own)
forwardingTable = {}  # forwardingTable as dictionary, target peer name as key, ((ip, port), cost) as value
ip = None  # Specified as argument
port = None  # Specified as argument
firstUpdate = True

def startPeer():
    serverSocket = setupServerSocket()
    while True:
        receiveMessage(serverSocket)


# Used to receive NTU's from the controller and NU's from other peers. New socket is used for every message.
def receiveMessage(serverSocket):
    global forwardingTable, port, ip, peerName, firstUpdate
    serverSocket.listen()
    clientSocket, clientAddress = serverSocket.accept()
    sockets_list = [clientSocket]
    read, write, exception = select.select(sockets_list, [], [])
    for sock in read:
        if sock == clientSocket:
            message = clientSocket.recv(BUFSIZE).decode()
            if not message:
                print("Connection closed")
                clientSocket.close()

            # Message from Controller about Peer names or NTU
            if "|" in message:
                peers = message.split("|")
                print(message)
                for peer in peers:
                    if "" == peer:
                        continue
                    if "-n" in peer:
                        peerName = None
                        peerNameList.clear()
                        connectionDict.clear()
                        forwardingTable.clear()
                        firstUpdate = True
                        continue
                    if "-update" in peer:  # Send update string to all connections
                        updateString = getUpdateString()
                        for connection in connectionDict.keys():
                            updateSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            updateSocket.connect((connectionDict[connection][0][0], int(connectionDict[connection][0][1])))
                            updateSocket.send(updateString.encode())
                            print("-updatestring: " + updateString)
                            updateSocket.close()
                        continue
                    if "," in peer:  # NTU, set connectionDict, set forwardingTable to mac int
                        peer = peer.split(",")
                        connectionDict[peer[0]] = ((peer[1], peer[2]), int(peer[3]))
                        forwardingTable[peer[0]] = ((peer[1], peer[2]), sys.maxsize)
                    else:
                        if peerName is None:  # List of peer names from the controller, first name is own peer name
                            peerName = peer
                        else:
                            peerNameList.append(peer)
                            forwardingTable[peer] = ("", sys.maxsize)

            # NU from other peers (Own_Name~Other_Name,Cost~Other_Name,Cost~...)
            if "~" in message:
                items = message.split("~")
                name = items[0]  # peer name of the NU sender
                items = items[1:]
                if name not in connectionDict.keys():
                    print("Error, peer received update from unknown peer")
                    continue
                receivedUpdate = False  # Check if forwardingTable is updated
                for item in items:
                    tokens = item.split(",")
                    if tokens[0] not in forwardingTable.keys():  # Should filter own peer from forwarding table
                        continue
                    # Check if there is a better connection to peer
                    if forwardingTable[tokens[0]][1] > int(tokens[1]) + connectionDict[name][1]:
                        if tokens[0] in connectionDict.keys() and connectionDict[tokens[0]][1] < int(tokens[1]) + connectionDict[name][1]:
                            forwardingTable[tokens[0]] = (connectionDict[tokens[0]][0], connectionDict[tokens[0]][1])
                        else:
                            forwardingTable[tokens[0]] = (connectionDict[name][0], int(tokens[1]) + connectionDict[name][1])
                        receivedUpdate = True
                if receivedUpdate or firstUpdate:  # Send own connections to other peers only if forwardingTable updated
                    updateString = getUpdateString()
                    firstUpdate = False
                    for connection in connectionDict:
                        updateSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        updateSocket.connect((connectionDict[connection][0][0], int(connectionDict[connection][0][1])))
                        updateSocket.send(updateString.encode())
                        print("Send Update: " + updateString)
                        updateSocket.close()

            # Received Message from peer or controller (Receiver_of_the_Message^Message)
            if "^" in message:
                oldMessage = message
                message = message.split("^")
                # Check if message already is at target peer
                if message[0] == peerName:
                    print("Message reached target: " + message[1])
                    return
                sendSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Send message to address in forwardingTable
                address = (forwardingTable[message[0]][0][0], forwardingTable[message[0]][0][1])
                sendSocket.connect((address[0], int(address[1])))
                print(peerName + " is forwarding the message to " + str(address))
                sendSocket.send(oldMessage.encode())
                sendSocket.close()
            clientSocket.close()
            return
    time.sleep(0.01)


def setupServerSocket():
    global ip, port
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((ip, port))
    return serverSocket


# Create String to send as NU (Own_Peer_Name~Other_Peer_Name,Cost~Other_Peer_Name,Cost~...)
def getUpdateString():
    message = peerName + "~"
    for peer in forwardingTable.keys():
        value = forwardingTable[peer][1]
        if peer in connectionDict.keys():
            # Take the connection cost if its smaller than the value in the forwardingTable
            if int(connectionDict[peer][1]) < int(forwardingTable[peer][1]):
                value = connectionDict[peer][1]
        message = message + peer + "," + str(value) + "~"
    return message[:-1]


def main():
    global ip, port
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        startPeer()
    else:
        print("Error, wrong arguments")


if __name__ == '__main__':
    main()
