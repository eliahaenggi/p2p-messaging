# P2P Messaging Tool in Python

A simple peer-to-peer messaging system allowing communication between peers or between a peer and a controller, with dynamic topology updates and cost-based routing.

---

## Features
- Peer-to-peer and peer-to-controller messaging
- Dynamic network topology updates
- Cost-based message routing

---

## Implementation

### Controller
- Reads network topology from a **readfile**:
node1,ip,port|node2,ip,port|node3,ip,port|...
node1,node2,10
node2,node3,4
node3,node1,20

- Maintains:
  - `nameDict`: peer → (IP, port)
  - `connectionDict`: (peer1, peer2) → cost
  - `socketDict`: peer → socket

- Sends peer list to all peers (`sendNames`):
-n|OwnPeer|IP|Port|OtherPeer|...
- Sends neighbor lists (`sendNTU`) with `-update` at the last message

### Peer
- Maintains:
  - `connectionDict`: peer → ((IP, port), cost)
  - `peerNameList`: all peers
- Sends updates (NU):
OwnPeerOtherPeer,CostOtherPeer,Cost~...

- Message forwarding format:
Receiver^Message

---

## Usage
1. Start **Controller.py** with the readfile.
2. Start each **Peer.py** with its name and port.
3. Peers exchange updates and forward messages automatically.

---

## Notes
- Text-based protocol uses `-n` for new topology and `-update` to signal completion.
- Cost values are used for routing messages efficiently.
