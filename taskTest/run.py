import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
import os
import subprocess
import charset_normalizer

from app import create_app
app_ = create_app()

bash_command = "ip addr"
cmd_command = "ipconfig"
try:
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    pc = 'linux'
except:
    process = subprocess.Popen(cmd_command.split(), stdout=subprocess.PIPE)
    pc = 'windows'
output, error = process.communicate()
if pc == 'windows':
    code_page = charset_normalizer.detect(output)
    print(code_page) 
    output = output.decode(code_page['encoding'])
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