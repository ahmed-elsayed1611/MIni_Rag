import os
import sys

_SRC_DIR = os.path.dirname(__file__)
_PROJECT_ROOT = os.path.abspath(os.path.join(_SRC_DIR, ".."))

if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI
from routes import base, data, nlp            # 
from helpers.config import get_settings        # 
from motor.motor_asyncio import AsyncIOMotorClient
from Stores.llm.provider.LLMProcviderFactory import LLMProviderFactory
from Stores.llm.LLMEnums import LLMEnums
from Stores.VectorDB.Providers.VectorDBProviderFactor import VectorDBProviderFactory
from Stores.llm.templates.template_parser import TemplateParser

app = FastAPI()
app.mongo = type('Mongo', (), {})()
    
async def startup():
    settings = get_settings()
    app.mongo.connection = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db = app.mongo.connection[settings.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(settings.dict())
    vector_db_provider_factory = VectorDBProviderFactory(settings.dict())

    #generation client 
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    #embedding client
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, model_size=settings.EMBEDDING_MODEL_SIZE)

    #vector db client
    app.vector_db_client = vector_db_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)

    app.vector_db_client.connect()

    #template parser
    app.template_parser = TemplateParser(language=settings.PRIMARY_LANGUAGE, default_language=settings.DEFAULT_LANGUAGE)
    
async def shutdown():
    app.mongo.connection.close()
    app.vector_db_client.disconnect()


app.router.on_startup.append(startup)
app.router.on_shutdown.append(shutdown)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
