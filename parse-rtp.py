#!/usr/bin/env python
import re
import sys
import time
import datetime
import socket
import MySQLdb as mdb
import ConfigParser

# Changelog
# v1 - Initial version
# v2 - Added logging to MySQL server
# v3 - Added Out-of-Order sequence checking
# v4 - Added Out-of-Order sequence logging to mysql
# v5 - Added ConfigParser support

def sequence_rollover_split(index,sequence):
	global rollover
	global packets_sequence
	global checked

	prevIndex = index - 1
	prevSequence = int(packets_sequence[prevIndex])
	
	if int(sequence) == 0:
		expectedPrevSeq = 65535
	else:
		expectedPrevSeq = int(sequence) - 1

	if (int(sequence) - prevSequence) < -10000:
		prerollover = rollover
		rollover += 1
		checked.append([])

	checked[rollover].append(sequence)	


def find_missing(int_list,firstrow,lastrow):
	original_set = set(int_list)
	smallest_item = min(original_set)
	largest_item = max(original_set)
	if firstrow:
		low = smallest_item
		if lastrow:
			high = largest_item
		else:
			high = 65535
	else:
		low = 0
		if lastrow:
			high = largest_item
		else:
			high = 65535
	full_set = set(xrange(low, high + 1))
	return sorted(list(full_set - original_set))
		

def find_oos(int_list):
	x = 0
	oos = 0
	while x < len(int_list) - 1:
		if int_list[x+1] - int_list[x] != 1:
			oos += 1
		x += 1			
	return oos

def calculate_packetloss():
	global checked
	global possible_lost
	global outoforder

	rows = len(checked)
	rcount = 1
	lost_packets = 0

	for x in checked:
        	# First and only row
        	if rcount == 1 & rcount == rows:
                	missing = find_missing(x,1,1)
                	lost_packets += len(missing)
			oos = find_oos(x)
                	outoforder += oos
			continue

        	# First row
        	if rcount == 1 & rcount != rows:
                	missing = find_missing(x,1,0)
                	lost_packets += len(missing)
                        oos = find_oos(x)
                	outoforder += oos
			rcount += 1
                	continue
        
		# Middle row(s)
        	if rows != rcount:
                	missing = find_missing(x,0,0)
                	lost_packets += len(missing)
                        oos = find_oos(x)
                	outoforder += oos
			rcount += 1
                	continue
        
		# Last row
        	if rows == rcount:
                	missing = find_missing(x,0,1)
                	lost_packets += len(missing)
                        oos = find_oos(x)
                        outoforder += oos

	return lost_packets

def get_ts():
	ts = time.time()
	dt = datetime.datetime.fromtimestamp(ts)
	return dt


def log_sql(qs):
	global sqlhost
	global sqluser
	global sqlpass
	global dbname

	try:
		con = mdb.connect(sqlhost, sqluser, sqlpass, dbname)
		cur = con.cursor()
		cur.execute(qs)

	except mdb.Error, e:
		print "Error %d: %s" % (e.args[0],e.args[1])
		sys.exit(1)

	finally:
		if con:
			# Commit the query
			con.commit()
			# Close SQL connection
			con.close()


def get_stream_ip(inputfile):
	match = re.search (r"(\d+\.\d+\.\d+\.\d+)", inputfile)
	return match.group(1)


# Make sure input file was passed and that we can read it
try:
        sys.argv[1]
except:
        print "Error - must pass input file name"
        sys.exit()

inputfile = sys.argv[1]

try:
        file = open(inputfile, 'r')
except:
        print inputfile + " does not exist or cannot be opened"
        sys.exit()



# Vars
count = 0
packets_ts = []
packets_sequence = []
rollover = 0
checked = []
checked.append([])
outoforder = 0

# Load in config file data
conf = ConfigParser.RawConfigParser()
conf.read('parse-rtp.cfg')

sqlhost = conf.get('database', 'host')
sqluser = conf.get('database', 'user')
sqlpass = conf.get('database', 'password')
dbname = conf.get('database', 'name')
probeid = socket.gethostname()
streamip = get_stream_ip(str(inputfile))


for line in file:
        line = line.rstrip('\r\n')
	match = re.search (r"^(\d+\.\d+|-\d+\.\d+)\s+(\d+)\s+(\d+)",line)
	if match:
		ts = match.group(1)
		rtpts = match.group(2)
		sequence = match.group(3)

		packets_ts.append(ts)
		packets_sequence.append(int(sequence))

		# Do some stuff here for checking delay, jitter, etc eventually

		count += 1	


index = 0
while index < count:
	if (index != 0):
		sequence_rollover_split(index,packets_sequence[index])
	else:
		checked[rollover].append(packets_sequence[index])

	index += 1


# Output
ts = get_ts()
print str(ts) + " - " + str(inputfile) + " - ",
print "Total packets: " + str(count) + " ",
lost_packets = calculate_packetloss()
if outoforder > 0:
	# 1 out of order packet will throw off 2 others show divide by 3 
	outoforder = outoforder / 3
print "Lost packets: " + str(lost_packets) + " ",
print "Out of order packets: " + str(outoforder)

# Build SQL Query
qs = "INSERT INTO log (probeid, streamip, totalpackets, lostpackets, oospackets) VALUES ('%s', '%s', '%d', '%d', '%d')" % (probeid, streamip, count, lost_packets, outoforder)
# Execute SQL Query
log_sql(qs)
