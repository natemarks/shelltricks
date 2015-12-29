#!/bin/bash
function connect {
    nc -w 3 -zv $1 $2 > /dev/null
    if [ $? -gt 0 ]
    then
        echo "FAILED AT: ${TIME}" >> watch_tcp.log
    else
        echo "SUCCEEDED AT: ${TIME}" >> watch_tcp.log
    fi
}
TIME=$(date)
echo "ATTEMPT: ${TIME}" >> watch_tcp.log
DURATION=`(time (connect $1 $2 )) 2>&1 | grep real`
echo ${DURATION} >> watch_tcp.log
