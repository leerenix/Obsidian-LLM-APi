document.addEventListener("DOMContentLoaded", () => {
    // --- DOM Element Selections ---
    const dialogsList = document.getElementById("dialogs-list");
    const newDialogBtn = document.getElementById("new-dialog-btn");
    const yoloToggle = document.getElementById("yolo-toggle");
    const chatTitle = document.getElementById("chat-title");
    const chatMessages = document.getElementById("chat-messages");
    const messageForm = document.getElementById("message-form");
    const messageInput = document.getElementById("message-input");
    const rightPanel = document.getElementById("right-panel");
    const closeRightPanelBtn = document.getElementById("close-right-panel-btn");
    const noteContentArea = document.getElementById("note-content-area");

    // --- State Management ---
    let activeDialogId = null;
    let ws = null;

    // --- Core Functions ---

    /**
     * Loads all dialogs from the API and populates the list.
     */
    async function loadDialogs() {
        try {
            const response = await fetch("/api/dialogs");
            if (!response.ok) throw new Error("Failed to fetch dialogs");
            const dialogs = await response.json();

            dialogsList.innerHTML = ""; // Clear existing list
            dialogs.forEach(dialog => {
                const li = document.createElement("li");
                li.textContent = dialog.title || `Conversation ${dialog.id}`;
                li.dataset.dialogId = dialog.id;

                li.addEventListener("click", () => {
                    if (activeDialogId !== dialog.id) {
                        activeDialogId = dialog.id;
                        loadMessages(dialog.id);
                        document.querySelectorAll("#dialogs-list li").forEach(item => item.classList.remove("active"));
                        li.classList.add("active");
                    }
                });
                dialogsList.appendChild(li);
            });

            // --- Auto-load first dialog ---
            if (dialogs.length > 0 && activeDialogId === null) {
                const firstDialog = dialogs[0];
                activeDialogId = firstDialog.id;
                loadMessages(firstDialog.id);
                dialogsList.querySelector(`[data-dialog-id='${firstDialog.id}']`).classList.add("active");
            }
        } catch (error) {
            console.error("Error loading dialogs:", error);
        }
    }

    /**
     * Loads messages for a specific dialog and displays them.
     * @param {number} dialogId
     */
    async function loadMessages(dialogId) {
        if (!dialogId) {
            chatMessages.innerHTML = "";
            chatTitle.textContent = "Select a Conversation";
            return;
        }

        try {
            const response = await fetch(`/api/dialogs/${dialogId}`);
            if (!response.ok) throw new Error("Failed to fetch messages");
            const dialog = await response.json();

            chatTitle.textContent = dialog.title || `Conversation ${dialog.id}`;
            chatMessages.innerHTML = "";
            dialog.messages.forEach(msg => renderMessage(msg.role, msg.content));

            connectWebSocket(); // Establish WS connection after loading messages
        } catch (error) {
            console.error(`Error loading messages for dialog ${dialogId}:`, error);
        }
    }

    /**
     * Establishes a WebSocket connection for the active dialog.
     */
    function connectWebSocket() {
        if (ws) {
            ws.close();
        }
        if (!activeDialogId) return;

        const wsUrl = `ws://${window.location.host}/ws/${activeDialogId}`;
        ws = new WebSocket(wsUrl);

        ws.onopen = () => console.log("WebSocket connection established.");
        ws.onclose = () => console.log("WebSocket connection closed.");
        ws.onerror = (error) => console.error("WebSocket error:", error);

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === 'status') {
                // You could render a temporary status message here if desired
                console.log("Status:", data.message);
            } else if (data.type === 'final_response') {
                renderMessage('assistant', data.content);
                // Check for note content in the full output and display it
                if (data.full_output) {
                    try {
                        const output = JSON.parse(data.full_output);
                        if (output.messages && output.messages.length > 1) {
                            // The tool output is usually the second-to-last message
                            const toolMessage = output.messages.find(m => m.type === 'tool');
                            if (toolMessage && toolMessage.content) {
                                const toolData = JSON.parse(toolMessage.content);
                                // Handle search results
                                if (toolData.results && toolData.results.length > 0) {
                                    const firstResult = toolData.results[0];
                                    displayNoteContent(firstResult.title, firstResult.content);
                                }
                                // Handle direct get_note calls
                                else if (toolData.content) {
                                    displayNoteContent(toolData.title, toolData.content);
                                }
                            }
                        }
                    } catch (e) {
                        console.error("Error parsing tool output from full_output:", e);
                    }
                }
            } else if (data.type === 'error') {
                renderMessage('assistant', `Error: ${data.message}`);
            }
        };
    }

    /**
     * Renders a message in the chat window.
     * @param {string} role - 'user' or 'assistant'
     * @param {string} content
     */
    function renderMessage(role, content) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", role);
        // Basic markdown-to-HTML conversion for links and bolding
        let htmlContent = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        htmlContent = htmlContent.replace(/\[\[(.*?)\]\]/g, '<a href="#" class="note-link" data-note="$1">$1</a>');
        messageDiv.innerHTML = htmlContent;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to bottom
    }

    // --- Event Listeners ---

    /**
     * Handle new dialog creation.
     */
    newDialogBtn.addEventListener("click", async () => {
        try {
            const response = await fetch("/api/dialogs", { method: "POST" });
            if (!response.ok) throw new Error("Failed to create new dialog");
            const newDialog = await response.json();
            activeDialogId = newDialog.id;
            loadDialogs(); // Reload the list to show the new one
            loadMessages(newDialog.id); // Load the (empty) new dialog
        } catch (error) {
            console.error("Error creating new dialog:", error);
        }
    });

    /**
     * Handle form submission to send a message.
     */
    messageForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const message = messageInput.value.trim();
        if (message && activeDialogId && ws && ws.readyState === WebSocket.OPEN) {
            renderMessage('user', message);
            ws.send(message);
            messageInput.value = "";
        } else {
            console.error("Cannot send message: No active dialog, or WebSocket is not connected.");
        }
    });

    /**
     * Displays note content in the right-side panel.
     * @param {string} title
     * @param {string} content
     */
    function displayNoteContent(title, content) {
        noteContentArea.innerHTML = `<h3>${title}</h3><pre>${content}</pre>`;
        rightPanel.classList.remove("hidden");
    }

    // --- Event Delegation for Note Links ---
    chatMessages.addEventListener("click", async (e) => {
        if (e.target.classList.contains("note-link")) {
            e.preventDefault();
            const notePath = e.target.dataset.note + ".md";
            try {
                const response = await fetch(`/api/note/by-path?path=${encodeURIComponent(notePath)}`);
                if (!response.ok) throw new Error(`Note not found: ${notePath}`);
                const note = await response.json();
                displayNoteContent(note.title, note.content);
            } catch (error) {
                console.error("Error fetching note by path:", error);
                displayNoteContent("Error", `Could not load note: ${notePath}`);
            }
        }
    });

    /**
     * Handle closing the right-side panel.
     */
    closeRightPanelBtn.addEventListener("click", () => {
        rightPanel.classList.add("hidden");
    });


    // --- Initializer ---

    /**
     * Initializes the application.
     */
    function init() {
        console.log("Application initialized.");
        loadDialogs();
        rightPanel.classList.add("hidden"); // Start with the panel hidden
    }

    init();
});
