const API = "http://localhost:8000";
let socket = null;
let gameState = null;
let playerId = null;
let isHost = false;
const $ = id => document.getElementById(id);

async function request(path, options) {
  const response = await fetch(`${API}${path}`, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || "Request failed");
  return body;
}

async function createGame() {
  try {
    const username = $("username").value.trim();
    const game = await request("/api/games", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({username})
    });
    playerId = game.host_id;
    isHost = true;
    connect(game.id);
  } catch (error) { setLobbyStatus(error.message); }
}

async function joinGame() {
  try {
    const username = $("username").value.trim();
    const gameId = $("game-id").value.trim().toUpperCase();
    const game = await request(`/api/games/${gameId}/join`, {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({username})
    });
    playerId = game.players.find(p => p.username === username).id;
    connect(game.id);
  } catch (error) { setLobbyStatus(error.message); }
}

function connect(gameId) {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  const host = location.hostname ? `${protocol}://${location.hostname}:8000` : "ws://localhost:8000";
  socket = new WebSocket(`${host}/ws/games/${gameId}/${playerId}`);
  socket.onopen = () => { $("lobby").hidden=true; $("game").hidden=false; $("game-label").textContent=`Game: ${gameId}`; };
  socket.onmessage = e => handleMessage(JSON.parse(e.data));
  socket.onclose = () => setLobbyStatus("Disconnected from server.");
}

function send(type, data={}) {
  if (socket?.readyState === WebSocket.OPEN) socket.send(JSON.stringify({type,...data}));
}

function handleMessage(message) {
  if (message.type === "game_state") { gameState=message.data; render(); return; }
  if (message.type === "game_started") { render(); return; }
  if (message.type === "chat_message") { appendChat(message.data); return; }
  if (message.type === "error") { alert(message.data.message); return; }
  if (message.type === "game_won") { alert("🏆 We have a grammar champion!"); }
}

function render() {
  if (!gameState) return;
  $("start-btn").hidden = !isHost || gameState.state !== "idle";
  $("roll-btn").disabled = gameState.state !== "playing" || gameState.current_player_id !== playerId;
  renderPlayers(); renderBoard(); renderChat();
}

function renderPlayers() {
  $("players").innerHTML = gameState.players.map(p =>
    `<div class="player-card">${escapeHtml(p.username)} — ${p.position} ${p.id===gameState.current_player_id ? "🎯" : ""}</div>`
  ).join("");
}

function renderBoard() {
  const cells=[];
  for (let i=1;i<=gameState.settings.board_size;i++) {
    const tokens=gameState.players.filter(p=>p.position===i).map(p=>`<span class="player-token">${escapeHtml(p.username)}</span>`).join("");
    const snake=gameState.board.snakes[i] ? ` 🐍→${gameState.board.snakes[i]}` : "";
    const ladder=gameState.board.ladders[i] ? ` 🪜→${gameState.board.ladders[i]}` : "";
    cells.push(`<div class="cell"><strong>${i}</strong>${snake}${ladder}<br>${tokens}</div>`);
  }
  $("board").innerHTML=cells.join("");
}

function renderChat() {
  $("chat-messages").innerHTML=gameState.chat.map(appendChatMarkup).join("");
}
function appendChat(data) {
  $("chat-messages").insertAdjacentHTML("beforeend",appendChatMarkup(data));
  $("chat-messages").scrollTop=$("chat-messages").scrollHeight;
}
function appendChatMarkup(data) { return `<div><strong>${escapeHtml(data.username)}:</strong> ${escapeHtml(data.message)}</div>`; }
function setLobbyStatus(text) { $("lobby-status").textContent=text; }
function escapeHtml(value) { const d=document.createElement("div"); d.textContent=value; return d.innerHTML; }
function sendChat() { const input=$("chat-input"); const message=input.value.trim(); if(message){send("chat",{message});input.value="";} }

$("host-btn").onclick=createGame;
$("join-btn").onclick=joinGame;
$("start-btn").onclick=()=>send("start_game");
$("roll-btn").onclick=()=>send("roll_dice");
$("chat-send").onclick=sendChat;
$("chat-input").addEventListener("keydown",e=>{if(e.key==="Enter")sendChat();});
