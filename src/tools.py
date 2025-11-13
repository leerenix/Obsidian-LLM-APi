import requests
import json
from langchain.tools import tool
from .config import OBSIDIAN_API_URL

# It's better to handle the API response formatting within the tools
# to provide clean, readable output to the LLM.

@tool
def search_notes(query: str, limit: int = 5) -> str:
    """
    Searches for notes in the Obsidian vault based on semantic similarity.
    Use this to find notes related to a specific topic or question.
    Returns a JSON string of notes with their content, UUID, filepath, and similarity score.
    """
    try:
        response = requests.get(
            f"{OBSIDIAN_API_URL}/api/search",
            params={"q": query, "limit": limit},
            timeout=15,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error: Could not search notes. {e}"

@tool
def get_note_by_uuid(uuid: str) -> str:
    """
    Retrieves the full content of a single note using its unique UUID.
    Use this when you have a UUID and need to read the note's content.
    Returns the note's content, title, and filepath as a JSON string.
    """
    try:
        response = requests.get(f"{OBSIDIAN_API_URL}/api/note/{uuid}", timeout=10)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error: Could not get note with UUID {uuid}. {e}"

@tool
def get_note_by_path(filepath: str) -> str:
    """
    Retrieves the full content of a single note using its relative file path.
    Use this when you know the exact file path of a note.
    Returns the note's content, title, and UUID as a JSON string.
    """
    try:
        response = requests.get(
            f"{OBSIDIAN_API_URL}/api/note/by-path",
            params={"path": filepath},
            timeout=10,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error: Could not get note with path {filepath}. {e}"

@tool
def create_note(filepath: str, content: str) -> str:
    """
    Creates a new note in the Obsidian vault with the given content and filepath.
    The filepath should be relative to the vault root and end with .md.
    Use this to create new notes or save information.
    Returns a confirmation message with the new note's UUID.
    """
    try:
        response = requests.post(
            f"{OBSIDIAN_API_URL}/api/note",
            json={"filepath": filepath, "content": content},
            timeout=15,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error: Could not create note at {filepath}. {e}"

@tool
def update_note(uuid: str, content: str) -> str:
    """
    Updates the entire content of an existing note identified by its UUID.
    Use this to modify or add to existing notes.
    The existing content will be completely replaced.
    Returns a confirmation message.
    """
    try:
        response = requests.patch(
            f"{OBSIDIAN_API_URL}/api/note/{uuid}",
            json={"content": content, "update_embedding": True},
            timeout=15,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error: Could not update note with UUID {uuid}. {e}"

@tool
def list_all_notes() -> str:
    """
    Lists all notes in the Obsidian vault, providing their UUID, title, and filepath.
    Use this to get an overview of the vault's contents or to find specific files.
    Returns a JSON string containing a list of all notes.
    """
    try:
        # The API paginates, so we fetch a large limit to get a comprehensive list.
        response = requests.get(f"{OBSIDIAN_API_URL}/api/notes/list", params={"limit": 500}, timeout=20)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.RequestException as e:
        return f"Error: Could not list all notes. {e}"
