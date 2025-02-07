let socket;
let username;
let activeUsers = [];
let selectedUser = null; // For private chat

function signIn() {
    username = document.getElementById("usernameInput").value.trim();
    if (!username) return alert("Please enter your name.");

    document.getElementById("loginContainer").classList.add("hidden");
    document.getElementById("usersContainer").classList.remove("hidden");

    socket = new WebSocket("wss://simplechat-3.onrender.com");

    socket.onopen = () => {
        socket.send(JSON.stringify({ type: "join", name: username }));
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
  
      if (data.type === "message") {
          displayMessage(data.name, data.message);
      } 
      else if (data.type === "private_message") {
          // Only display the message if it's from or for the selected user
          if (data.receiver === username && data.name === selectedUser) {
              displayPrivateMessage(data.name, data.message);
          }
      } 
      else if (data.type === "active_users") {
          updateActiveUsers(data.users);
      }
  }
  
}

// Show Active Users
function updateActiveUsers(users) {
    activeUsers = users.filter(user => user !== username);
    const userList = document.getElementById("activeUsersList");
    userList.innerHTML = "";

    activeUsers.forEach(user => {
        const li = document.createElement("li");
        li.textContent = user;
        li.onclick = () => startPrivateChat(user);
        userList.appendChild(li);
    });
}

// Open Group Chat
function openGroupChat() {
    document.getElementById("usersContainer").classList.add("hidden");
    document.getElementById("chatContainer").classList.remove("hidden");
    document.getElementById("displayName").textContent = username;
}

// Send Public Message
function sendMessage() {
    const input = document.getElementById("messageInput");
    if (!input.value.trim()) return;

    socket.send(JSON.stringify({ type: "message", name: username, message: input.value }));
    //displayMessage(username, input.value);

    input.value = "";
}

// Display Public Messages
function displayMessage(name, message) {
    const chatBox = document.getElementById("chatBox");
    const div = document.createElement("div");
    div.className = "message " + (name === username ? "user-message" : "other-message");
    div.textContent = `${name}: ${message}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Start Private Chat
function startPrivateChat(user) {
    selectedUser = user;
    document.getElementById("usersContainer").classList.add("hidden");
    document.getElementById("privateChatContainer").classList.remove("hidden");
    document.getElementById("privateChatUser").textContent = user;
}

// Send Private Message
function sendPrivateMessage() {
  const input = document.getElementById("privateMessageInput");
  if (!input.value.trim() || !selectedUser) return;

  const messageData = {
      type: "private_message",
      name: username,  // Sender
      message: input.value,
      receiver: selectedUser  // Receiver
  };

  socket.send(JSON.stringify(messageData));

  // Display message locally for the sender
  displayPrivateMessage(username, input.value, true);

  input.value = "";
}

// Display Private Messages
function displayPrivateMessage(name, message, self = false) {
    const chatBox = document.getElementById("privateChatBox");
    const div = document.createElement("div");
    div.className = "message " + (self ? "user-message" : "other-message");
    div.textContent = `${name}: ${message}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Back to Active Users List
function backToUsers() {
    document.getElementById("privateChatContainer").classList.add("hidden");
    document.getElementById("usersContainer").classList.remove("hidden");
}
function backFromGroupChat() {
  document.getElementById("chatContainer").classList.add("hidden");
  document.getElementById("usersContainer").classList.remove("hidden");
}
