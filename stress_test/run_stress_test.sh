#!/bin/bash

# Kill any existing locust processes
pkill -f locust

# Start locust in headless mode
locust -f locustfile.py --host http://localhost:5000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --headless \
    --only-summary \
    --logfile stress_test_results.log

# Print results
echo "Stress Test Results:"
echo "==================="
cat stress_test_results.log 