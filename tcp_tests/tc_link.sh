#!/bin/bash

function change_tc {
    sudo tc qdisc replace dev enp3s0 root handle 1: netem delay 1ms loss $1%
    sleep 30
}

iperf3 -c 192.168.1.47 -p 6666 -t 150 -C bbr &

change_tc 0
change_tc 0.5
change_tc 1
change_tc 2
change_tc 3
