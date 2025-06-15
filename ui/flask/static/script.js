document.addEventListener('DOMContentLoaded', function() {
    // Existing element selectors
    const snapshotListUL = document.getElementById('snapshot-list');
    const chatWindow = document.getElementById('chat-window');
    const currentChatNameDisplay = document.getElementById('current-chat-name');
    const messageInput = document.getElementById('message-input');
    const sendButton = document.getElementById('send-button');
    const newChatButton = document.getElementById('new-chat-button');
    const saveChatButton = document.getElementById('save-chat-button');
    const animationHeaderTitle = document.getElementById('animation-header-title');
    const animationContent = document.getElementById('animation-content');
    const storeAnimationCheckbox = document.getElementById('store-animation-checkbox');
    const renderButton = document.getElementById('render-button');
    const stopButton = document.getElementById('stop-button');

    // New selectors for advanced action buttons
    const restartLatestButton = document.getElementById('restart-latest-button');
    const reduceTokensButton = document.getElementById('reduce-tokens-button');

    let currentChatSessionId = null;

    // --- Event Listeners for existing buttons (condensed for brevity) ---
    if (newChatButton) { newChatButton.addEventListener('click', () => { window.location.href = '/new_chat_form'; }); }
    if (snapshotListUL) { snapshotListUL.addEventListener('click', (e) => { if (e.target.tagName === 'A') { e.preventDefault(); const name = e.target.dataset.snapshotName; if (name && name !== currentChatSessionId) loadChat(name); }}); }
    if (saveChatButton) { saveChatButton.addEventListener('click', () => { /* ... save chat logic ... */
        if (!currentChatSessionId) { alert("No active chat."); return; }
        const newName = prompt("Save as:", currentChatSessionId);
        if (newName && newName.trim()) {
            const nameToSave = newName.trim();
            if (!/^[a-zA-Z0-9_-]+$/.test(nameToSave) || (nameToSave[0] >= '0' && nameToSave[0] <= '9' && !nameToSave.startsWith("chat_")) || nameToSave.length > 50) { alert("Invalid name."); return; }
            saveChatButton.disabled = true; saveChatButton.textContent = 'Saving...';
            fetch(`/save_snapshot/${currentChatSessionId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ new_snapshot_name: nameToSave })})
            .then(r => r.json()).then(d => { alert(d.error||d.message); if (!d.error && (d.was_renamed || currentChatSessionId !== d.saved_snapshot_name)) { currentChatSessionId = d.saved_snapshot_name; if(currentChatNameDisplay)currentChatNameDisplay.textContent=currentChatSessionId; fetchSnapshotsAndUpdateList(currentChatSessionId); } else if(!d.error){ highlightSnapshotInList(currentChatSessionId);}})
            .catch(e => { console.error(e); alert('Error saving.'); }).finally(() => { saveChatButton.disabled=false; saveChatButton.textContent='Save Chat';});
        }
    }); }
    if (renderButton) { renderButton.addEventListener('click', () => { /* ... render logic ... */
        if(!currentChatSessionId){alert("No active chat."); return;} const store=storeAnimationCheckbox?storeAnimationCheckbox.checked:false;
        renderButton.disabled=true; renderButton.textContent="Rendering..."; stopButton.disabled=true;
        fetch(`/action/render/${currentChatSessionId}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({store_animation:store})})
        .then(r=>r.json()).then(d=>{if(d.error)appendMessageToChatWindow({sender:"System",text:`Render Error: ${d.error}`,type:"system-error"}); else {appendMessageToChatWindow({sender:"System",text:d.message,type:"system-info"}); if(d.refresh_animation)updateAnimationDisplay(currentChatSessionId);}})
        .catch(e=>{console.error(e);appendMessageToChatWindow({sender:"System",text:"Render failed.",type:"system-error"});}).finally(()=>{renderButton.disabled=false;renderButton.textContent="Render";stopButton.disabled=false;});
    }); }
    if (stopButton) { stopButton.addEventListener('click', () => { /* ... stop logic ... */
        if(!currentChatSessionId){alert("No active chat."); return;}
        stopButton.disabled=true; stopButton.textContent="Stopping..."; renderButton.disabled=true;
        fetch(`/action/stop/${currentChatSessionId}`,{method:'POST',headers:{'Content-Type':'application/json'}})
        .then(r=>r.json()).then(d=>{if(d.error)appendMessageToChatWindow({sender:"System",text:`Stop Error: ${d.error}`,type:"system-error"}); else {appendMessageToChatWindow({sender:"System",text:d.message,type:"system-info"}); if(d.refresh_animation)updateAnimationDisplay(currentChatSessionId);}})
        .catch(e=>{console.error(e);appendMessageToChatWindow({sender:"System",text:"Stop failed.",type:"system-error"});}).finally(()=>{stopButton.disabled=false;stopButton.textContent="Stop";renderButton.disabled=false;});
    }); }

    // --- Event Listeners for New Advanced Action Buttons ---
    if (restartLatestButton) {
        restartLatestButton.addEventListener('click', function() {
            if (!currentChatSessionId) { alert("No active chat session to restart from."); return; }
            if (!confirm("Are you sure you want to restart with the latest animation sequence? This will create a new chat session.")) return;

            restartLatestButton.disabled = true; restartLatestButton.textContent = "Restarting...";
            setAdvancedButtonsDisabled(true);

            fetch(`/action/restart_latest/${currentChatSessionId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(`Error restarting chat: ${data.error}`);
                    appendMessageToChatWindow({ sender: "System", text: `Restart Error: ${data.error}`, type: "system-error" });
                } else {
                    alert(data.message); // e.g., "Chat restarted as 'new_chat_name'."
                    // The response contains new_chat_name, messages, config, chat_session_id
                    currentChatSessionId = data.chat_session_id; // Update to the new chat ID

                    fetchSnapshotsAndUpdateList(currentChatSessionId); // Refresh list and highlight new chat

                    chatWindow.innerHTML = ''; // Clear old messages
                    if (data.messages && data.messages.length > 0) {
                        data.messages.forEach(msg => appendMessageToChatWindow(msg));
                    } else {
                        appendMessageToChatWindow({ sender: "System", text: "New chat session started.", type: "system-info" });
                    }
                    if (currentChatNameDisplay) currentChatNameDisplay.textContent = data.new_chat_name;
                    updateAnimationDisplay(currentChatSessionId); // Update animation for new chat
                    // No need to call highlightSnapshotInList separately if fetchSnapshotsAndUpdateList handles it
                }
            })
            .catch(error => {
                console.error('Restart latest action error:', error);
                appendMessageToChatWindow({ sender: "System", text: `Restart action failed: ${error.message}`, type: "system-error" });
                alert('An error occurred while restarting the chat.');
            })
            .finally(() => {
                restartLatestButton.disabled = false; restartLatestButton.textContent = "Restart w/ Latest Anim";
                setAdvancedButtonsDisabled(false);
                updateSendButtonState(); // Reflect changes to currentChatSessionId
            });
        });
    }

    if (reduceTokensButton) {
        reduceTokensButton.addEventListener('click', function() {
            if (!currentChatSessionId) { alert("No active chat session for token reduction."); return; }
            if (!confirm("Are you sure you want to summarize this chat and restart its history? This cannot be undone for the current session.")) return;

            reduceTokensButton.disabled = true; reduceTokensButton.textContent = "Reducing...";
            setAdvancedButtonsDisabled(true);

            fetch(`/action/reduce_tokens/${currentChatSessionId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(`Error reducing tokens: ${data.error}`);
                    appendMessageToChatWindow({ sender: "System", text: `Reduce Tokens Error: ${data.error}`, type: "system-error" });
                } else {
                    alert(data.message); // Display status message
                    appendMessageToChatWindow({ sender: "System", text: data.message, type: "system-info" });

                    chatWindow.innerHTML = ''; // Clear old messages
                    if (data.chat_history && data.chat_history.length > 0) {
                        data.chat_history.forEach(msg => appendMessageToChatWindow(msg));
                    } else {
                        appendMessageToChatWindow({ sender: "System", text: "Chat history cleared or unavailable after token reduction.", type: "system-info" });
                    }
                    if (data.refresh_animation) {
                        updateAnimationDisplay(currentChatSessionId);
                    }
                }
            })
            .catch(error => {
                console.error('Reduce tokens action error:', error);
                appendMessageToChatWindow({ sender: "System", text: `Reduce tokens action failed: ${error.message}`, type: "system-error" });
                alert('An error occurred while reducing tokens.');
            })
            .finally(() => {
                reduceTokensButton.disabled = false; reduceTokensButton.textContent = "Summarize & Restart";
                setAdvancedButtonsDisabled(false);
            });
        });
    }

    function setAdvancedButtonsDisabled(disabled) {
        if(restartLatestButton) restartLatestButton.disabled = disabled;
        if(reduceTokensButton) reduceTokensButton.disabled = disabled;
    }

    // --- Core Functions (condensed for brevity, assuming they exist as per previous steps) ---
    function fetchSnapshotsAndUpdateList(snapshotToHighlightAfterLoad) { /* ... */
        fetch('/snapshots').then(r => r.json()).then(names => {
            if(snapshotListUL) {
                snapshotListUL.innerHTML = '';
                if(names.length === 0) snapshotListUL.innerHTML = '<li>No chats.</li>';
                else names.forEach(name => {
                    const li=document.createElement('li'); const a=document.createElement('a');
                    a.href='#'; a.dataset.snapshotName=name; a.textContent=name;
                    li.appendChild(a); snapshotListUL.appendChild(li);
                });
            }
            const nameToHighlight = snapshotToHighlightAfterLoad || currentChatSessionId;
            if(nameToHighlight) highlightSnapshotInList(nameToHighlight);
        }).catch(e => { console.error(e); if(snapshotListUL) snapshotListUL.innerHTML='<li>Error.</li>'; });
    }
    function highlightSnapshotInList(snapshotName) { /* ... */
         document.querySelectorAll('#snapshot-list a').forEach(a => {
            a.classList.toggle('active', a.dataset.snapshotName === snapshotName);
        });
    }
    function updateAnimationDisplay(chatSessionIdForAnimation) { /* ... */
        if (!animationHeaderTitle || !animationContent) return;
        if (!chatSessionIdForAnimation) { animationHeaderTitle.textContent = "Animation Data"; animationContent.textContent = "No chat."; return; }
        animationHeaderTitle.textContent = `Anim Data - Step ... (Loading for ${chatSessionIdForAnimation})`; animationContent.textContent = "Loading...";
        fetch(`/animation_data/${chatSessionIdForAnimation}`).then(r => {if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()})
        .then(d => { if(d.error){animationHeaderTitle.textContent="Anim Data - Error";animationContent.textContent=d.error;}else{animationHeaderTitle.textContent=`Anim Data - Step ${d.step_number||0}`;animationContent.textContent=d.animation_data_str||"No data.";}})
        .catch(e => {console.error('Err anim data:',e);animationHeaderTitle.textContent="Anim Data - Fetch Error";animationContent.textContent=`Failed: ${e.message}`;});
    }
    function loadChat(snapshotName, isAutoLoad = false) { /* ... */
        chatWindow.innerHTML = `<div class="message system">Loading ${snapshotName}...</div>`;
        if(currentChatNameDisplay)currentChatNameDisplay.textContent=`Loading ${snapshotName}...`;
        const oldSessId=currentChatSessionId; currentChatSessionId=null; updateSendButtonState();updateAnimationDisplay(null);
        fetch(`/snapshots/${snapshotName}`).then(r=>{if(!r.ok)throw new Error(`HTTP ${r.status}`);return r.json()})
        .then(d=>{if(d.error){throw new Error(d.error);} currentChatSessionId=d.chat_session_id; chatWindow.innerHTML='';
            if(d.messages&&d.messages.length>0)d.messages.forEach(msg=>appendMessageToChatWindow(msg));else chatWindow.innerHTML='<div class="message system">No messages.</div>';
            if(currentChatNameDisplay)currentChatNameDisplay.textContent=d.name||snapshotName; highlightSnapshotInList(snapshotName); updateAnimationDisplay(currentChatSessionId);
        }).catch(e=>{console.error(`Err load ${snapshotName}:`,e);chatWindow.innerHTML=`<div class="message system">Error load ${snapshotName}: ${e.message}</div>`;if(currentChatNameDisplay)currentChatNameDisplay.textContent='Error';currentChatSessionId=oldSessId;if(oldSessId)highlightSnapshotInList(oldSessId);else highlightSnapshotInList(null);updateAnimationDisplay(currentChatSessionId);})
        .finally(()=>{updateSendButtonState();if(isAutoLoad&&window.history.replaceState){const u=new URL(window.location);u.searchParams.delete('new_chat_name');u.searchParams.delete('auto_load_chat');window.history.replaceState({path:u.href},'',u.href);}});
    }
    function appendMessageToChatWindow(messageData) { /* ... (using enhanced version from previous step) ... */
        const {sender,text,timestamp,context,type}=messageData; const msgDiv=document.createElement('div');msgDiv.classList.add('message');
        const senderClass=sender?sender.toLowerCase().replace(/\s+/g,'-'):'unknown'; msgDiv.classList.add(senderClass);
        if(type){const typeClass=type.toLowerCase().replace(/_/g,'-');msgDiv.classList.add(typeClass.startsWith('tag-')?typeClass:`message-${typeClass}`);}
        else if(senderClass==='system')msgDiv.classList.add('message-system-default');
        const senderSpan=document.createElement('span');senderSpan.classList.add('sender');senderSpan.textContent=`${sender||'System'}: `;
        const textSpan=document.createElement('span');textSpan.classList.add('text');textSpan.textContent=text||'';
        msgDiv.appendChild(senderSpan);msgDiv.appendChild(textSpan);
        if(timestamp){const tsSpan=document.createElement('span');tsSpan.classList.add('timestamp');try{const dO=(timestamp instanceof Date)?timestamp:new Date(timestamp);tsSpan.textContent=dO.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit',second:'2-digit'});}catch(e){tsSpan.textContent=String(timestamp);} msgDiv.appendChild(tsSpan);}
        chatWindow.appendChild(msgDiv); chatWindow.scrollTop=chatWindow.scrollHeight;
    }
    function updateSendButtonState() { /* ... (ensure it handles advanced buttons if needed) ... */
        const canInteract=!!currentChatSessionId;
        if(sendButton)sendButton.disabled=!canInteract; if(saveChatButton)saveChatButton.disabled=!canInteract;
        if(renderButton)renderButton.disabled=!canInteract; if(stopButton)stopButton.disabled=!canInteract;
        if(storeAnimationCheckbox)storeAnimationCheckbox.disabled=!canInteract;
        if(restartLatestButton)restartLatestButton.disabled=!canInteract; // Disable if no active chat
        if(reduceTokensButton)reduceTokensButton.disabled=!canInteract; // Disable if no active chat
        if(messageInput){messageInput.disabled=!canInteract;messageInput.placeholder=canInteract?`Type message in ${currentChatSessionId}...`:"Select/create chat";}
    }
    function sendMessage() { /* ... */
        const txt=messageInput.value.trim(); if(!txt||!currentChatSessionId)return;
        appendMessageToChatWindow({sender:'User',text:txt,timestamp:new Date().toISOString(),type:'TAG_USER_INPUT'});
        messageInput.value=''; sendButton.disabled=true;
        fetch(`/send_message/${currentChatSessionId}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:txt})})
        .then(r=>{if(!r.ok)return r.json().then(e=>{throw new Error(e.error||`HTTP ${r.status}`)}).catch(()=>{throw new Error(`HTTP ${r.status}`)});return r.json()})
        .then(d=>{if(d.error)appendMessageToChatWindow({sender:"System",text:`Error: ${d.error}`,type:"system-error"});else if(d.new_messages)d.new_messages.forEach(m=>appendMessageToChatWindow(m)); updateAnimationDisplay(currentChatSessionId);})
        .catch(e=>{appendMessageToChatWindow({sender:"System",text:`Send fail: ${e.message}`,type:"system-error"});}).finally(()=>{updateSendButtonState();messageInput.focus();});
    }
    if (sendButton && messageInput) { sendButton.addEventListener('click', sendMessage); messageInput.addEventListener('keypress', (e) => { if (e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMessage();}}); }

    // --- Initial Page Load Logic ---
    updateSendButtonState(); updateAnimationDisplay(null);
    const urlP = new URLSearchParams(window.location.search); const chatAutoLoad = urlP.get('auto_load_chat')||urlP.get('new_chat_name');
    if(chatAutoLoad){const link=document.querySelector(`#snapshot-list a[data-snapshot-name="${chatAutoLoad}"]`); if(link)loadChat(chatAutoLoad,true);else{console.warn(`Chat ${chatAutoLoad} for auto-load not in list.`);fetchSnapshotsAndUpdateList(chatAutoLoad);}}
    else{const activeLink=document.querySelector('#snapshot-list a.active');if(activeLink)loadChat(activeLink.dataset.snapshotName);else{const firstLink=document.querySelector('#snapshot-list a');if(firstLink){}else{if(currentChatNameDisplay)currentChatNameDisplay.textContent='None';if(snapshotListUL&&(snapshotListUL.children.length===0||snapshotListUL.firstElementChild?.textContent?.includes("No chats"))){chatWindow.innerHTML='<div class="message system">No chats. Click "New Chat".</div>';}}}}
    if(snapshotListUL&&snapshotListUL.children.length===0&&!chatAutoLoad){fetchSnapshotsAndUpdateList();}
});
