const DEFAULT_API = "http://localhost:8000";
const API = (() => {
  const params = new URLSearchParams(window.location.search);
  const override = params.get("api");
  return override ? override.replace(/\/$/, "") : DEFAULT_API;
})();

let socket = null;
let gameState = null;
let playerId = null;
let isHost = false;
let pendingQuestion = null;
let lastRoll = null;
let activeGameId = null;
const $ = id => document.getElementById(id);

function resetUiState() {
  const overlay = $("game-over-overlay");
  const restart = $("restart-btn");
  const indicator = $("roll-indicator");
  if (overlay) {
    overlay.classList.add("hidden");
    overlay.classList.remove("visible");
    overlay.hidden = false;
  }
  if (restart) {
    restart.classList.add("hidden");
    restart.hidden = false;
  }
  if (indicator) indicator.hidden = true;
  if ($("winner-text")) $("winner-text").textContent = "";
}

async function request(path, options) {
  const response = await fetch(`${API}${path}`, options);
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail || "Request failed");
  return body;
}

async function createGame() {
  try {
    const username = $("username").value.trim();
    if (username === "") {
      alert("Es necesario poner un nombre");
      return;
    }

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
    if (username === "") {
      alert("Es necesario poner un nombre");
      return;
    }
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
  activeGameId = gameId;
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.onmessage = null;
    socket.onclose = null;
    socket.close();
  }

  gameState = null;
  pendingQuestion = null;
  lastRoll = null;
  resetUiState();

  const apiUrl = new URL(API);
  const wsProtocol = apiUrl.protocol === "https:" ? "wss:" : "ws:";
  const wsBase = `${wsProtocol}//${apiUrl.host}`;
  socket = new WebSocket(`${wsBase}/ws/games/${gameId}/${playerId}`);
  socket.onopen = () => { $("lobby").hidden=true; $("game").hidden=false; $("game-label").textContent=`Game: ${gameId}`; };
  socket.onmessage = e => {
    const message = JSON.parse(e.data);
    if (message.type === "game_state" && message.data && message.data.id && message.data.id !== activeGameId) {
      return;
    }
    handleMessage(message);
  };
  socket.onclose = () => setLobbyStatus("Disconnected from server.");
}

function send(type, data={}) {
  if (socket?.readyState === WebSocket.OPEN) socket.send(JSON.stringify({type,...data}));
}

function handleMessage(message) {
  if (message.type === "game_state") {
    gameState = message.data;
    const me = gameState.players.find(p => p.id === playerId);
    pendingQuestion = me && me.pending_question ? me.pending_question : null;
    render();
    return;
  }
  if (message.type === "dice_rolled") {
    lastRoll = Number(message.data.value);
    showRoll(lastRoll);
    return;
  }
  if (message.type === "game_started") { render(); return; }
  if (message.type === "chat_message") { appendChat(message.data); return; }
  if (message.type === "question_queued") {
    if (message.data.player_id !== playerId) return;
    pendingQuestion = message.data.question;
    renderQuestion();
    return;
  }
  if (message.type === "question_answered") {
    if (message.data.player_id !== playerId) return;
    pendingQuestion = null;
    renderQuestion();
    render();
    return;
  }
  if (message.type === "error") { alert(message.data.message); return; }
  if (message.type === "game_won") {
    const winner = gameState?.players.find(p => p.id === message.data.player_id);
    renderWinner(winner ? winner.username : "Someone");
    return;
  }
  if (message.type === "game_restarted") {
    renderWinner(null);
    return;
  }
}

function render() {
  if (!gameState) return;
  const canRoll = gameState.state === "playing" && gameState.current_player_id === playerId;
  $("start-btn").hidden = !isHost || gameState.state !== "idle";
  $("restart-btn").hidden = !isHost || gameState.state !== "finished";
  $("roll-btn").disabled = !canRoll || !!pendingQuestion || gameState.state !== "playing";
  if (lastRoll !== null) showRoll(lastRoll, false);

  const winnerName = gameState.state === "finished" && gameState.winner_id
    ? gameState.players.find(p => p.id === gameState.winner_id)?.username || "Someone"
    : null;
  renderWinner(winnerName);

  renderPlayers(); renderBoard(); renderChat(); renderQuestion();
}

function renderWinner(username) {
  const overlay = $("game-over-overlay");
  const label = $("winner-text");
  const restart = $("restart-btn");

  if (!gameState || gameState.state !== "finished" || !gameState.winner_id || !username) {
    if (overlay) {
      overlay.classList.add("hidden");
      overlay.classList.remove("visible");
      overlay.hidden = false;
    }
    if (restart) {
      restart.classList.add("hidden");
      restart.hidden = false;
    }
    if (label) label.textContent = "";
    return;
  }

  label.textContent = `${username} won the game!`;
  overlay.classList.remove("hidden");
  overlay.classList.add("visible");
  overlay.hidden = false;
  restart.classList.toggle("hidden", !isHost);
  restart.hidden = false;
}

function showRoll(value, animate = true) {
  const indicator = $("roll-indicator");
  if (!indicator) return;
  indicator.hidden = false;
  indicator.textContent = `🎲 Roll: ${value}`;
  if (animate) {
    indicator.classList.remove("flash");
    void indicator.offsetWidth;
    indicator.classList.add("flash");
  }
}

const COLORS = ["#e5533d","#2f7de1","#8b5cf6","#d6408f","#1c8c74","#c47a12","#0f8fb5","#6b7280"];
const colorOf = id => COLORS[Math.max(0, gameState.players.findIndex(p => p.id === id)) % COLORS.length];

function renderPlayers() {
  $("players").innerHTML = gameState.players.map(p =>
    `<div class="player-card${p.id===gameState.current_player_id ? " current" : ""}" style="--c:${colorOf(p.id)}"><span class="dot"></span>${escapeHtml(p.username)} <small>casilla ${p.position}</small> ${p.id===gameState.current_player_id ? "🎯" : ""}</div>`
  ).join("");
}

function renderBoard() {
  const size = gameState.settings.board_size, cols = 10, rows = Math.ceil(size / cols);
  const cells = [];
  for (let r = rows - 1; r >= 0; r--) {
    const nums = [];
    for (let c = 0; c < cols; c++) { const n = r * cols + c + 1; if (n <= size) nums.push(n); }
    if (r % 2 === 1) nums.reverse();
    nums.forEach(i => {
      const tokens = gameState.players.filter(p => p.position === i)
        .map(p => `<span class="player-token" style="--c:${colorOf(p.id)}">${escapeHtml(p.username)}</span>`).join("");
      const s = gameState.board.snakes[i], l = gameState.board.ladders[i];
      const jump = s ? `<span class="jump">🐍→${s}</span>` : l ? `<span class="jump">🪜→${l}</span>` : "";
      const cls = ["cell", (r + i) % 2 ? "alt" : "", s ? "snake" : "", l ? "ladder" : "", i === size ? "goal" : ""].join(" ");
      cells.push(`<div class="${cls}"><strong>${i}</strong>${jump}<div>${tokens}</div></div>`);
    });
  }
  $("board").innerHTML = cells.join("");
}

function renderChat() {
  $("chat-messages").innerHTML=gameState.chat.map(appendChatMarkup).join("");
}
function renderQuestion() {
  const panel = $("question-panel");
  const text = $("question-text");
  const list = $("question-options");
  if (!pendingQuestion) { panel.hidden = true; return; }
  text.textContent = pendingQuestion.question;
  list.innerHTML = pendingQuestion.options.map((option, index) =>
    `<button type="button" data-index="${index}">${escapeHtml(option.text)}</button>`
  ).join("");
  list.querySelectorAll("button").forEach(button => {
    button.onclick = () => send("answer_question", { option_index: Number(button.dataset.index) });
  });
  panel.hidden = false;
}
function appendChat(data) {
  $("chat-messages").insertAdjacentHTML("beforeend",appendChatMarkup(data));
  $("chat-messages").scrollTop=$("chat-messages").scrollHeight;
}
function appendChatMarkup(data) { return `<div><strong>${escapeHtml(data.username)}:</strong> ${escapeHtml(data.message)}</div>`; }
function setLobbyStatus(text) { $("lobby-status").textContent=text; }
function escapeHtml(value) { const d=document.createElement("div"); d.textContent=value; return d.innerHTML; }
function sendChat() { const input=$("chat-input"); const message=input.value.trim(); if(message){send("chat",{message});input.value="";} }

resetUiState();
$("host-btn").onclick=createGame;
$("join-btn").onclick=joinGame;
$("start-btn").onclick=()=>send("start_game");
$("restart-btn").onclick=()=>send("restart_game");
$("roll-btn").onclick=()=>send("roll_dice");
$("chat-send").onclick=sendChat;
$("chat-input").addEventListener("keydown",e=>{if(e.key==="Enter")sendChat();});