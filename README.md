# Request Smuggling Lab

Ce laboratoire est conçu pour pratiquer les attaques de HTTP Request Smuggling (CL.TE, TE.CL, TE.TE). Il simule une architecture vulnérable composée d'un Frontend (Load Balancer/Proxy) et d'un Backend, avec un Bot simulant une victime administrative.

## Installation & Lancement

### 1. Installation
Clonez ce dépôt :
```bash
git clone <votre-repo-url>
cd request-smuggling-lab
```

### 2. Lancement (Windows PowerShell)

Le laboratoire supporte 3 modes de challenge. Vous pouvez basculer entre eux en utilisant la variable d'environnement `$env:CHALLENGE_MODE`.

**Mode CL.TE (Par défaut)**
Frontend utilise `Content-Length`, Backend utilise `Transfer-Encoding`.
```powershell
docker compose up -d --build
```

**Mode TE.CL**
Frontend utilise `Transfer-Encoding`, Backend utilise `Content-Length`.
```powershell
$env:CHALLENGE_MODE='TE.CL'; docker compose up -d --build
```

**Mode TE.TE**
Les deux supportent `Transfer-Encoding`, mais l'un peut être obfusqué.
```powershell
$env:CHALLENGE_MODE='TE.TE'; docker compose up -d --build
```

> **Note :** Pour arrêter le lab proprement entre deux changements de mode, utilisez :
> ```powershell
> docker compose down
> ```

## Exploitation

Des scripts Python sont fournis pour automatiser l'envoi des exploits. Ces scripts sont compatibles Windows/Linux/MacOS et gèrent correctement le formatage des requêtes.

1.  **Lancer l'exploit correspondant au mode actif :**
    ```bash
    # Pour CL.TE
    python exploit_cl_te.py

    # Pour TE.CL
    python exploit_te_cl.py

    # Pour TE.TE
    python exploit_te_te.py
    ```

2.  **Vérifier le résultat :**
    Ouvrez votre navigateur sur le tableau de bord IDS pour voir les requêtes capturées (et le cookie Admin volé) :
    [http://localhost:3000/ids/dashboard](http://localhost:3000/ids/dashboard)

## Architecture

*   **Frontend (Port 3000)** : Proxy inverse qui transmet les requêtes au backend. Vulnérable ou non au parsing TE selon le mode.
*   **Backend (Port 8888)** : Serveur d'application qui traite les requêtes.
*   **Bot** : Script simulant un administrateur visitant le site régulièrement avec un cookie sensible.
*   **IDS Dashboard** : Interface pour visualiser les tentatives de request smuggling réussies.

## Prérequis

*   Docker & Docker Compose
*   Python 3.x (pour lancer les scripts d'exploit)