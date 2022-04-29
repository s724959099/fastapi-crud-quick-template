"""Main programe"""
import os
import sys

import uvicorn
from api.v1.router import api_router
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from log import logger, setup_logging
from pony.orm import db_session

app_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, app_path)
VERSION = os.environ.get('TAG', '0.0.1')
logger.info(f'version: {VERSION}')
FAST_API_TITLE = 'DEMO TITLE'

app = FastAPI(
    version=VERSION,
    title=FAST_API_TITLE,

)

origins = [
    '*'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix='/api/v1')


@app.on_event('startup')
async def startup_event():
    """setup logging"""
    setup_logging()
    # todo
    # app.add_middleware(
    #     AuthenticationMiddleware,
    #     backend=AuthenticationBackend()
    # )


@app.middleware('http')
async def add_pony(request: Request, call_next):
    """add pony for each api"""
    with db_session:
        response = await call_next(request)
        return response


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=5000, log_level='info',
                reload=True, workers=1)
