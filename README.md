# shelltricks
Silly shell scripts I keep around.  most are examples of things I forget all the time

# watch_tcp.sh
use as a background process to populate a watch_tcp.log file in the current directory
watch -n 5 'watch_tcp.sh www.google.com 80' &>/dev/null &


# purge-tree.py
used to move rrd data from the zenoss collector directory tree by finding rrds
that are aged out, recreating their directory path in a new location and moving
those aged rrds out to the new location. This allows us to run without the
data, but still be able to put them back if needed wihtout burning a lot of new
disk space.

# exportCollectorDetails.py
the stdio form this script is in the format of an ansible inventory file.  it
also creates a yamls list of rht collector details which I'll use in
salt-collector-check.py to verofy that all the collectors are in salt, working
correctly.  A manual task would be removeing collecotrs form salt that are no
longer in use.,E
