// saved login token
let token = localStorage.getItem("token");
if (!token) {
  token = "";
}

let selectedTicketId = null;
let ws = null;

// small popup message
function showMessage(text, isError) {
  var box = document.createElement("div");
  if (isError) {
    box.className = "toast toast-error";
  } else {
    box.className = "toast toast-success";
  }
  box.textContent = text;
  document.body.appendChild(box);
  setTimeout(function () {
    box.remove();
  }, 3000);
}

// write API result in log box
function writeLog(text, cssClass) {
  var logBox = document.getElementById("api-log");
  var line = document.createElement("div");
  if (cssClass) {
    line.className = cssClass;
  }
  var time = new Date().toLocaleTimeString();
  line.textContent = "[" + time + "] " + text;
  logBox.prepend(line);
}

// common fetch setup
function makeHeaders() {
  var headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = "Bearer " + token;
  }
  return headers;
}

function getErrorMessage(data, response) {
  if (data && data.detail) {
    if (typeof data.detail === "string") {
      return data.detail;
    }
    return JSON.stringify(data.detail);
  }
  return response.statusText;
}

// --- Auth ---

async function signup() {
  var email = document.getElementById("signup-email").value;
  var password = document.getElementById("signup-password").value;
  var role = document.getElementById("signup-role").value;

  var response = await fetch("/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email, password: password, role: role }),
  });

  var data = await response.json();
  writeLog("POST /auth/signup -> " + response.status, response.ok ? "ok" : "err");

  if (!response.ok) {
    showMessage(getErrorMessage(data, response), true);
    return;
  }

  showMessage("Account created. Please sign in.", false);
}

async function login() {
  var email = document.getElementById("login-email").value;
  var password = document.getElementById("login-password").value;

  var response = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email, password: password }),
  });

  var data = await response.json();
  writeLog("POST /auth/login -> " + response.status, response.ok ? "ok" : "err");

  if (!response.ok) {
    showMessage(getErrorMessage(data, response), true);
    return;
  }

  token = data.access_token;
  localStorage.setItem("token", token);
  showMessage("Signed in successfully", false);
  loadUserInfo();
  loadTickets();
}

function logout() {
  token = "";
  localStorage.removeItem("token");
  document.getElementById("user-info").textContent = "Please sign in to continue";
  document.getElementById("ticket-list").innerHTML = "";
  document.getElementById("user-badge").textContent = "Not signed in";
  document.getElementById("user-badge").className = "badge badge-offline";
  document.getElementById("agent-card").classList.add("dimmed");
  disconnectWs();
  showMessage("Signed out successfully", false);
}

async function loadUserInfo() {
  if (!token) {
    return;
  }

  var response = await fetch("/auth/me", {
    headers: makeHeaders(),
  });

  var user = await response.json();
  writeLog("GET /auth/me -> " + response.status, response.ok ? "ok" : "err");

  if (!response.ok) {
    logout();
    return;
  }

  var info = document.getElementById("user-info");
  var roleClass = "badge-user";
  if (user.role === "agent") {
    roleClass = "badge-agent";
    document.getElementById("agent-card").classList.remove("dimmed");
  } else {
    document.getElementById("agent-card").classList.add("dimmed");
  }

  info.innerHTML =
    "<strong>" +
    user.email +
    "</strong><br>Role: <span class=\"badge " +
    roleClass +
    "\">" +
    user.role +
    "</span>";

  document.getElementById("user-badge").textContent = user.email;
  document.getElementById("user-badge").className = "badge badge-user";
}

// --- Tickets ---

async function createTicket() {
  var title = document.getElementById("ticket-title").value;
  var description = document.getElementById("ticket-desc").value;

  var response = await fetch("/tickets", {
    method: "POST",
    headers: makeHeaders(),
    body: JSON.stringify({ title: title, description: description }),
  });

  var data = await response.json();
  writeLog("POST /tickets -> " + response.status, response.ok ? "ok" : "err");

  if (!response.ok) {
    showMessage(getErrorMessage(data, response), true);
    return;
  }

  showMessage("Ticket #" + data.id + " created", false);
  document.getElementById("ticket-title").value = "";
  document.getElementById("ticket-desc").value = "";
  loadTickets();
}

async function loadTickets() {
  if (!token) {
    showMessage("Please sign in first", true);
    return;
  }

  var response = await fetch("/tickets", {
    headers: makeHeaders(),
  });

  var tickets = await response.json();
  writeLog("GET /tickets -> " + response.status, response.ok ? "ok" : "err");

  if (!response.ok) {
    showMessage(getErrorMessage(tickets, response), true);
    return;
  }

  showTicketList(tickets);
}

function showTicketList(tickets) {
  var list = document.getElementById("ticket-list");
  list.innerHTML = "";

  if (tickets.length === 0) {
    list.innerHTML = '<p class="empty-msg">No tickets found</p>';
    return;
  }

  for (var i = 0; i < tickets.length; i++) {
    var ticket = tickets[i];
    var item = document.createElement("div");
    item.className = "ticket-item";
    if (ticket.id === selectedTicketId) {
      item.className = "ticket-item active";
    }
    item.dataset.id = ticket.id;

    var shortDesc = ticket.description;
    if (shortDesc.length > 60) {
      shortDesc = shortDesc.slice(0, 60) + "...";
    }

    item.innerHTML =
      "<h3>#" +
      ticket.id +
      " - " +
      ticket.title +
      "</h3><p>" +
      shortDesc +
      '</p><span class="status status-' +
      ticket.status +
      '">' +
      ticket.status +
      "</span>";

    item.onclick = function () {
      selectedTicketId = Number(this.dataset.id);
      document.getElementById("agent-ticket-id").value = selectedTicketId;
      document.getElementById("ws-ticket-id").value = selectedTicketId;
      showTicketList(tickets);
      showMessage("Ticket #" + selectedTicketId + " selected", false);
    };

    list.appendChild(item);
  }
}

// --- Agent ---

async function agentReply() {
  var ticketId = document.getElementById("agent-ticket-id").value;
  var message = document.getElementById("agent-reply").value;

  var response = await fetch("/tickets/" + ticketId + "/replies", {
    method: "POST",
    headers: makeHeaders(),
    body: JSON.stringify({ message: message }),
  });

  var data = await response.json();
  writeLog("POST /tickets/" + ticketId + "/replies -> " + response.status, response.ok ? "ok" : "err");

  if (!response.ok) {
    showMessage(getErrorMessage(data, response), true);
    return;
  }

  showMessage("Reply sent successfully", false);
  document.getElementById("agent-reply").value = "";
}

async function agentStatus() {
  var ticketId = document.getElementById("agent-ticket-id").value;
  var status = document.getElementById("agent-status").value;

  var response = await fetch("/tickets/" + ticketId + "/status", {
    method: "PATCH",
    headers: makeHeaders(),
    body: JSON.stringify({ status: status }),
  });

  var data = await response.json();
  writeLog("PATCH /tickets/" + ticketId + "/status -> " + response.status, response.ok ? "ok" : "err");

  if (!response.ok) {
    showMessage(getErrorMessage(data, response), true);
    return;
  }

  showMessage("Status updated successfully", false);
  loadTickets();
}

// --- WebSocket ---

function connectWs() {
  var ticketId = document.getElementById("ws-ticket-id").value;
  if (!ticketId) {
    showMessage("Please enter a ticket ID", true);
    return;
  }

  disconnectWs();

  var protocol = "ws:";
  if (location.protocol === "https:") {
    protocol = "wss:";
  }

  var url = protocol + "//" + location.host + "/ws/tickets/" + ticketId;
  ws = new WebSocket(url);

  ws.onopen = function () {
    document.getElementById("ws-status").textContent = "Connected";
    document.getElementById("ws-status").className = "badge badge-agent";
    writeLog("WebSocket connected for ticket #" + ticketId, "ok");
    ws.send("ping");
  };

  ws.onmessage = function (event) {
    var wsLog = document.getElementById("ws-log");
    var line = document.createElement("div");
    var time = new Date().toLocaleTimeString();
    line.textContent = "[" + time + "] " + event.data;
    wsLog.prepend(line);
  };

  ws.onclose = function () {
    document.getElementById("ws-status").textContent = "Disconnected";
    document.getElementById("ws-status").className = "badge badge-offline";
  };
}

function disconnectWs() {
  if (ws) {
    ws.close();
    ws = null;
  }
}

// --- Button clicks ---

document.getElementById("btn-signup").onclick = signup;
document.getElementById("btn-login").onclick = login;
document.getElementById("btn-logout").onclick = logout;
document.getElementById("btn-create-ticket").onclick = createTicket;
document.getElementById("btn-load-tickets").onclick = loadTickets;
document.getElementById("btn-agent-reply").onclick = agentReply;
document.getElementById("btn-agent-status").onclick = agentStatus;
document.getElementById("btn-ws-connect").onclick = connectWs;
document.getElementById("btn-ws-disconnect").onclick = disconnectWs;
document.getElementById("btn-clear-log").onclick = function () {
  document.getElementById("api-log").innerHTML = "";
};

// page load
if (token) {
  loadUserInfo();
} else {
  document.getElementById("agent-card").classList.add("dimmed");
}
