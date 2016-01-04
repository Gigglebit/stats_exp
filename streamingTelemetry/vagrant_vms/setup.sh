#!/bin/bash
CLIENT=$1

echo "Creating agents ..."
# creating clients folder and copy config file
mkdir $(seq -f "agent%01g" "$CLIENT")
echo $(seq -f "agent%01g" "$CLIENT") | xargs -n 1 cp Vagrantfile
BASE_IP='10.1.1.'
BASE_PORT=9999
# bring up each client
i=3
for d in ./agent*/ ; do 
	(cd "$d" && IP=$BASE_IP$i PORT=$((BASE_PORT+$i)) vagrant up ); 
	i=$((i+1))
done
# bring up the controller
mkdir controller
cp Vagrantfile_ctrl controller/Vagrantfile
(cd controller && CONTROLLER_IP='10.1.1.2' vagrant up); 

