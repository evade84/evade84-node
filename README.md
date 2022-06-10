# evade84-node
## Running
**Dependencies:**
* docker
* docker compose plugin

Clone **evade-84** repo.
```shell
git clone https://github.com/evade84/evade84-node
cd evade84-node/
```
Create `.env` file and fill it.
```shell
cp .env.example .env
vim .env
```
Build docker images and run them using docker-compose
```shell
docker compose build
docker compose up
```
Done! You are running evade84-node.
