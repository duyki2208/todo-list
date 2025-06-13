# Stress Test for Todo App

This directory contains stress testing scripts for the Todo application using Locust.

## Prerequisites

- Python 3.8+
- Locust (`pip install locust==2.24.0`)
- Todo App running on `http://localhost:5000`

## Files

- `locustfile.py`: Contains the stress test scenarios
- `run_stress_test.sh`: Shell script to run the stress test
- `stress_test_results.log`: Generated test results

## Test Scenarios

The stress test simulates the following user behaviors:

1. User Registration and Login
2. Fetching Tasks
3. Creating New Tasks
4. Updating Existing Tasks
5. Deleting Tasks

## Running the Test

1. Make sure the Todo App is running:

```bash
docker-compose up -d
```

2. Make the script executable:

```bash
chmod +x run_stress_test.sh
```

3. Run the stress test:

```bash
./run_stress_test.sh
```

## Test Parameters

- Number of Users: 100
- Spawn Rate: 10 users/second
- Test Duration: 5 minutes
- Host: http://localhost:5000

## Monitoring

During the test, you can monitor:

1. API Service logs:

```bash
docker-compose logs -f api_service
```

2. Task Service logs:

```bash
docker-compose logs -f task_service
```

3. User Service logs:

```bash
docker-compose logs -f user_service
```

4. MongoDB logs:

```bash
docker-compose logs -f mongodb-primary
```

## Results

The test results will be saved in `stress_test_results.log` and will include:

- Total Requests
- Failed Requests
- Response Time Statistics
- Requests Per Second
- User Count
