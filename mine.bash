#!/bin/bash

curl -X POST -H "Content-Type: application/json" -d '{"transactions": [{"sender": "Alice", "receiver": "Bob", "amount": 10}]}' http://localhost:5001/mine &

echo sleeping
sleep 8

curl -X POST -H "Content-Type: application/json" -d '{"transactions": [{"sender": "Alice", "receiver": "Bob", "amount": 10}]}' http://localhost:5000/mine &
