import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

from app import create_app
app_ = create_app()

config = Config()
# config.from_mapping(bind='http://0.0.0.0:5000')
config.bind = ["192.168.0.165:80"] 
# config.from_toml('config.toml')
asyncio.run(serve(app_, config))