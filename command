Command to execute docker

docker build -t fastapi-html .  &&  docker stop $(docker ps -aq) && docker rm $(docker ps -aq) && docker run -d -p 8000:80 --name fastapi-html-container fastapi-html
