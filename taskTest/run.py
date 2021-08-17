import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
import os

from app import create_app
app_ = create_app()

bashCommand = "ip addr"
import subprocess
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output, error = process.communicate()
print(output)
for s in str(output).split():
    if '172' in s:
        ip = s.split('/')[0]
        break
print(ip)
try:
    port = os.environ['PORT']
except:
    port = 8000
        
# print(output.split()[13])

config = Config()
# config.from_mapping(bind='http://0.0.0.0:5000')
config.bind = [f'{ip}:{port}'] 
# config.from_toml('config.toml')
asyncio.run(serve(app_, config))