import sys
import socket
import select
import time

BUFSIZE = 512
peerName = ""
connectionDict = {}  # Dictionary of connections, name as key, ((ip, port), number) as value


def startPeer(address, port):
    while True:
        receiveMessage(address, port)


# Used to receive NTU's from the controller and NU's from other peers. New socket is used for every message
def receiveMessage(address, port):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((address, port))
    serverSocket.listen()
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
                if "|" in message:  # Message from Controller about connection (of the form ...|name,ip,port,number|...
                    peers = message.split("|")
                    for peer in peers:
                        if "-update" in peer:  # -update if peer is last to be informed
                            # TODO Send NU to all connections
                            continue
                        peer = peer.split(",")
                        if len(peer) == 1:  # First segment is name of peer
                            peerName = peer
                        else:
                            connectionDict[peer[0]] = ((peer[1], peer[2]), peer[3])  # Update connection
                clientSocket.close()
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
