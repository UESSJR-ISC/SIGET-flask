docker run -d --name siget-test -v siget-test-vol:/siget-vol -p 172.16.4.200:80:5000 --env DOCKER=1 edo/siget-test:1.0
docker ps -a