"""
CursorOS HTTP Server Wrapper
Exposes the existing backend via a local HTTP API for Electron.
"""
import os
import sys
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Add the DONA project root to path so 'backend' package is importable
wrapper_dir = os.path.dirname(os.path.abspath(__file__))

# Try multiple strategies to find the DONA root
possible_roots = [
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(wrapper_dir)))),
    os.getcwd(),
    os.path.dirname(os.path.dirname(os.path.dirname(wrapper_dir))),
]

dona_root = None
for root in possible_roots:
    if os.path.isdir(os.path.join(root, 'backend', 'core')):
        dona_root = root
        break

if dona_root is None:
    dona_root = os.getcwd()

sys.path.insert(0, dona_root)
print(f'[Wrapper] DONA root: {dona_root}', flush=True)

# Load .env from backend/ directory
try:
    from dotenv import load_dotenv
    env_path = os.path.join(dona_root, 'backend', '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f'[Wrapper] Loaded .env from {env_path}', flush=True)
except Exception as e:
    print(f'[Wrapper] Warning: Could not load .env: {e}', flush=True)

from backend.core.agent import Agent
from backend.core.os_context import get_open_explorer_windows, read_file_content
from backend.core.llm import llm_service
from backend.tasks.organise_folder import OrganiseFolderTask
from backend.tasks.find_file import FindFileTask


class CursorOSHandler(BaseHTTPRequestHandler):
    agent = None
    current_plan = {"actions": [], "context": {}}
    event_queue = []

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/status':
            self._json_response({"status": "ok", "version": "2.0.0"})
        elif parsed.path == '/api/events':
            events = self.event_queue.copy()
            self.event_queue.clear()
            self._json_response({"events": events})
        else:
            self._json_response({"error": "Not found"}, 404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}
        parsed = urlparse(self.path)

        if parsed.path == '/api/submit':
            self._handle_submit(body)
        elif parsed.path == '/api/execute':
            self._handle_execute()
        elif parsed.path == '/api/confirm-org':
            self._handle_confirm_org(body)
        elif parsed.path == '/api/open-file':
            self._handle_open_file(body)
        else:
            self._json_response({"error": "Not found"}, 404)

    def _handle_submit(self, body):
        text = body.get('text', '')
        mode = body.get('mode', 'Auto')
        thread = threading.Thread(target=self._process_query, args=(text, mode), daemon=True)
        thread.start()
        self._json_response({"status": "processing"})

    def _process_query(self, text, mode):
        self._emit_event({"type": "task_step", "id": "plan", "description": "Thinking..."})
        self._emit_event({"type": "task_status", "id": "plan", "status": "in-progress"})
        try:
            context = {"explorer_windows": get_open_explorer_windows()}
            plan = self.agent.think(text, context)
            actions = plan.get("actions", [])
            self.current_plan["actions"] = actions
            self._emit_event({"type": "task_status", "id": "plan", "status": "completed"})
            if mode == "Plan":
                self._emit_event({"type": "plan_ready"})
            else:
                self._execute_actions(actions, text)
        except Exception as e:
            print(f"Planning Error: {e}")
            self._emit_event({"type": "task_status", "id": "plan", "status": "failed"})

    def _execute_actions(self, actions, user_text):
        last_result_path = None
        for i, action_item in enumerate(actions):
            action = action_item.get("action")
            params = action_item.get("params", {})
            explanation = action_item.get("explanation", "Working...")
            task_id = f"task_{i}"
            self._emit_event({"type": "task_step", "id": task_id, "description": explanation})
            self._emit_event({"type": "task_status", "id": task_id, "status": "in-progress"})
            try:
                if action == "find_file":
                    search_desc = params.get("description") or user_text
                    task = FindFileTask()
                    results, msg = task.run(search_desc)
                    if results:
                        last_result_path = results[0]
                        self._emit_event({"type": "results", "items": results})
                    else:
                        raise Exception(f"Could not find '{search_desc}'")

                elif action == "organise_folder":
                    folder_path = params.get("path") or last_result_path
                    if not folder_path:
                        raise Exception("No path provided.")
                    task = OrganiseFolderTask()
                    proposal, err = task.propose(folder_path)
                    if err:
                        raise Exception(err)
                    self._emit_event({"type": "org_preview", "proposal": proposal})

                elif action == "open_path":
                    folder_path = params.get("path") or last_result_path
                    if folder_path:
                        os.startfile(folder_path)
                        self._emit_event({"type": "hide"})

                elif action == "copy_path":
                    folder_path = params.get("path") or last_result_path
                    if folder_path:
                        import subprocess
                        subprocess.run(['clip'], input=folder_path.encode(), check=True)
                        self._emit_event({"type": "message", "text": f"Copied to clipboard: {folder_path}"})

                elif action == "peek_file":
                    folder_path = params.get("path") or last_result_path
                    if folder_path:
                        content, err = read_file_content(folder_path)
                        if err:
                            raise Exception(err)
                        prompt = f"The user asked: '{user_text}'\n\nHere is the beginning of the file '{os.path.basename(folder_path)}':\n\n{content}\n\nBased on this content, provide a concise answer or summary."
                        response = llm_service.call("You are a helpful desktop assistant.", prompt)
                        self._emit_event({"type": "message", "text": response})

                elif action == "chat":
                    message = params.get("message", "...")
                    self._emit_event({"type": "message", "text": message})

                self._emit_event({"type": "task_status", "id": task_id, "status": "completed"})

            except Exception as e:
                print(f"Action failed: {e}")
                self._emit_event({"type": "task_status", "id": task_id, "status": "failed"})
                break

    def _handle_execute(self):
        actions = self.current_plan.get("actions", [])
        threading.Thread(target=self._execute_actions, args=(actions, ""), daemon=True).start()
        self._json_response({"status": "executing"})

    def _handle_confirm_org(self, body):
        proposal = body.get('proposal', [])
        actions = self.current_plan.get("actions", [])
        for action_item in actions:
            if action_item.get("action") == "organise_folder":
                params = action_item.get("params", {})
                folder_path = params.get("path")
                if folder_path and proposal:
                    task = OrganiseFolderTask()
                    results, msg = task.execute(folder_path, proposal)
                    self._emit_event({"type": "message", "text": msg})
                    break
        self._json_response({"status": "confirmed"})

    def _handle_open_file(self, body):
        file_path = body.get('path', '')
        if file_path:
            os.startfile(file_path)
        self._json_response({"status": "ok"})

    def _emit_event(self, event):
        self.event_queue.append(event)

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        pass


def main():
    port = int(os.environ.get('CURSOROS_HTTP_PORT', 9182))
    CursorOSHandler.agent = Agent()
    server = HTTPServer(('localhost', port), CursorOSHandler)
    print(f'SERVER_READY — CursorOS HTTP server on port {port}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
