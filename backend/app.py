import socket
import threading
import sys
import time
import html

THREATS = {
    'cl.te': [],
    'te.cl': [],
    'te.te': [],
    'default': []
}
ADMIN_SECRET = "CgcWgAPyfrG5JZpPrFQ1YJPzF7G1obUT"

STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
    body {
        background-color: #050505;
        color: #0f0;
        font-family: 'Share Tech Mono', monospace;
        margin: 0;
        padding: 20px;
        background-image: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        background-size: 100% 2px, 3px 100%;
    }
    .container { max-width: 900px; margin: 0 auto; border: 1px solid #333; padding: 20px; box-shadow: 0 0 10px #0f0; }
    h1 { text-align: center; color: #f0f; text-shadow: 2px 2px #0f0; text-transform: uppercase; letter-spacing: 5px; }
    .status { border-bottom: 2px solid #0f0; margin-bottom: 20px; padding-bottom: 10px; display: flex; justify-content: space-between; }
    .blink { animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .log-entry { border: 1px solid #1a1a1a; padding: 10px; margin-bottom: 10px; background: #0a0a0a; white-space: pre-wrap; word-break: break-all; opacity: 0; animation: fadeIn 0.5s forwards; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    .timestamp { color: #888; font-size: 0.8em; }
    .btn { background: #000; color: #0f0; border: 1px solid #0f0; padding: 10px 20px; text-decoration: none; display: inline-block; transition: all 0.3s; cursor: pointer; }
    .btn:hover { background: #0f0; color: #000; box-shadow: 0 0 10px #0f0; }
    .alert { color: red; font-weight: bold; }
    .panel { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    .metric { border: 1px solid #333; padding: 10px; text-align: center; }
    .metric h2 { margin: 0; color: #f0f; font-size: 2em; }
</style>
"""

NAV = """
<div style="margin-bottom: 20px; text-align: center;">
    <a href="/" class="btn">HOME</a>
    <a href="/ids/dashboard" class="btn">THREAT LOGS</a>
    <a href="/admin" class="btn">ADMIN CONSOLE</a>
</div>
"""

def process_request(sock, method, path, headers, body):
    # Determine Context from X-Mode
    # The frontend injects 'x-mode' (cl.te, te.cl, te.te). 
    # Use this to separate databases.
    # Note: Headers keys are lowercased in handle_client but passed as dict here?
    # Let's check handle_client logic. Yes, headers[k.lower()] = v.
    mode = headers.get('x-mode', 'default').strip()
    if mode not in THREATS: mode = 'default'

    response_body = "Not Found"
    status = "404 Not Found"
    
    if path == "/":
        status = "200 OK"
        # Calculate Total Threats for THIS mode
        count = len(THREATS[mode])
        
        response_body = f"""
        <html><head><title>CyberSentinel IDS [{mode.upper()}]</title>{STYLE}</head>
        <body>
            <div class="container">
                <h1>CyberSentinel IDS <span style="font-size:0.5em; color:#555">//{mode.upper()}</span></h1>
                <div class="status">
                    <span>SYSTEM STATUS: <span style="color:#0f0">ONLINE</span></span>
                    <span class="blink">MONITORING ACTIVE</span>
                </div>
                {NAV}
                <div class="panel">
                    <div class="metric"><h2>99.9%</h2><p>UPTIME</p></div>
                    <div class="metric"><h2>{count}</h2><p>THREATS DETECTED</p></div>
                </div>
                <div style="text-align:center; padding: 50px;">
                    <p>AUTHENTICATION REQUIRED FOR CONFIGURATION</p>
                    <a href="/admin" class="btn">LOGIN</a>
                </div>
            </div>
        </body></html>
        """
        
    elif path == "/admin":
        cookie = headers.get('cookie', '')
        if f"secret={ADMIN_SECRET}" in cookie:
            status = "200 OK"
            response_body = f"""
            <html><head><title>Admin Console</title>{STYLE}</head>
            <body>
                <div class="container">
                    <h1>ACCESS GRANTED</h1>
                    {NAV}
                    <div class="log-entry" style="border-color: #f0f;">
                        <h3>WELCOME ADMINISTRATOR</h3>
                        <p>FLAG: FLAG{{SMUGGLING_MASTER_CLASS}}</p>
                    </div>
                </div>
            </body></html>
            """
        else:
            status = "403 Forbidden"
            response_body = f"""
            <html><head><title>Access Denied</title>{STYLE}</head>
            <body>
                <div class="container" style="border-color: red; box-shadow: 0 0 10px red;">
                    <h1 style="color: red;">ACCESS DENIED</h1>
                    {NAV}
                    <p style="text-align:center; font-size: 20px;">INVALID OR MISSING CREDENTIALS</p>
                </div>
            </body></html>
            """
            
    elif path == "/ids/report" and method == "POST":
        try:
            content = body.decode('utf-8', errors='ignore')
            val = ""
            if "threat_data=" in content:
                val = content.split("threat_data=", 1)[1]
            elif "comment=" in content:
                val = content.split("comment=", 1)[1]
            
            if val:
                user_cookie = headers.get('cookie', 'None')
                timestamp = time.strftime("%H:%M:%S")
                safe_val = html.escape(val)
                entry = f"<span class='timestamp'>[{timestamp}]</span> ORIGIN: {headers.get('host', 'UNKNOWN')} | COOKIE: {user_cookie[:10]}... <br>DATA: {safe_val}"
                
                # Append to Specific Mode List
                THREATS[mode].append(entry)
                
                status = "200 OK"
                response_body = "THREAT REPORT LOGGED"
            else:
                status = "400 Bad Request"
                response_body = "MISSING DATA"
        except:
             status = "500 Error"

    elif path == "/ids/dashboard":
        status = "200 OK"
        # Retrieve from Specific Mode List AND default (for smuggled requests without headers)
        current_logs = THREATS[mode] + THREATS['default']
        logs_html = "".join([f"<div class='log-entry'>{t}</div>" for t in reversed(current_logs)])
        
        response_body = f"""
        <html><head><title>Threat Dashboard</title>{STYLE}</head>
        <body>
            <div class="container">
                <h1>THREAT INTELLIGENCE <span style="font-size:0.5em; color:#555">//{mode.upper()}</span></h1>
                {NAV}
                
                <div style="border: 1px solid #333; padding: 10px; margin-bottom: 20px;">
                    <h3>SUBMIT NEW THREAT</h3>
                    <form action="/ids/report" method="POST">
                        <input type="text" name="threat_data" placeholder="ENTER THREAT SIGNATURE" style="background: #000; color: #0f0; border: 1px solid #0f0; padding: 10px; width: 70%;">
                        <input type="submit" value="UPLOAD" class="btn">
                    </form>
                </div>

                <div style="height: 500px; overflow-y: scroll; border: 1px solid #333; padding: 10px;">
                    {logs_html if logs_html else "<p>NO THREATS DETECTED</p>"}
                </div>
            </div>
        </body></html>
        """

    response = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Length: {len(response_body)}\r\n"
        "Content-Type: text/html\r\n"
        "Connection: keep-alive\r\n"
        "\r\n"
        f"{response_body}"
    )
    try:
        sock.sendall(response.encode('utf-8'))
    except: pass

def connection_handler(sock):
    # Buffer for the connection
    buf = b""
    while True:
        try:
            if not buf:
                chunk = sock.recv(4096)
                if not chunk: break
                buf += chunk
            
            if b"\r\n\r\n" not in buf:
                chunk = sock.recv(4096)
                if not chunk: break
                buf += chunk
                continue
                
            header_end = buf.find(b"\r\n\r\n") + 4
            header_part = buf[:header_end]
            
            headers_text = header_part.decode('utf-8', errors='ignore')
            lines = headers_text.split('\r\n')
            parts = lines[0].split(' ')
            if len(parts) < 2: break
            method, path = parts[0], parts[1]
            
            headers = {}
            raw_headers = lines[1:]
            for line in raw_headers:
                if ": " in line:
                    k, v = line.split(": ", 1)
                    headers[k.lower()] = v
            
            mode = headers.get('x-mode', 'default').lower()
            
            content_length = int(headers.get('content-length', 0))
            is_chunked = False
            
            if mode == 'te.cl':
                # TE.CL Vulnerability:
                # Frontend (TE) sees chunked.
                # Backend (CL) MUST IGNORE TE and use CL.
                # So we force is_chunked = False.
                is_chunked = False
            else:
                for line in raw_headers:
                    if ':' in line:
                        k, v = line.split(':', 1)
                        if k.strip().lower() == 'transfer-encoding':
                             if 'chunked' in v.lower():
                                 is_chunked = True
                                 break
            
            body_start_index = header_end
            
            if is_chunked:
                body_stream = buf[body_start_index:]
                parsed_len = 0
                decoded_body = b""
                
                while True:
                    if b"\r\n" not in body_stream:
                        more = sock.recv(4096)
                        if not more: break 
                        buf += more
                        body_stream = buf[body_start_index + parsed_len:]
                        continue
                    
                    nl_idx = body_stream.find(b"\r\n")
                    sz_line = body_stream[:nl_idx]
                    try:
                        sz = int(sz_line.strip(), 16)
                    except: break 
                    
                    parsed_len += nl_idx + 2
                    
                    if sz == 0:
                        if len(body_stream) < nl_idx + 2 + 2:
                             parsed_len += 2 
                             break
                        parsed_len += 2 
                        break
                    
                    total_chunk_len = sz + 2 
                    while len(body_stream) < nl_idx + 2 + total_chunk_len:
                        more = sock.recv(4096)
                        if not more: break
                        buf += more
                        body_stream = buf[body_start_index + parsed_len:]
                    
                    chunk_content = body_stream[nl_idx+2 : nl_idx+2+sz]
                    decoded_body += chunk_content
                    parsed_len += nl_idx + 2 + total_chunk_len
                    body_stream = body_stream[nl_idx+2+total_chunk_len:]
                
                process_request(sock, method, path, headers, decoded_body)
                buf = buf[body_start_index + parsed_len:] 
                
            else:
                total_needed = body_start_index + content_length
                while len(buf) < total_needed:
                    more = sock.recv(4096)
                    if not more: break
                    buf += more
                
                req_body = buf[body_start_index : body_start_index + content_length]
                process_request(sock, method, path, headers, req_body)
                buf = buf[total_needed:]

        except Exception as e:
            # print(f"Connection Error: {e}")
            break
    sock.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 8888))
    s.listen(100)
    print("Backend listening on 8888")
    
    while True:
        client, addr = s.accept()
        t = threading.Thread(target=connection_handler, args=(client,))
        t.start()

if __name__ == "__main__":
    main()
