# Server Golem
## A discord bot for starting servers.

## Usage
Servers should be startable via docker compose.  
Currently bot.py needs to reside in the same folder as your docker-compose.yml, currently working on getting the bot also running in a docker container.  
Should have the following variables set in a .env  
<ul>
    <li>TOKEN</li>
    <li>APP_ID</li>
    <li>PUB_KEY</li>
    <li>PREFIX, defualt=/</li>
    <li>AUTHORIZED_ROLE</li>
    <li>GUILD_ID, deafault=None</li>
</ul>

