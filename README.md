iptv-rtp-probe
======================

A set of scripts that wrap around and parse rtpdump data for monitoring MPEG2-over-RTP video streams egressing Microsoft Mediaroom

The remote probe is assumed to be Debian or Ubuntu that is joined to multicast streams using smcroute. Once the probe is receiving the specified multicast streams rtpdump
is used to "sniff" the traffic and output to file. A python script is then used to parse and summarize the RTP packet statistics in the output file and log the summary to a log file
as well as a centralized MySQL database

Setting up a probe:

````
apt-get install -y build-essential smcroute python-mysqldb python-pip git
pip install ConfigParser

cd /usr/local/src
wget http://www.cs.columbia.edu/irt/software/rtptools/download/rtptools-1.20.tar.gz
tar -zxvf rtptools-1.20.tar.gz
cd rtptools-1.20
./confgure
make
make install

cd /root
git clone https://github.com/killminus9/iptv-rtp-probe.git

````
Tell iptv-rtp-probe where your MySQL database lives:
````
nano /root/iptv-rtp-probe/parse-rtp.cfg
````




Join a multicast group:
````
smcroute -j eth0 239.192.37.30
````

Verify group membership:
````
netstat -g
````
Start monitoring an individual RTP stream (starts rtpdump, runs the python script after 1 minute of RTP packet capture, starts a new instance of rtpdump, etc.)
````
cd /root/iptv-rtp-probe
./monitor-rtp-stream.sh 239.192.37.30 &
````

As an alternative you can edit monitor-start.sh which will automatically join
and monitor the channels specified in the script and start the monitor-rtp-stream.sh shell script

To run the startup script:
````
cd /root/iptv-rtp-probe
./monitor-start.sh
````
