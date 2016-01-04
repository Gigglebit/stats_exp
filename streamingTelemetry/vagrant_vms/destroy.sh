#!/bin/bash


echo "Destroying all clients"
for d in ./*/ ; do 
	(cd "$d" && vagrant destroy); 
done
rm -rf agent*