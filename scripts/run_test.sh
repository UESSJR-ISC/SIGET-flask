docker run -d --name siget-test -v siget-test-vol:/siget-vol -p 172.16.4.200:5000:5000 --env DOCKER=1 --restart always edo/siget-test:1.0
docker ps -a
