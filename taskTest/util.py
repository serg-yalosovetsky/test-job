import asyncio
import datetime
import logging
import hmac
import traceback
from base64 import b64encode
from time import time


from quart import current_app
from sqlalchemy.exc import SQLAlchemyError

from app import db
from models import Orders


class LoopTimer:
    """Run a task repeatedly at spaced intervals.

    The provided callback function is called in a loop, which sleeps at the
    beginning of each iteration for the specified timeout period.
    """

    def __init__(self, timeout, callback, **kwargs):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.create_task(self._run())
        self._kwargs = kwargs

    async def _run(self):
        while True:
            await asyncio.sleep(self._timeout)
            try:
                await self._callback(**self._kwargs)
            except Exception as e:
                logging.exception(
                    "Exception during excecution of LoopTimer callback function"
                )

    def cancel(self):
        """Cancel the running task."""
        self._task.cancel()


def commit_database(log_error=True, rollback=True, reraise=False):
    try:
        db.session.commit()
        return True
    except SQLAlchemyError:
        if log_error:
            logging.exception('Exception during database commit.')

        if rollback:
            db.session.rollback()

        if reraise:
            raise

        return False

