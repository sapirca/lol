import os
import json
import re
from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

# --- Attempt to import project modules ---
try:
    from constants import (FLASK_SNAPSHOTS_DIR, TAG_USER_INPUT, TAG_ASSISTANT, TAG_SYSTEM, TAG_SYSTEM_INTERNAL, TAG_ACTION_RESULTS,
                           MESSAGE_SNAPSHOT_FILE, CONFIG_FILE, MODEL_CONFIGS, TIME_FORMAT, DEFAULT_CONFIG)
    from controller.logic_pp import LogicPlusPlus
    PROJECT_MODULES_IMPORTED = True
except ImportError as e:
    print(f"Warning: Error importing project modules: {e}. Using fallbacks.")
    PROJECT_MODULES_IMPORTED = False
    FLASK_SNAPSHOTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "snapshots_fallback"))
    TAG_USER_INPUT, TAG_ASSISTANT, TAG_SYSTEM, TAG_SYSTEM_INTERNAL, TAG_ACTION_RESULTS = "TAG_USER_INPUT", "TAG_ASSISTANT", "TAG_SYSTEM", "TAG_SYSTEM_INTERNAL", "TAG_ACTION_RESULTS"
    MESSAGE_SNAPSHOT_FILE, CONFIG_FILE = "messages.jsonl", "config.json"
    MODEL_CONFIGS = {
        "dummy-claude": {"model_name": "claude-dummy", "max_tokens": 1000, "backend": "Claude"},
        "dummy-gpt": {"model_name": "gpt-dummy", "max_tokens": 1000, "backend": "GPT"},
    }
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
    DEFAULT_CONFIG = {"auto_save_on_new_message": True, "print_internal_messages": False, "song_name":"default_song"}

    class DummyMessages:
        def __init__(self): self.messages = []; self.new_message_flags = {}
        def add_message(self, tag, text, context, visible=True, timestamp=None): # Added visible, matching LPP
            ts = timestamp or datetime.now().strftime(LogicPlusPlus.TIME_FORMAT) # Use LPP's time format
            self.messages.append([ts, text, tag, visible, context]) # Matches LPP internal order
        def get_new_messages(self): return []
        def messages_chronological(self): # Sort by timestamp (index 0)
            return sorted(self.messages, key=lambda m: m[0])


    class LogicPlusPlus:
        # Class constants for dummy
        TIME_FORMAT = TIME_FORMAT
        TAG_USER_INPUT, TAG_ASSISTANT, TAG_SYSTEM, TAG_SYSTEM_INTERNAL, TAG_ACTION_RESULTS = TAG_USER_INPUT, TAG_ASSISTANT, TAG_SYSTEM, TAG_SYSTEM_INTERNAL, TAG_ACTION_RESULTS
        DEFAULT_CONFIG = DEFAULT_CONFIG

        def __init__(self, snapshot_name=None, base_snapshots_dir=None, restart_config=None):
            self.base_snapshots_dir = base_snapshots_dir if base_snapshots_dir else FLASK_SNAPSHOTS_DIR
            self.msgs = DummyMessages() # Use enhanced DummyMessages
            self.animation_manager = self.DummyAnimationManager()

            if restart_config: # This is an old_controller instance
                self.snapshot_name = snapshot_name or f"restarted_{restart_config.snapshot_name[:10]}_{datetime.now().strftime('%H%M%S')}"
                self.config = dict(restart_config.config) # Deep copy config
                self.config["song_name"] = f"Restarted {self.config.get('song_name', 'unknown_song')}"
                self.snapshot_path = os.path.join(self.base_snapshots_dir, self.snapshot_name)
                self.msgs.add_message(self.TAG_SYSTEM, f"Restarted session from {restart_config.snapshot_name}. Latest animation sequence applied.", {}, True)
                if hasattr(restart_config, 'animation_manager') and restart_config.animation_manager:
                     self.animation_manager.latest_sequence = restart_config.animation_manager.latest_sequence
                     self.animation_manager.step_number = restart_config.animation_manager.step_number
            elif snapshot_name:
                self.snapshot_name = snapshot_name
                self.snapshot_path = os.path.join(self.base_snapshots_dir, self.snapshot_name)
                self.config = self._load_config()
                self._load_messages_from_file() # Simulate loading messages
            else: # New, untitled
                self.snapshot_name = f"untitled_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                self.snapshot_path = os.path.join(self.base_snapshots_dir, self.snapshot_name) # Path for potential save
                self.config = self.DEFAULT_CONFIG.copy()

            print(f"Dummy LogicPlusPlus initialized: {self.snapshot_name}. Config: {self.config.get('song_name')}")


        class DummyAnimationManager: # (Same as before)
            def __init__(self): self.latest_sequence = "Default dummy anim"; self.step_number = 0; self.sequence_manager = self
            def get_latest_sequence_with_step(self): self.step_number += 1; self.latest_sequence = f"Anim step {self.step_number}"; return (self.latest_sequence, self.step_number)
            def get_animation_filename(self): return "/dummy/anim.ext"

        def _load_config(self):
            config_p = os.path.join(self.snapshot_path, CONFIG_FILE)
            if os.path.exists(config_p):
                try:
                    with open(config_p, 'r') as f: return json.load(f)
                except Exception as ex: print(f"Dummy LPP: Error loading config {config_p}: {ex}")
            return self.DEFAULT_CONFIG.copy()

        def _load_messages_from_file(self): # New dummy method
            messages_path = os.path.join(self.snapshot_path, MESSAGE_SNAPSHOT_FILE)
            if os.path.exists(messages_path):
                with open(messages_path, 'r') as f:
                    for line in f:
                        try:
                            # LPP stores as: [timestamp, message_text, tag, visible, context]
                            loaded_msg_parts = json.loads(line.strip())
                            self.msgs.messages.append(loaded_msg_parts) # Add directly to messages list
                        except: pass # Ignore malformed lines in dummy

        def update_config(self, new_cfg): self.config.update(new_cfg)
        def add_user_input_to_chat(self, text): self.msgs.add_message(self.TAG_USER_INPUT, text, {})
        def communicate(self, text):
            if hasattr(self, 'animation_manager') and self.animation_manager: self.animation_manager.step_number +=1
            self.msgs.add_message(self.TAG_ASSISTANT, f"Response to: {text}", {}, True) # Dummy response
            return []
        def save_snapshot_if_needed(self): self.save_snapshot() # Dummy always saves
        def save_snapshot(self, snapshot_name_to_save_as=None):
            original_name = self.snapshot_name
            if snapshot_name_to_save_as:
                self.snapshot_name = snapshot_name_to_save_as
                self.snapshot_path = os.path.join(self.base_snapshots_dir, self.snapshot_name)
            if not os.path.exists(self.snapshot_path): os.makedirs(self.snapshot_path)
            with open(os.path.join(self.snapshot_path, CONFIG_FILE), 'w') as f: json.dump(self.config, f, indent=2)
            with open(os.path.join(self.snapshot_path, MESSAGE_SNAPSHOT_FILE), 'w') as f:
                for msg_tuple in self.msgs.messages_chronological(): # Save sorted messages
                    f.write(json.dumps(msg_tuple) + "\n")
        def build_skeleton_sync(self): self.msgs.add_message(self.TAG_SYSTEM, "[Dummy] Skeleton plan generated.", {}, True)
        def add_system_message(self, text, context=None): self.msgs.add_message(self.TAG_SYSTEM, text, context or {})
        def render(self, store_animation=False): return f"[Dummy] Rendered (Store: {store_animation})"
        def stop(self): return "[Dummy] Stopped"

        def _tag_to_sender(self, tag):
            return {self.TAG_USER_INPUT: "User", self.TAG_ASSISTANT: "Assistant", self.TAG_SYSTEM: "System",
                    self.TAG_SYSTEM_INTERNAL: "SystemInternal", self.TAG_ACTION_RESULTS: "Action"}.get(tag, "System")

        def get_chat_history_for_display(self):
            display_messages = []
            for ts, text, tag, vis, ctx in self.msgs.messages_chronological():
                if vis or self.config.get("print_internal_messages", False):
                    display_messages.append({"sender": self._tag_to_sender(tag), "text": text, "timestamp": ts, "context": ctx or {}, "type": tag})
            return display_messages

        def reduce_tokens(self):
            if len(self.msgs.messages) > 1:
                summary_msg = f"Summarized previous {len(self.msgs.messages)} messages."
                last_message = self.msgs.messages_chronological()[-1]
                self.msgs.messages = [] # Clear existing
                self.msgs.add_message(self.TAG_SYSTEM, summary_msg, {}, True)
                self.msgs.add_message(last_message[2], last_message[1], last_message[4], last_message[3], timestamp=last_message[0]) # Re-add last message with its details
                return f"Successfully reduced tokens. {summary_msg}"
            return "Not enough messages to reduce tokens."

app = Flask(__name__)
active_controllers = {}
if not os.path.exists(FLASK_SNAPSHOTS_DIR): os.makedirs(FLASK_SNAPSHOTS_DIR)

def is_valid_chat_name_flask(name, check_exists=True): # (Same as before)
    if not name or not isinstance(name,str) or len(name)>50 or (name[0].isdigit() and not name.startswith("chat_")) or not re.match(r'^[a-zA-Z0-9_-]+$',name): return False
    return not (check_exists and os.path.exists(os.path.join(FLASK_SNAPSHOTS_DIR,name)))

# --- Standard Routes (condensed for brevity) ---
@app.route('/')
def index(): snapshot_names=sorted([d for d in os.listdir(FLASK_SNAPSHOTS_DIR) if os.path.isdir(os.path.join(FLASK_SNAPSHOTS_DIR,d))]) if os.path.exists(FLASK_SNAPSHOTS_DIR) else []; auto_load=request.args.get('new_chat_name'); active_snap=auto_load if auto_load in snapshot_names else None; return render_template('index.html',snapshots=snapshot_names,chat_history=[{'sender':'System','text':'Welcome!'}],active_snapshot=active_snap,auto_load_chat=auto_load)
@app.route('/new_chat_form')
def new_chat_form_route(): backends=sorted(list(set(d.get("backend","N/A") for _,d in MODEL_CONFIGS.items()))); songs=["s1","s2"]; frameworks=["f1","f2"]; existing=[d for d in os.listdir(FLASK_SNAPSHOTS_DIR) if os.path.isdir(os.path.join(FLASK_SNAPSHOTS_DIR,d))] if os.path.exists(FLASK_SNAPSHOTS_DIR) else []; return render_template('new_chat_form.html',model_configs_json=json.dumps(MODEL_CONFIGS),backends=backends,songs=songs,frameworks=frameworks,existing_chat_names_json=json.dumps(existing))
@app.route('/create_new_chat', methods=['POST'])
def create_new_chat_route(): # (Condensed)
    data=request.form; name=data.get('chat_name',f"chat_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    if not is_valid_chat_name_flask(name): return f"Invalid name: {name}",400
    cfg={"song_name":data.get('song_name'),"framework":data.get('framework'),"selected_backend":data.get('backend'),"model_key":data.get('model'),"model_config":MODEL_CONFIGS.get(data.get('model'),{}),"auto_save_on_new_message":True,"print_internal_messages":False}
    try:
        new_dir=os.path.join(FLASK_SNAPSHOTS_DIR,name); os.makedirs(new_dir)
        with open(os.path.join(new_dir,CONFIG_FILE),"w") as f:json.dump(cfg,f,indent=2)
        with open(os.path.join(new_dir,MESSAGE_SNAPSHOT_FILE),"w") as f:pass
        ctrl=LogicPlusPlus(snapshot_name=name,base_snapshots_dir=FLASK_SNAPSHOTS_DIR); active_controllers[name]=ctrl
        if data.get('start_with_skeleton')=='on': ctrl.build_skeleton_sync(); ctrl.save_snapshot_if_needed()
        return redirect(url_for('index',new_chat_name=name))
    except Exception as e: print(f"E create {name}:{e}"); return "Error",500
@app.route('/snapshots')
def get_snapshot_list(): return jsonify(sorted([d for d in os.listdir(FLASK_SNAPSHOTS_DIR) if os.path.isdir(os.path.join(FLASK_SNAPSHOTS_DIR,d))]) if os.path.exists(FLASK_SNAPSHOTS_DIR) else [])
@app.route('/snapshots/<snapshot_name>')
def load_snapshot(snapshot_name): # (Condensed)
    s_dir=os.path.join(FLASK_SNAPSHOTS_DIR,snapshot_name); cfg={}; hist=[]
    if not os.path.isdir(s_dir): return jsonify({"error":"Not found"}),404
    try:
        cfg_p=os.path.join(s_dir,CONFIG_FILE); cfg=json.load(open(cfg_p)) if os.path.exists(cfg_p) else {"print_internal_messages":True};
        if not os.path.exists(cfg_p): json.dump(cfg,open(cfg_p,'w'))
        msg_p=os.path.join(s_dir,MESSAGE_SNAPSHOT_FILE)
        if os.path.exists(msg_p):
            with open(msg_p,'r') as f:
                for i,l in enumerate(f):
                    try: ts,txt,tag,vis,ctx=json.loads(l.strip()); hist.append({"sender":LogicPlusPlus._tag_to_sender(None,tag),"text":txt,"timestamp":ts,"context":ctx or {},"type":tag})
                    except: pass # skip line
        if snapshot_name not in active_controllers: active_controllers[snapshot_name]=LogicPlusPlus(snapshot_name=snapshot_name,base_snapshots_dir=FLASK_SNAPSHOTS_DIR)
        else: active_controllers[snapshot_name].config = cfg # Ensure active controller has latest config
        hist.sort(key=lambda m:m.get("timestamp",""))
        return jsonify({"messages":hist,"name":snapshot_name,"config":cfg,"chat_session_id":snapshot_name})
    except Exception as e: print(f"E load {snapshot_name}:{e}"); return jsonify({"error":str(e)}),500
@app.route('/save_snapshot/<chat_session_id>', methods=['POST'])
def save_snapshot_route(chat_session_id): # (Condensed)
    data=request.get_json(); new_name=data.get('new_snapshot_name',"").strip()
    if chat_session_id not in active_controllers: return jsonify({"error":"No active chat"}),404
    ctrl=active_controllers[chat_session_id]; orig_id=ctrl.snapshot_name; final_name=orig_id; renamed=False
    if new_name and new_name!=orig_id:
        if not is_valid_chat_name_flask(new_name): return jsonify({"error":"Invalid name"}),400
        final_name=new_name; new_dir=os.path.join(FLASK_SNAPSHOTS_DIR,final_name);
        if not os.path.exists(new_dir): os.makedirs(new_dir)
        renamed=True
    else: cur_dir=os.path.join(FLASK_SNAPSHOTS_DIR,final_name); os.makedirs(cur_dir,exist_ok=True)
    try:
        ctrl.save_snapshot(snapshot_name_to_save_as=final_name)
        if renamed: active_controllers[final_name]=active_controllers.pop(orig_id)
        return jsonify({"message":f"Saved as '{final_name}'.","saved_snapshot_name":final_name,"was_renamed":renamed,"original_snapshot_name":orig_id if renamed else None})
    except Exception as e: print(f"E save {final_name}:{e}"); return jsonify({"error":str(e)}),500
@app.route('/send_message/<chat_session_id>', methods=['POST'])
def send_chat_message(chat_session_id): # (Condensed)
    data=request.get_json(); user_msg=data.get('message')
    if not user_msg: return jsonify({"error":"No msg"}),400
    if chat_session_id not in active_controllers:
        if not os.path.isdir(os.path.join(FLASK_SNAPSHOTS_DIR,chat_session_id)): return jsonify({"error":"No dir"}),404
        active_controllers[chat_session_id]=LogicPlusPlus(snapshot_name=chat_session_id,base_snapshots_dir=FLASK_SNAPSHOTS_DIR)
    ctrl=active_controllers[chat_session_id]
    try:
        ctrl.add_user_input_to_chat(user_msg); ctrl.communicate(user_msg); new_msgs=[]
        for ts,txt,tag,vis,ctx in ctrl.msgs.get_new_messages(): # get_new_messages in dummy is empty, use all for test
             for ts_m, txt_m, tag_m, vis_m, ctx_m in ctrl.msgs.messages_chronological(): # Use all messages for dummy testing
                 if vis_m or ctrl.config.get("print_internal_messages",False): new_msgs.append({"sender":ctrl._tag_to_sender(tag_m),"text":txt_m,"timestamp":ts_m,"context":ctx_m or {},"type":tag_m})
        if ctrl.config.get("auto_save_on_new_message",True): ctrl.save_snapshot_if_needed()
        return jsonify({"new_messages":new_msgs[-2:] if new_msgs else [] }) # Return last 2 for dummy
    except Exception as e: print(f"E send {chat_session_id}:{e}"); return jsonify({"error":str(e)}),500
@app.route('/animation_data/<chat_session_id>')
def get_animation_data_route(chat_session_id): # (Condensed)
    if chat_session_id not in active_controllers: return jsonify({"animation_data_str":"No ctrl","step_number":0}),404
    ctrl=active_controllers[chat_session_id]
    if not hasattr(ctrl,'animation_manager') or not ctrl.animation_manager: return jsonify({"animation_data_str":"No anim","step_number":0}),500
    try:
        seq,step=ctrl.animation_manager.get_latest_sequence_with_step(); return jsonify({"animation_data_str":str(seq),"step_number":int(step)})
    except Exception as e: print(f"E anim {chat_session_id}:{e}"); return jsonify({"error":str(e)}),500
@app.route('/action/render/<chat_session_id>', methods=['POST'])
def action_render_route(chat_session_id): # (Condensed)
    if chat_session_id not in active_controllers: return jsonify({"error":"No ctrl"}),404
    ctrl=active_controllers[chat_session_id]; data=request.get_json(); store=data.get('store_animation',False) if data else False
    try: msg=ctrl.render(store_animation=store); return jsonify({"message":msg,"refresh_animation":True})
    except Exception as e: print(f"E render {chat_session_id}:{e}"); return jsonify({"error":str(e)}),500
@app.route('/action/stop/<chat_session_id>', methods=['POST'])
def action_stop_route(chat_session_id): # (Condensed)
    if chat_session_id not in active_controllers: return jsonify({"error":"No ctrl"}),404
    ctrl=active_controllers[chat_session_id]
    try: msg=ctrl.stop(); return jsonify({"message":msg,"refresh_animation":True})
    except Exception as e: print(f"E stop {chat_session_id}:{e}"); return jsonify({"error":str(e)}),500

# --- New Advanced Action Routes ---
@app.route('/action/restart_latest/<chat_session_id>', methods=['POST'])
def action_restart_latest_route(chat_session_id):
    if chat_session_id not in active_controllers:
        return jsonify({"error": "Original chat session not found."}), 404
    old_controller = active_controllers[chat_session_id]
    try:
        prospective_new_name = f"restarted_{old_controller.snapshot_name[:15]}_{datetime.now().strftime('%H%M%S')}"
        new_chat_name = prospective_new_name; counter = 1
        while not is_valid_chat_name_flask(new_chat_name, check_exists=True): # Ensure unique name
            new_chat_name = f"{prospective_new_name}_{counter}"; counter += 1
            if counter > 100: return jsonify({"error": "Could not generate unique name for restarted chat."}), 500

        new_snapshot_dir = os.path.join(FLASK_SNAPSHOTS_DIR, new_chat_name)
        if not os.path.exists(new_snapshot_dir): os.makedirs(new_snapshot_dir)

        # Initialize new controller, passing old_controller to constructor for restart logic
        new_controller = LogicPlusPlus(snapshot_name=new_chat_name, base_snapshots_dir=FLASK_SNAPSHOTS_DIR, restart_config=old_controller)
        new_controller.save_snapshot() # Persist initial state of new chat

        active_controllers[new_chat_name] = new_controller

        initial_messages = new_controller.get_chat_history_for_display()
        config = new_controller.config

        return jsonify({
            "message": f"Chat restarted as '{new_chat_name}'.",
            "new_chat_name": new_chat_name,
            "messages": initial_messages,
            "config": config,
            "chat_session_id": new_chat_name # Ensure client updates to this new ID
        })
    except Exception as e:
        print(f"Error restarting chat from {chat_session_id}: {e}"); import traceback; traceback.print_exc()
        return jsonify({"error": f"Error restarting chat: {str(e)}"}), 500

@app.route('/action/reduce_tokens/<chat_session_id>', methods=['POST'])
def action_reduce_tokens_route(chat_session_id):
    if chat_session_id not in active_controllers:
        return jsonify({"error": "Chat session not found."}), 404
    controller = active_controllers[chat_session_id]
    try:
        status_message = controller.reduce_tokens()
        controller.save_snapshot()
        updated_history = controller.get_chat_history_for_display()
        return jsonify({
            "message": status_message,
            "chat_history": updated_history,
            "refresh_animation": True
        })
    except Exception as e:
        print(f"Error reducing tokens for {chat_session_id}: {e}"); import traceback; traceback.print_exc()
        return jsonify({"error": f"Error reducing tokens: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
