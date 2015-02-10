#!/bin/sh

/usr/sbin/smcroute -j eth0 239.192.37.113
/usr/sbin/smcroute -j eth0 239.192.37.44
/usr/sbin/smcroute -j eth0 239.192.37.30
/root/iptv-rtp-probe/monitor-rtp-stream.sh 239.192.37.113 &
/root/iptv-rtp-probe/monitor-rtp-stream.sh 239.192.37.44 &
/root/iptv-rtp-probe/monitor-rtp-stream.sh 239.192.37.30 &
