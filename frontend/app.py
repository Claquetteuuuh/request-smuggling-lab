import socket
import threading
import time
import select

BACKEND_HOST = 'backend'
BACKEND_PORT = 8888

# Global socket to backend + Lock for thread safety/sequencing
# We want to share the connection so that Request 1 (Attacker) and Request 2 (Bot) go over same socket
backend_sock = None
backend_lock = threading.Lock()

def get_backend_sock():
    global backend_sock
    if backend_sock is None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((BACKEND_HOST, BACKEND_PORT))
            backend_sock = s
        except:
            return None
    return backend_sock

def reset_backend():
    global backend_sock
    if backend_sock:
        try: backend_sock.close() 
        except: pass
    backend_sock = None

def forward_to_backend(data):
    # This function handles sending data to backend and receiving the response
    # It returns the response bytes
    with backend_lock:
        s = get_backend_sock()
        if not s: return b"HTTP/1.1 502 Bad Gateway\r\n\r\nBackend Down"
        
        try:
            s.sendall(data)
            
            # Read Response
            # We need to read until complete HTTP response
            # Simple heuristic: Read until headers done, then CL or Chunked
            # Simplified: Just read a bit? No, must be complete for proxy to work
            # For this lab, assume backend responds quickly and nicely
            
            response = b""
            while True:
                # Use select to wait for data with timeout
                ready = select.select([s], [], [], 1.0)
                if ready[0]:
                    chunk = s.recv(4096)
                    if not chunk: 
                        reset_backend()
                        break
                    response += chunk
                    
                    # Heuristic end check
                    if b"Content-Length: " in response:
                         # Check if we have full body
                         # Extract CL
                         try:
                             head, _ = response.split(b"\r\n\r\n", 1)
                             for line in head.decode(errors='ignore').split('\r\n'):
                                 if line.lower().startswith("content-length:"):
                                     cl = int(line.split(":")[1].strip())
                                     if len(response) >= len(head) + 4 + cl:
                                         return response # Done
                         except: pass
                    
                    # If assume short responses for lab:
                    if len(chunk) < 4096:
                         # Maybe done? 
                         pass
                else:
                    # Timeout implies done for now?
                    break
            
            return response
            
        except Exception as e:
            reset_backend()
            return f"HTTP/1.1 502 Bad Gateway\r\n\r\nError: {e}".encode()


def handle_client(client_sock, mode):
    try:
        req = b""
        while b"\r\n\r\n" not in req:
            chunk = client_sock.recv(4096)
            if not chunk: break
            req += chunk
            
        if not req: return

        header_part, body_start = req.split(b"\r\n\r\n", 1)
        headers_str = header_part.decode('utf-8', errors='ignore')
        lines = headers_str.split('\r\n')
        
        # Inject X-Mode
        # We reconstruct the headers
        new_headers = [lines[0]]
        new_headers.append(f"X-Mode: {mode}")
        
        te_found = False
        cl_val = 0
        
        for line in lines[1:]:
             new_headers.append(line)
             if line.lower().startswith("content-length:"):
                 cl_val = int(line.split(":")[1].strip())
             if line.lower().startswith("transfer-encoding:"):
                 te_found = True
        
        # LOGIC FOR MODES
        
        if mode == 'te.te':
            # WAF Logic: If we see Transfer-Encoding, BLOCK
            # This is a naive WAF. User must bypass it.
            # Bypasses: "Transfer-Encoding : chunked", "X: Y\nTransfer-Encoding: chunked" etc
            # Our python split logic above is simple.
            # If line.lower().startswith("transfer-encoding:") triggered, we block.
            if te_found:
                 client_sock.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\nSmuggling Attempt Detected")
                 client_sock.close()
                 return
            # If bypassed (e.g. space before colon), te_found is False.
            # We proceed (Default to CL because TE not found by us)
            # Backend acts as 'te.te' (Lax) -> will find the TE.
        
        # Read Body based on PROXY RULES
        # 8001 (CL.TE): TRUST CL. IGNORE TE.
        # 8002 (TE.CL): TRUST TE. IGNORE CL.
        # 8003 (TE.TE): TRUST CL (Because WAF didn't find TE).
        
        body = body_start
        
        # 8002: If TE is present (even if obfuscated potentially? No 8002 is Standard Lax)
        # Actually 8002 should just support TE if present.
        
        should_use_te = False
        if mode == 'te.cl':
             # Check broadly for TE
             if "transfer-encoding" in headers_str.lower():
                 should_use_te = True
        
        if should_use_te:
             # Read until we find the end of chunked body (0\r\n\r\n)
             # Naive check is sufficient for this lab
             while not body.endswith(b"\r\n0\r\n\r\n") and not body.startswith(b"0\r\n\r\n"):
                 chunk = client_sock.recv(4096)
                 if not chunk: break
                 body += chunk 
        else:
             # Use CL
             while len(body) < cl_val:
                 chunk = client_sock.recv(4096)
                 if not chunk: break
                 body += chunk
             body = body[:cl_val] # TRUNCATE to CL! Crucial for CL.TE logic
             
        # Construct Request to Backend
        final_req = "\r\n".join(new_headers).encode() + b"\r\n\r\n" + body
        
        # Forward
        resp = forward_to_backend(final_req)
        
        client_sock.sendall(resp)
        
    except Exception as e:
        print(f"Proxy Error: {e}")
    finally:
        client_sock.close()

def start_server(port, mode):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', port))
    s.listen(50)
    print(f"Frontend listening on {port} ({mode})")
    
    # Pre-connect to backend?
    # get_backend_sock() will handle it.
    
    while True:
        c, a = s.accept()
        threading.Thread(target=handle_client, args=(c, mode)).start()

if __name__ == "__main__":
    import os
    # Default to CL.TE if not set
    mode = os.environ.get('CHALLENGE_MODE', 'CL.TE').lower()
    
    # Normalize mode string
    if mode not in ['cl.te', 'te.cl', 'te.te']:
        print(f"Invalid Mode: {mode}. Defaulting to cl.te")
        mode = 'cl.te'
        
    print(f"Starting Single-Mode Frontend: {mode.upper()}")
    
    # Start on Port 80 (Internal Docker Port, mapped to 3000 host)
    start_server(80, mode)
