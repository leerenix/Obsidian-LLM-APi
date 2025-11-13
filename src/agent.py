from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
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

# 3. Create the prompt with a placeholder for chat history
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant that manages an Obsidian vault. You are conversational and will remember previous messages."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# 4. Create the agent
# We go back to the create_tool_calling_agent to have more control over the prompt
agent = create_tool_calling_agent(llm, all_tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=all_tools, verbose=True)


# 5. Update invoke_agent to accept history
def invoke_agent(input_text: str, chat_history: List[BaseMessage]):
    """
    Invokes the agent with input text and the conversation history.
    """
    return agent_executor.invoke({
        "input": input_text,
        "chat_history": chat_history,
    })
