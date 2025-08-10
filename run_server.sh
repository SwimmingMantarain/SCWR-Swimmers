#!/bin/bash

fastapi dev app.py --host 0.0.0.0 &
PID=$!

sleep 3s

if command -v xdg-open > /dev/null; then
		xdg-open http://localhost:8000/
elif command -v open > /dev/null; then
		open http://localhost:8000/
else
		echo "Please manually open http://localhost:8000/"
fi

trap 'echo "Interrupted. Stopping Fastapi Server..."; kill $PID; exit' INT

wait $PID
