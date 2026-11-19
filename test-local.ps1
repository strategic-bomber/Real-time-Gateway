# Start all services
docker-compose up -d --build

# Wait for services
Start-Sleep -Seconds 10

# Run Python tests
docker-compose exec python-api pytest tests/ -v

# Run Go tests
docker-compose exec go-gateway go test ./... -v

# Test integration
curl http://localhost:8000/docs
curl http://localhost:8080/health

# Stop services
docker-compose down

#!/bin/bash
# set -e
# echo "1"
# docker-compose up -d --build
# echo "2"
# sleep 10

# docker-compose exec python-api pytest tests/ -v
# echo "3"
# docker-compose exec go-gateway go test ./... -v
# echo "4"
# curl -f http://localhost:8000/docs
# curl -f http://localhost:8080/health
# echo "5"
# docker-compose down
# echo "gg"