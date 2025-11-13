from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List
from langchain_core.messages import BaseMessage
from . import config
from . import tools

# 1. Initialize the LLM
llm = ChatOpenAI(
    model=config.LLM_MODEL_NAME,
    api_key=config.LLM_API_KEY,
    base_url=config.LLM_API_URL,
    temperature=0.7,
    streaming=True,
)

# 2. Collect tools
all_tools = [
    tools.search_notes,
    tools.get_note_by_uuid,
    tools.get_note_by_path,
    tools.create_note,
    tools.update_note,
    tools.list_all_notes,
]

# 3. Create the agent using the new, simplified API
# The create_agent function handles the prompt internally.
# We pass the llm instance as the `model` argument.
agent_executor = create_agent(
    model=llm,
    tools=all_tools,
    system_prompt="You are a helpful assistant that manages an Obsidian vault. You are conversational and will remember previous messages."
)

# 4. Update invoke_agent to accept history
def invoke_agent(input_text: str, chat_history: List[BaseMessage]):
    """
    Invokes the agent with input text and the conversation history.
    """
    # The new agent executor expects a list of messages in the 'messages' key
    messages = chat_history + [("user", input_text)]
    return agent_executor.invoke({
        "messages": messages
    })
