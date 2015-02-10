#!/bin/bash

if [ -z "$1" ]; then
	echo "Usage: monitor-rtp-stream.sh multicastip"
	exit
fi

c=1
while true; do 
	`/usr/local/bin/rtpdump -F short -t 1 -o /root/iptv-rtp-probe/$1-$c.rtp $1/7534`;  
	/usr/bin/python /root/iptv-rtp-probe/parse-rtp.py /root/iptv-rtp-probe/$1-$c.rtp >> /root/iptv-rtp-probe/rtplog.log; 
	/bin/rm /root/$1-$c.rtp;
	(( c++ ))
done

