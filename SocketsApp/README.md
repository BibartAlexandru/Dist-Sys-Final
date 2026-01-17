# Use case 
- Load balances TCP traffic at layer 4
- Client initiates a connection -> assign a server in a Round-Robin manner -> create TCP session with server and exchange the received bytes between the client and created connection 
# Usage
- Install docker
```
git clone https://github.com/BibartAlexandru/Dist-Sys-Final.git
cd SocketsApp/src
chmod +x ./re # restarts containers
chmod +x ./lg # checks load balancer logs
chmod +x ./load-bal-capture # Live pcap with tcpdump of load-balancer traffic
chmod +x ./test # Sends 10 http requests with curl to the load-balancer
./re
```
- Now you can navigate to `http://localhost:8000` in your browser and see the `it-tools` page. Check out `it-tools` here (it's a great project): https://hub.docker.com/r/corentinth/it-tools
