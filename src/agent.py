from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from . import config
from . import tools

# 1. Initialize the custom LLM
# The model instance is passed directly to the agent now.
llm = ChatOpenAI(
    model=config.LLM_MODEL_NAME,
    api_key=config.LLM_API_KEY,
    base_url=config.LLM_API_URL,
    temperature=0.7,
    streaming=True,
)

# 2. Collect all the defined tools
all_tools = [
    tools.search_notes,
    tools.get_note_by_uuid,
    tools.get_note_by_path,
    tools.create_note,
    tools.update_note,
    tools.list_all_notes,
]

# 3. Create the agent using the new, simplified API
# The prompt is now handled internally by the create_agent function,
# but we can pass a system prompt for customization.
system_prompt = "You are a helpful assistant that manages an Obsidian vault. Be concise but thorough. You have access to a set of tools to interact with the vault."

agent_executor = create_agent(
    model=llm,
    tools=all_tools,
    system_prompt=system_prompt
)

# 4. Provide a simple interface to invoke the agent
def invoke_agent(input_text: str):
    """
    Invokes the agent with a given input text and returns the result.
    The input format for the new agent is a dictionary of messages.
    """
    return agent_executor.invoke({
        "messages": [
            ("user", input_text)
        ]
    })
