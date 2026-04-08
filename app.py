from flask import Flask, render_template, request
import time
import uuid

app = Flask(__name__)

tokens = {}
pending_requests = {}
logs = []
status_message = ""
token_time = 0
current_resource = ""

resources = ["VM-1", "VM-2", "Container-1"]

@app.route('/')
def home():
    return render_template('index.html', resources=resources, status=status_message, time_left=token_time)

# 🔐 Request Access
@app.route('/request_access', methods=['POST'])
def request_access():
    global status_message, current_resource

    resource = request.form.get('resource')
    request_id = str(uuid.uuid4())

    pending_requests[request_id] = resource
    current_resource = resource

    logs.append(f"📩 Request for {resource}")

    status_message = f"📨 Request sent for {resource} (Waiting for approval)"

    return render_template('index.html', resources=resources, status=status_message, time_left=0)

# 🔐 Approve
@app.route('/approve_latest')
def approve_latest():
    global status_message, token_time

    if pending_requests:
        request_id, resource = pending_requests.popitem()

        token = str(uuid.uuid4())
        expiry = time.time() + 300

        tokens[token] = {
            "resource": resource,
            "expiry": expiry
        }

        token_time = 300

        logs.append(f"✅ Approved {resource}")
        logs.append(f"🔑 Token: {token[:8]}...")

        status_message = f"✅ Approved for {resource}! Token: {token}"

    else:
        status_message = "❌ No pending requests"

    return render_template('index.html', resources=resources, status=status_message, time_left=token_time)

# 🔐 Access Resource (RESOURCE VALIDATION 🔥)
@app.route('/access_resource', methods=['POST'])
def access_resource():
    global status_message

    token = request.form.get('token')
    resource = request.form.get('resource_access')

    logs.append("🔍 Access attempt")

    if token in tokens:
        token_data = tokens[token]

        if time.time() > token_data["expiry"]:
            status_message = "❌ Token Expired"
            logs.append("⚠ Expired token")

        elif token_data["resource"] != resource:
            status_message = "🚫 Access Denied (Wrong Resource)"
            logs.append("🚫 Wrong resource access attempt")

        else:
            status_message = "✅ Access Granted"
            logs.append(f"✔ Accessed {resource}")

    else:
        status_message = "❌ Invalid Token"
        logs.append("❌ Invalid token")

    return render_template('index.html', resources=resources, status=status_message, time_left=0)

# 📊 Logs
@app.route('/logs')
def view_logs():
    log_html = "".join([f"<li>{log}</li>" for log in logs])

    return f"""
    <body style="background:#0f172a;color:white;padding:40px;">
    <h2>📊 System Logs</h2>
    <ul>{log_html}</ul>
    <br>
    <a href="/" style="color:#38bdf8;">⬅ Back</a>
    </body>
    """

if __name__ == '__main__':
    app.run(debug=True)