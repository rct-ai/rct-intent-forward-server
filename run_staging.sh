#!/bin/bash

CONSUL_NAME="intent-staging"
PORT=8078

CMD="python app.py --name $CONSUL_NAME --port $PORT"
echo $CMD
$CMD
