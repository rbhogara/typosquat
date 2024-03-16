# typosquat
code for typosquatting


docker stop $(docker ps -aq) 
docker rm $(docker ps -aq) 
docker build -t fastapi-html .  
docker run -d -p 8000:80 --name fastapi-html-container fastapi-html
