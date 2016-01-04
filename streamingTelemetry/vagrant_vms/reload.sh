BASE_IP='10.1.1.'
BASE_PORT=9999
# bring up each client
for d in ./*/ ; do 
	(cd "$d" && vagrant halt) 
done