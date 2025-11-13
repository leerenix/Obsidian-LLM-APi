from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import create_db_and_tables
from .agent import invoke_agent
import logging
from langchain_core.messages import HumanMessage, AIMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Obsidian LLM Assistant",
    description="An LLM assistant for your Obsidian vault, powered by LangChain.",
    version="0.1.0",
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

import json

# Custom JSON encoder to handle non-serializable objects like LangChain messages
class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'dict'):
            return o.dict()
        if isinstance(o, (set, tuple)):
            return list(o)
        # Add other type handlers as needed
        return f"<<non-serializable: {type(o).__name__}>>"

@app.websocket("/ws/{dialog_id}")
async def websocket_endpoint(websocket: WebSocket, dialog_id: int):
    await websocket.accept()
    logger.info(f"WebSocket connection established for dialog {dialog_id}.")

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message from client for dialog {dialog_id}: {data}")

            # Correctly handle DB session per message
            with next(database.get_db()) as db:
                # Save user message
                user_message = database.Message(dialog_id=dialog_id, role="user", content=data)
                db.add(user_message)
                db.commit()

            await websocket.send_json({"type": "status", "message": "Processing your request..."})

            try:
                # --- Fetch Chat History ---
                history = db.query(database.Message).filter(database.Message.dialog_id == dialog_id).order_by(database.Message.created_at).all()
                chat_history = []
                for msg in history:
                    if msg.role == "user":
                        chat_history.append(HumanMessage(content=msg.content))
                    elif msg.role == "assistant":
                        chat_history.append(AIMessage(content=msg.content))

                # --- Invoke Agent with History ---
                result = invoke_agent(data, chat_history)

                final_answer = ""
                if isinstance(result.get("messages"), list) and len(result["messages"]) > 0:
                    final_answer = result["messages"][-1].content

                # Correctly handle DB session per message
                with next(database.get_db()) as db:
                    # Save assistant message
                    assistant_message = database.Message(dialog_id=dialog_id, role="assistant", content=final_answer)
                    db.add(assistant_message)
                    db.commit()

                logger.info(f"Agent execution complete. Sending response to client for dialog {dialog_id}.")

                # Robustly serialize the full agent output to a JSON string
                full_output_json = json.dumps(result, cls=CustomEncoder, indent=2)

                await websocket.send_json({
                    "type": "final_response",
                    "content": final_answer,
                    "full_output": full_output_json
                })

            except Exception as e:
                logger.error(f"Agent invocation error: {e}", exc_info=True)
                await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        logger.info(f"WebSocket connection closed for dialog {dialog_id}.")
    except Exception as e:
        logger.error(f"An unexpected error occurred in the WebSocket endpoint: {e}", exc_info=True)

# API Endpoints for Conversation History
from . import database
from sqlalchemy.orm import Session
from fastapi import Depends
from typing import List

# Pydantic models for API
from pydantic import BaseModel
from datetime import datetime

class MessageModel(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}

class DialogModel(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: List[MessageModel] = []

    model_config = {"from_attributes": True}


@app.post("/api/dialogs", response_model=DialogModel)
def create_dialog(db: Session = Depends(database.get_db)):
    """
    Creates a new, empty dialog.
    """
    new_dialog = database.Dialog()
    db.add(new_dialog)
    db.commit()
    db.refresh(new_dialog)
    return new_dialog

@app.get("/api/dialogs", response_model=List[DialogModel])
def get_dialogs(db: Session = Depends(database.get_db)):
    """
    Retrieves all dialogs, ordered by creation date.
    """
    return db.query(database.Dialog).order_by(database.Dialog.created_at.desc()).all()

@app.get("/api/dialogs/{dialog_id}", response_model=DialogModel)
def get_dialog_messages(dialog_id: int, db: Session = Depends(database.get_db)):
    """
    Retrieves all messages for a specific dialog.
    """
    dialog = db.query(database.Dialog).filter(database.Dialog.id == dialog_id).first()
    if not dialog:
        raise HTTPException(status_code=404, detail="Dialog not found")
    return dialog
