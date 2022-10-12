#!/bin/bash

CONSUL_NAME="intent_prod"
PORT=8077

CMD="python app.py --name $CONSUL_NAME --port $PORT"
echo $CMD
$CMD