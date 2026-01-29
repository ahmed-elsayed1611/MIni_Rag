from enum import Enum

class LLMEnums(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"

class OpenAIRoleEnums(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class CohereRoleEnums(Enum):
    USER = "USER"
    ASSISTANT = "CHATBOT"
    SYSTEM = "SYSTEM"

    DOCUMENT = "search_document"
    QUERY  = "search_query"
 
class DocumentTypeEnums(Enum):
    QUERY = "query"
    DOCUMENT = "document"

