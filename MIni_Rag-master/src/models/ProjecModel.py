from .BaseDataModel import BaseDataModel
from .db_schemes.project import project
from .Enums.DataBaseEnums import DataBasesEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBasesEnum.Collection_Projects_name.value]

    async def create_project(self, project: project):
        result = await self.collection.insert_one(project.dict())
        project._id = result.inserted_id
        return project

    async def get_project_or_create_one(self, project_id: str):
        record = await self.collection.find_one({"project_id": project_id})
        if record:
            return record
        else:
            new_project = project(project_id=project_id)
            return await self.create_project(new_project)

    async def get_all_projects(self, page: int = 1, page_size: int = 10):
        total_documents = await self.collection.count_documents({})
        total_pages = (total_documents + page_size - 1) // page_size
        
        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)

        projects = []
        async for document in cursor:
            projects.append(project(**document))
        return projects, total_pages