const byId = (id)=>document.getElementById(id);
const auth = byId('auth');
const chat = byId('chat');
const statusEl = byId('status');
const messages = byId('messages');
const loginBtn = byId('loginBtn');
const sendBtn = byId('sendBtn');
const username = byId('username');
const password = byId('password');
const msgInput = byId('msg');

let token = null;
let ws = null;
let reconnectTimer = null;

function setStatus(s){ statusEl.textContent = s; }

function escapeHTML(s){
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

loginBtn.addEventListener('click', async ()=>{
  loginBtn.disabled = true;
  try{
    const res = await fetch('/auth/login', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({username: username.value.trim(), password: password.value})
    });
    if(!res.ok){ alert('Невірні дані входу'); return; }
    const data = await res.json();
    token = data.access_token;
    auth.classList.add('hidden'); chat.classList.remove('hidden');
    connect();
  }finally{
    loginBtn.disabled = false;
  }
});

function connect(){
  if(!token) return;
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws?token=${encodeURIComponent(token)}`);
  setStatus('connecting…');
  ws.onopen = ()=> setStatus('online');
  ws.onclose = ()=>{
    setStatus('offline');
    if(!reconnectTimer){
      reconnectTimer = setTimeout(()=>{ reconnectTimer=null; connect(); }, 1200);
    }
  };
  ws.onmessage = (e)=>{
    let data; try{ data = JSON.parse(e.data); }catch{return;}
    if(data.type === 'chat'){
      addMsg(data.from, data.message, data.me);
    }else if(data.type === 'error'){
      addMsg('system', data.message, false);
    }
  };
}

function addMsg(from, text, me){
  const el = document.createElement('div');
  el.className = 'msg ' + (me ? 'me':'other');
  const meta = document.createElement('div');
  meta.className = 'meta';
  const time = new Date().toLocaleTimeString();
  meta.innerHTML = escapeHTML(`${from} • ${time}`);
  const body = document.createElement('div');
  body.innerHTML = escapeHTML(text);
  el.appendChild(meta); el.appendChild(body);
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
}

sendBtn.addEventListener('click', send);
msgInput.addEventListener('keydown', (e)=>{
  if(e.key === 'Enter'){ e.preventDefault(); send(); }
});

function send(){
  const v = msgInput.value.trim();
  if(!v || !ws || ws.readyState !== WebSocket.OPEN) return;
  ws.send(JSON.stringify({message: v}));
  addMsg('me', v, true);
  msgInput.value = '';
}
