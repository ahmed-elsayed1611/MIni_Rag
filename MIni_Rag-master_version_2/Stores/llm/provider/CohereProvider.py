from email import message
from ..LLMinterface import LLMinterface
from cohere import Client
import logging
from ..LLMEnums import CohereRoleEnums , DocumentTypeEnums
from typing import List , Union
import time
import random
import httpx


class CohereProvider(LLMinterface):
    def __init__(self, api_key: str, default_input_max_characters: int = 1000, default_generation_max_output_tokens: int = 1000, default_generation_temperature: float = 0.1):
        self.api_key = api_key
        timeout = httpx.Timeout(connect=30.0, read=60.0, write=60.0, pool=60.0)
        self.client = Client(api_key=self.api_key, timeout=timeout)
        self.logger = logging.getLogger(__name__)
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        self.enums = CohereRoleEnums

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, model_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = model_size

    def construct_prompt(self, prompt: str , role: str):
        return {"role": role, "content": prompt}

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

    def embed_text(self, text: Union[str, list],document_type: str = None):
        vectors = self.embed_texts(texts=[text], document_type=document_type)
        if not vectors or len(vectors) == 0:
            return None
        if isinstance(vectors, list):
            return vectors[0]
        return vectors

    def embed_texts(self, texts: list, document_type: str = None):
        if not self.client:
            self.logger.error("Cohere client not initialized")
            return None

        if not self.embedding_model_id :
            self.logger.error("Embedding model not initialized")
            return None

        input_type = CohereRoleEnums.DOCUMENT.value
        if document_type == DocumentTypeEnums.QUERY.value:
            input_type = CohereRoleEnums.QUERY.value

        processed_texts = [self.process_text(t) for t in texts]

        all_vectors = []
        batch_size = 8
        max_retries = 6

        for i in range(0, len(processed_texts), batch_size):
            text_batch = processed_texts[i:i + batch_size]
            last_err = None

            for attempt in range(max_retries):
                try:
                    response = self.client.embed(
                        texts=text_batch,
                        model=self.embedding_model_id,
                        input_type=input_type,
                        embedding_types=["float"],
                    )

                    if not response or not response.embeddings or not response.embeddings.float:
                        self.logger.error("Failed to generate embedding ")
                        return None

                    all_vectors.extend([f for f in response.embeddings.float])
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    err_txt = str(e)
                    is_timeout = isinstance(e, (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.WriteTimeout, httpx.PoolTimeout)) or ("ConnectTimeout" in err_txt) or ("ReadTimeout" in err_txt) or ("timed out" in err_txt.lower())
                    is_rate_limited = ("TooManyRequests" in err_txt) or ("status_code: 429" in err_txt) or ("rate limit" in err_txt.lower())
                    if (not is_rate_limited and not is_timeout) or attempt == max_retries - 1:
                        raise

                    sleep_s = min(60, (2 ** attempt) + random.random())
                    if is_timeout:
                        self.logger.warning(f"Cohere request timed out. Retrying in {sleep_s}s (attempt {attempt + 1}/{max_retries})")
                    else:
                        self.logger.warning(f"Cohere rate limit hit (429). Retrying in {sleep_s}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(sleep_s)

            if last_err is not None:
                raise last_err

        return all_vectors