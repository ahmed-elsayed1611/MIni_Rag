from email import message
from ..LLMinterface import LLMinterface
from cohere import Client
import logging
from ..LLMEnums import CohereRoleEnums , DocumentTypeEnums


class CohereProvider(LLMinterface):
    def __init__(self, api_key: str, default_input_max_characters: int = 1000, default_generation_max_output_tokens: int = 1000, default_generation_temperature: float = 0.1):
        self.api_key = api_key
        self.client = Client(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, model_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = model_size

    def construct_prompt(self, prompt: str , role: str):
        return {"role": role, "content": self.process_text(prompt)}

    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, chat_history: list = [], prompt: str = None, max_output_tokens: int = None, temperature: float = None):
        if not self.client:
            self.logger.error("Cohere client not initialized")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model not initialized")
            return None
        max_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temp = temperature if temperature else self.default_generation_temperature

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            chat_history=chat_history, 
            max_tokens=max_tokens,
            temperature=temp,
            message = self.process_text(prompt)
        )
        if not response or not response.text or len(response.text) == 0:
            self.logger.error("Failed to generate text")
            return None
        return response.text

    def embed_text(self, text: str,document_type: str = None):
        if not self.client:
            self.logger.error("Cohere client not initialized")
            return None

        if not self.embedding_model_id :
            self.logger.error("Embedding model not initialized")
            return None

        input_type = DocumentTypeEnums.DOCUMENT.value
        if document_type == DocumentTypeEnums.QUERY.value:
            input_type = DocumentTypeEnums.QUERY.value

        response = self.client.embed(texts=self.process_text(text), model=self.embedding_model_id, input_type=input_type,embedding_types=["float"])
        if not response or not response.embeddings  or not response.embeddings.float:
            self.logger.error("Failed to generate embedding ")
            return None
        return response.embeddings.float[0]