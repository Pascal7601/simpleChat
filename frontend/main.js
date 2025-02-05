let ws;
let username = "";
const chatBox = document.getElementById("chatBox");
const messageInput = document.getElementById("messageInput");
const loginContainer = document.getElementById("loginContainer");
const chatContainer = document.getElementById("chatContainer");
const displayName = document.getElementById("displayName");

// Sign in function
function signIn() {
  username = document.getElementById("usernameInput").value.trim();
  if (!username) {
    alert("Please enter your name!");
    return;
  }

  // Show chat container & hide login form
  loginContainer.classList.add("hidden");
  chatContainer.classList.remove("hidden");
  displayName.textContent = username;

  // Connect to WebSocket
  ws = new WebSocket("ws://localhost:9090");

  ws.onopen = () => {
    console.log("Connected to WebSocket server.");
    ws.send(JSON.stringify({ type: "join", name: username }));
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    displayMessage(data.name, data.message, data.name === username);
  };

  ws.onclose = () => {
    console.log("Disconnected from WebSocket server.");
  };
}

// Send message function
function sendMessage() {
  const message = messageInput.value.trim();
  if (message && ws) {
    ws.send(JSON.stringify({ type: "message", name: username, message }));
    messageInput.value = ""; // Clear input field
  }
}

// Display messages with different colors
function displayMessage(sender, message, isUser) {
  const msgElement = document.createElement("div");
  msgElement.classList.add("message");
  msgElement.classList.add(isUser ? "user-message" : "other-message");
  msgElement.textContent = `${sender}: ${message}`;
  chatBox.appendChild(msgElement);
  chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
}
