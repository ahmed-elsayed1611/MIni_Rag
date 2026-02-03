from Stores.llm.LLMEnums import LLMEnums
from .CohereProvider import CohereProvider
from .OpenAiProvider import OpenAiProvider


class LLMProviderFactory:
    def __init__(self,config:dict):
        self.config = config

    
    def create(self,provider:str):
        provider = (provider or "").strip().upper()
        if provider == LLMEnums.OPENAI.value:
            return OpenAiProvider(
            api_key=self.config["OPENAI_API_KEY"],
            api_url=self.config["OPENAI_API_URL"],
            default_input_max_characters=self.config["default_input_max_characters"],
            default_generation_max_output_tokens=self.config["default_generation_max_output_tokens"],
            default_generation_temperature=self.config["default_generation_temperature"]
            )
        if provider == LLMEnums.COHERE.value:
            return CohereProvider(
            api_key=self.config["COHERE_API_KEY"],
            default_input_max_characters=self.config["default_input_max_characters"],
            default_generation_max_output_tokens=self.config["default_generation_max_output_tokens"],
            default_generation_temperature=self.config["default_generation_temperature"]
            )
        if provider == LLMEnums.GROQ.value:
            return OpenAiProvider(
            api_key=self.config["GROQ_API_KEY"],
            api_url=self.config["GROQ_API_URL"],
            default_input_max_characters=self.config["default_input_max_characters"],
            default_generation_max_output_tokens=self.config["default_generation_max_output_tokens"],
            default_generation_temperature=self.config["default_generation_temperature"]
            )

        return None