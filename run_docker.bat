@echo off
set IMAGE_NAME=dps-app
set PORT=8000

echo Building Docker image...
docker build -t %IMAGE_NAME% .

echo Running Docker container...
docker run -p %PORT%:%PORT% %IMAGE_NAME%
