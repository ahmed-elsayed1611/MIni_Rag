from fastapi import APIRouter, Depends, UploadFile, HTTPException , status ,Request
from fastapi.responses import JSONResponse
from models.db_schemes.nlp import PushRequest , SearchRequest
from models.db_schemes.Mini_rag.schemes import Project
import logging
from controllers import NLPController
from models.Enums.ResponseEnums import ResponseStatus
from models.ChunckModel import ChunckModel
from models.ProjecModel import ProjectModel
from tqdm.auto  import tqdm

logger = logging.getLogger("uvicorn.error")


nlp_router = APIRouter(

    prefix = "/AI/nlp"

)


@nlp_router.post("/index/push/{project_id}")
async def index_project(project_id: int, request: Request,push_request: PushRequest):
    project_model = await ProjectModel.create_instance(
        db_client = request.app.db
    )

    chunck_model = await ChunckModel.create_instance(
        db_client = request.app.db
    )

    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": ResponseStatus.PROJECT_NOT_FOUND.value,
                "message": "Project not found"
            }
        )
    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        template_parser=request.app.template_parser
    )

    has_records  = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    collection_name = await nlp_controller.create_collection_name(project_id=project.id)
   
    await request.app.vector_db_client.create_collection(collection_name=collection_name,
    embedding_size=request.app.embedding_client.embedding_size,
    do_reset=push_request.do_reset)

    total_chuncks_count = await chunck_model.get_total_chunks_count(project_id=project.id)

    pbar = tqdm(total=total_chuncks_count,desc="Indexing",position=0)

    
    while has_records:
        page_chuncks, total_chuncks_count = await chunck_model.get_poject_chunks(
            project_id = project.id,
            page_no = page_no,
            page_size = push_request.page_size,
        )
        if len(page_chuncks) :
            page_no += 1
        if not page_chuncks or len(page_chuncks) == 0 :
            has_records = False
            break
        chuncks = list(range(idx, idx + len(page_chuncks)))
        idx += len(page_chuncks)
        is_inserted = await nlp_controller.index_into_vector_db(project = project, chunks = page_chuncks, do_reset=push_request.do_reset,chunck_id=chuncks)
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": ResponseStatus.INSERT_INTO_VECTOR_DB_FAILED.value,
                    "message": "Failed to insert into vector database"
                }
            )
        pbar.update(len(page_chuncks)) 
        inserted_items_count += len(page_chuncks)
    pbar.close()
    return JSONResponse({
        "status": ResponseStatus.INSERT_INTO_VECTOR_DB_SUCCESS.value,
        "message": f"Successfully inserted {inserted_items_count} items into vector database"
    },
        status_code=status.HTTP_200_OK,
        
    )



    


@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: int):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        template_parser=request.app.template_parser
    )

    collection_info = await nlp_controller.get_vector_db_collection_info(project=project)

    return JSONResponse(
        content={
            "status": ResponseStatus.VECTOR_DB_COLLECTION_RETRIVED.value,
            "collection_info": collection_info
        }
    )


@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: int, search_request: SearchRequest):
    
    logger.info(f"Search request received for project {project_id}: {search_request.text}")
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    logger.info(f"Project found: {project}")

    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        embedding_client=request.app.embedding_client,
        generation_client=request.app.generation_client,
        template_parser=request.app.template_parser
    )

    logger.info("NLP Controller created, starting search...")
    
    try:
        results = await nlp_controller.search_vector_db_collection(
            project=project, text=search_request.text, limit=search_request.limit
        )
        logger.info(f"Search completed. Results type: {type(results)}, Value: {results}")
    except Exception as e:
        logger.error(f"Search failed with exception: {e}")
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "signal": ResponseStatus.VECTOR_DB_SEARCH_FAILED.value,
                    "message": f"Search exception: {str(e)}"
                }
            )

    if not results or results == False:
        logger.error(f"Search returned no results for project {project_id} with text: {search_request.text}")
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.VECTOR_DB_SEARCH_FAILED.value,
                    "message": "No results found or search failed"
                }
            )
    
    # Convert results to serializable format
    try:
        results_list = []
        for result in results:
            if hasattr(result, 'dict'):
                results_list.append(result.dict())
            else:
                results_list.append({
                    "text": str(result.text) if hasattr(result, 'text') else str(result),
                    "score": float(result.score) if hasattr(result, 'score') else 0.0
                })
    except Exception as e:
        logger.error(f"Error converting search results: {e}")
        return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "signal": ResponseStatus.VECTOR_DB_SEARCH_FAILED.value,
                    "message": f"Error processing results: {str(e)}"
                }
            )
    
    logger.info(f"Returning {len(results_list)} search results")
    
    return JSONResponse(
        content={
            "signal": ResponseStatus.VECTORDB_SEARCH_SUCCESS.value,
            "results": results_list
        }
    )
@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: int, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    nlp_controller = NLPController(
        vector_db_client=request.app.vector_db_client,
        generation_client=request.app.generation_client,
        embedding_client=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )

    answer, full_prompt, chat_history = await nlp_controller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit,
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseStatus.RAG_ANSWER_ERROR.value
                }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseStatus.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )
