from ..LLMinterface import LLMinterface
from openai import OpenAI
import logging
import hashlib
import random
from ..LLMEnums import OpenAIRoleEnums 
from typing import List, Union 

class OpenAiProvider(LLMinterface):
    def __init__(self,api_key:str,api_url:str=None,
                default_input_max_characters:int=1000,
                default_generation_max_output_tokens:int=1000,
                default_generation_temperature:float=0.1):
        self.api_key = api_key
        self.api_url = api_url
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        base_url = self.api_url
        if isinstance(base_url, str):
            base_url = base_url.strip()
            if base_url == "":
                base_url = None
            elif not (base_url.startswith("http://") or base_url.startswith("https://")):
                base_url = f"https://{base_url}"

        self.client = OpenAI(api_key=self.api_key, base_url=base_url)
        self.logger = logging.getLogger(__name__)
        self._logged_embedding_fallback_warning = False
        self.enums = OpenAIRoleEnums

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
            self.logger.error("OpenAI client not initialized")
            return None
        if not self.generation_model_id:
            self.logger.error("Generation model not initialized")
            return None
        max_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temp = temperature if temperature else self.default_generation_temperature

        # Only append user prompt if it's provided (not None)
        if prompt is not None:
            chat_history.append(self.construct_prompt(prompt = prompt, role = OpenAIRoleEnums.USER.value))

        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_tokens,
            temperature=temp
        )
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message.content:
            self.logger.error("Failed to generate text")
            return None
        return response.choices[0].message.content

    def embed_text(self, text: Union[str, list],document_type: str = None):
        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return None

        if isinstance(text, str):
            text = [text]

        if not self.embedding_model_id :
            self.logger.error("Embedding model not initialized")
            return None

        try:
            response = self.client.embeddings.create(
                model=self.embedding_model_id,
                input=text
            )
            if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
                self.logger.error("Failed to generate embedding")
                return None
            return [f for f in response.data[0].embedding] 
        except Exception as e:
            # Fallback for models that don't support embeddings (e.g., Groq chat models)
            if not self._logged_embedding_fallback_warning:
                self.logger.warning(f"Embedding API failed ({e}), returning dummy vector of size {self.embedding_size}")
                self._logged_embedding_fallback_warning = True

            size = self.embedding_size or 1536
            seed_material = f"{self.embedding_model_id}|{document_type or ''}|{text}".encode("utf-8", errors="ignore")
            seed = int.from_bytes(hashlib.sha256(seed_material).digest()[:8], "big", signed=False)
            rng = random.Random(seed)
            return [rng.uniform(-1.0, 1.0) for _ in range(size)]