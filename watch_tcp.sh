#!/bin/sh
TIME=$(date)
echo "ATTEMPT: ${TIME}" >> watch_tcp.log
DURATION=`(time nc -w 3 -zv $1 $2  >> /dev/null) 2>&1 | grep real`
if [ $? !=  0 ]
then
    echo "FAILED AT: ${TIME}" >> watch_tcp.log
else
    echo "SUCCEEDED AT: ${TIME}" >> watch_tcp.log
fi
echo ${DURATION} >> watch_tcp.log
