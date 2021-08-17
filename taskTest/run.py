import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

from app import create_app
app_ = create_app()

bashCommand = "ip addr| grep eth0"
import subprocess
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print(output)
print(output.split())
print(output.split()[13])
config = Config()
# config.from_mapping(bind='http://0.0.0.0:5000')
config.bind = ["172.17.62.242:80"] 
# config.from_toml('config.toml')
asyncio.run(serve(app_, config))