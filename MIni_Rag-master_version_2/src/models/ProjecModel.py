from .BaseDataModel import BaseDataModel
from .db_schemes.Mini_rag.schemes import Project 
from .Enums.DataBaseEnums import DataBasesEnum
from sqlalchemy import select, func

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.db_client = db_client
    
    @classmethod
    async def create_instance(cls,db_client: object):
        instance = cls(db_client)
        return instance


    async def create_project(self, project: Project):
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.refresh(project)
        return project



    async def get_project_or_create_one(self, project_id: str):
        
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.id == project_id)
                result = await session.execute(query)
                project_record = result.scalar_one_or_none()
                if project_record:
                    return project_record
                else:
                    new_project = Project(id=project_id)
                    session.add(new_project)
            await session.refresh(new_project)
            return new_project



    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        async with self.db_client() as session:
            async with session.begin():
                total_query = select(func.count(Project.id))
                total_result = await session.execute(total_query)
                total_documents = total_result.scalar()
                query = select(Project).offset((page - 1) * page_size).limit(page_size)
                result = await session.execute(query)
                projects = result.scalars().all()
                return projects, total_documents