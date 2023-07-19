docker run -d --name siget-prod -v siget-prod-vol:/siget-vol -p 172.16.4.200:80:5000 --env DOCKER=1 --restart always edo/siget-prod:1.0
docker ps -a
