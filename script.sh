echo 'deploying'
docker-compose down
docker-compose pull web
docker-compose up -d
echo 'deployed'
