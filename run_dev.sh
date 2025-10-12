#!/bin/bash

fastapi dev app.py --host 0.0.0.0 &
BACK_PID=$!

cd frontend
npm run dev -- --host 0.0.0.0 &
FRONT_PID=$!

sleep 5s

if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5173/
elif command -v open > /dev/null; then
    open http://localhost:5173/
else
    echo "Please manually open http://localhost:5173/"
fi

trap 'clear; 
echo "Interrupted. Stopping Fastapi Server...";
kill $BACK_PID; wait $BACK_PID 2>/dev/null;
kill $FRONT_PID; wait $FRONT_PID 2>/dev/null;
clear; exit' INT

wait
