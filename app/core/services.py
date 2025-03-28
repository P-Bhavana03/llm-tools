import time
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.schema import Document
from app.utils.vector_store import get_vector_store
from app.core.tools import tool_registry, tools


class RAGService:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro-exp-03-25")
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-exp-03-07",
        )

        self.vector_store = get_vector_store(self.embeddings)

        # Initialize with sample function tools
        # self._initialize_function_tools()

    def _initialize_function_tools(self):
        # function_tools = [
        #     Document(
        #         page_content="Open calculator application",
        #         metadata={"function": "open_calculator"},
        #     ),
        #     Document(
        #         page_content="Open web browser", metadata={"function": "open_browser"}
        #     ),
        # ]

        function_tools = [
            Document(page_content=tool.__doc__, metadata={"function": tool.__name__})
            for tool in tools
        ]

        for tool in function_tools:
            time.sleep(30)
            self.vector_store.add_documents([tool])


# async def execute_rag_query(prompt: str) -> List[str]:
#     service = RAGService()


async def execute_query(prompt: str):
    service = RAGService()
    docs = service.vector_store.similarity_search(prompt, k=2)
    function_tools = [doc.metadata["function"] for doc in docs]
    selected_tools = [tool_registry[name] for name in function_tools]

    from langgraph.prebuilt import create_react_agent

    # agent with selected tools
    agent = create_react_agent(
        service.llm,
        tools=selected_tools,
    )

    result = await agent.ainvoke({"messages": [("user", prompt)]})
    for message in result["messages"]:
        message.pretty_print()

    res = result["messages"][-1].content
    print(res)
    return res
