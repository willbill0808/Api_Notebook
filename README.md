# Notes App

En notat-app med GUI og server-backend som lagrer notater i en SQLite database.

---

## Avhengigheter

For å kjøre prosjektet trenger du:

- Python 3.14 eller nyere
- Pakkene:
  - `FreeSimpleGUI`
  - `requests`
  - `sqlite3` (følger med Python)

Installer avhengigheter med pip:

``` bash
pip install FreeSimpleGUI requests
```

---

## Oppsett

1. **Klone prosjektet**:

```bash
git clone https://github.com/willbill0808/Api_Notebook.git
cd Api_Notebook
```

2. **Opprette og aktivere virtuell miljø (anbefalt)**:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux
```

3. **Start serveren**:

på maskinen som du vil kjøre server-siden på så skriver du inn i terminalen:

```bash
python3 server2.py
```

Serveren kjører nå på: `http://localhost:8000`

```python
server = HTTPServer(("0.0.0.0", 8000), Handler)
```
Denne linjen styrer hvor du vil at serveren skal høre etter requests
Om du endrer "0.0.0.0" til "localhost" kommer den bare til å ta i mot forespørseler fra datamaskinen som kjører serveren
Om du endrer 8000 til et annet tall så bytter du port den hører på(hver obs på at du må endre dette i applet koden også)

4. **Start klienten**:

```bash
python3 client.py
```

GUI vil hente eksisterende notater fra serveren og tillate oppretting og oppdatering av nye notater.

```python
# Server connection details
ip = "193.69.217.172"
port = 8000
```
disse variablene styrer hvor den leter etter en server
Endre Ip til server maskinen sin ip (om du prøver å koble til den over wan så må du sette opp port-forwarding)
Endre port til hvilken port serveren er satt til å lete på, om disse ikke stemmer kommer ikke serveren å se requesten.

---

## TODO / Videreutvikling

* [ ] Legge til brukergodkjenning og passordhashing
* [ ] Forbedre GUI med mulighet for å slette notater
* [ ] Lagring av endringer automatisk uten å trykke "Update"
* [ ] Bytte over til mariaDB for bedre skalering
