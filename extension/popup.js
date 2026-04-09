const API_BASE = "http://localhost:8000";
const chatContainer = document.getElementById("chat-container");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const indexBtn = document.getElementById("index-btn");
const statusBadge = document.getElementById("backend-status");

// Check backend status on load
async function checkStatus() {
  try {
    const response = await fetch(`${API_BASE}/`);
    if (response.ok) {
      statusBadge.textContent = "Backend: Online";
      statusBadge.style.color = "#10b981"; // Emerald 500
    }
  } catch (error) {
    statusBadge.textContent = "Backend: Offline";
    statusBadge.style.color = "#ef4444"; // Red 500
  }
}

checkStatus();

function addMessage(text, role) {
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${role}`;
  msgDiv.textContent = text;
  chatContainer.appendChild(msgDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
  return msgDiv;
}

function addLoadingDots() {
  const loadingDiv = document.createElement("div");
  loadingDiv.className = "message assistant";
  loadingDiv.innerHTML = '<div class="loading-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';
  chatContainer.appendChild(loadingDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
  return loadingDiv;
}

indexBtn.addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  addMessage("Indexing page contents...", "system");
  indexBtn.disabled = true;
  indexBtn.textContent = "Indexing...";

  try {
    // 1. Get text from content script
    const response = await chrome.tabs.sendMessage(tab.id, { action: "extractText" });
    
    if (!response || !response.text) {
      throw new Error("Could not extract page text.");
    }

    // 2. Send to backend
    const backendRes = await fetch(`${API_BASE}/ingest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: response.text,
        url: response.url
      })
    });

    if (backendRes.ok) {
      const data = await backendRes.json();
      addMessage(`Page indexed successfully! (${data.chunks_ingested} chunks)`, "system");
    } else {
      throw new Error("Backend failed to ingest text.");
    }
  } catch (error) {
    addMessage(`Error: ${error.message}`, "system");
  } finally {
    indexBtn.disabled = false;
    indexBtn.textContent = "Index Page";
  }
});

async function handleSendMessage() {
  const query = userInput.value.trim();
  if (!query) return;

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const url = tab.url;

  addMessage(query, "user");
  userInput.value = "";
  
  const loadingMsg = addLoadingDots();

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, url })
    });

    if (response.ok) {
      const data = await response.json();
      loadingMsg.remove();
      addMessage(data.answer, "assistant");
    } else {
      throw new Error("Failed to get response from assistant.");
    }
  } catch (error) {
    loadingMsg.remove();
    addMessage(`Error: ${error.message}`, "system");
  }
}

sendBtn.addEventListener("click", handleSendMessage);
userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") handleSendMessage();
});
