import sys
import socket
import select
import time

BUFSIZE = 512
peerName = ""
connectionDict = {}  # Dictionary of connections, name as key, ((ip, port), number) as value
socketDict = {}  # name as key, socket as value


def startPeer(address, port):
    clientSocket, clientAddress = createControllerSocket(address, port)
    receiveMessage(clientSocket, clientAddress)


def createControllerSocket(address, port):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((address, port))
    serverSocket.listen()
    return serverSocket.accept()


def receiveMessage(clientSocket, clientAddress):
    sockets_list = [clientSocket]
    while True:
        read, write, exception = select.select(sockets_list, [], [])
        for sock in read:
            if sock == clientSocket:
                message = clientSocket.recv(BUFSIZE).decode()
                if not message:
                    print("Connection closed")
                    clientSocket.close()
                if "|" in message:  # Message from Controller
                    peers = message.split("|")
                    for peer in peers:
                        if "-update" in peer:
                            # TODO Send NU to all connections
                            continue
                        peer = peer.split(",")
                        if len(peer) == 1:  # First segment is name of peer
                            peerName = peer
                        else:
                            connectionDict[peer[0]] = ((peer[1], peer[2]), peer[3])  # Update connection
                return
        time.sleep(0.01)



def main():
    if len(sys.argv) == 3:
        address = sys.argv[1]
        port = sys.argv[2]
        startPeer(address, port)
    else:
        print("Error, wrong arguments")


if __name__ == '__main__':
    main()
