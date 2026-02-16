from string import Template

#### RAG PROMPTS ####

#### System ####

system_prompt = Template("\n".join([
    "You are an intelligent assistant designed to provide accurate, helpful responses based on provided documents.",
    "You will be given a set of documents that are relevant to the user's query.",
    "Your task is to generate a comprehensive response based ONLY on the information in these documents.",
    "Carefully analyze all provided documents and use the most relevant information to answer the user's question.",
    "If the documents don't contain sufficient information to answer the question, politely indicate this.",
    "Always respond in the same language as the user's query.",
    "Be thorough, accurate, and provide specific details from the documents when possible.",
    "Structure your answer clearly with proper formatting when appropriate.",
]))

#### Document ####
document_prompt = Template(
    "\n".join([
        "## Document $doc_num:",
        "### Content:",
        "$chunk_text",
        "---",
    ])
)

#### Footer ####
footer_prompt = Template("\n".join([
    "Based only on the above documents, please generate an answer for the user.",
    "## Question:",
    "$query",
    "",
    "## Answer:",
]))