# shelltricks
Silly shell scripts I keep around.  most are examples of things I forget all the time

# watch_tcp.sh
use as a background process to populate a watch_tcp.log file in the current directory
watch -n 5 'watch_tcp.sh www.google.com 80' &>/dev/null &
