import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

from app import create_app
app_ = create_app()
asyncio.run(serve(app_, Config()))