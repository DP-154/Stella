echo 'deploying'
docker-compose stop web
docker-compose kill web
docker-compose pull web
docker-compose up -d web
echo 'deployed'
