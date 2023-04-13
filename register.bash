#!/bin/bash
curl -X POST -H "Content-Type: application/json" -d '{"nodes": ["localhost:5001"]}' http://localhost:5000/nodes/register
curl -X POST -H "Content-Type: application/json" -d '{"nodes": ["localhost:5000"]}' http://localhost:5001/nodes/register

