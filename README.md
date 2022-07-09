# evade84-node
(Work in progress)

## Running
**Dependencies:**
* docker
* docker compose plugin

Clone **evade-84** repo.
```shell
git clone https://github.com/evade84/evade84-node
cd evade84-node/
git checkout cf2f4f2  # stable version, supported by eef
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
