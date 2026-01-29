from fastapi import APIRouter, Depends, UploadFile, HTTPException , status ,Request
from fastapi.responses import JSONResponse
from models.db_schemes.nlp import PushRequest
from models.db_schemes.project import ProjecModel

nlp_router = APIRouter(

    prefix = "/AI/nlp"

)


@nlp_router.post("/index/push/{project_id}")
async def index_project(project_id: str, request: Request,push_request: PushRequest):
    ProjecModel = await ProjecModel.create_instance(
        db_client = request.app.db
    )


    