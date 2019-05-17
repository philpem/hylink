#!/bin/bash

# repeater IP
REPEATER=10.0.0.96

# repeater controller IP
RPTRCON=10.0.0.230

sudo ip addr add $RPTRCON dev br0 label br0:1
sudo ip route add $REPEATER dev br0 src $RPTRCON
