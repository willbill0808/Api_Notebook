# Notes app

En enkel notat-app som bruker et GUI for å lage og administrere notater. Serveren lagrer notater i en SQLite-database og gir tilgang til notatene via en HTTP API.

---
## Dependensies

Før du kan kjøre prosjektet, trenger du følgende:

* Python 3.14 eller nyere (kan lastes ned fra [python.org](https://www.python.org/downloads/))
* Pakkene:

  * `FreeSimpleGUI`
  * `requests`
  * `sqlite3` (følger med Python)

Først må du lage og gå inn i et venv (virtuelt enviornement)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Installer avhengigheter med `pip`:

```bash
pip install FreeSimpleGUI requests
```

### Teknologier

* **Python 3.14+** for all logic
* **FreeSimpleGUI** for GUI
* **SQLite** for lagring
* **Requests** for HTTP-kommunikasjon
* **JSON** for datautveksling mellom klient og server

---

## Bruk av appen

På maskinen du vil bruke på serveren må du ha server_final.py
Pass på at du har lastet ned alle Dependensies

Gå inn i det virtuele enviornementet
```bash
source .venv/bin/activate
```
Også kjør server koden
```bash
python3 server_final.py
```

~~

På klienmaskinen må du ha applet_final.py
Pass på at du har lastet ned alle Dependensies

Gå inn i det virtuele enviornementet
```bash
source .venv/bin/activate
```
Også kjør klient koden
```bash
python3 applet_final.py
```
**Merk at appen krasjer om serveren ikke kjører**


Bruk av Guien fungerer som følgende:
* **Legg til notater**: Klikk på "Make a new tab" for å lage et nytt notat. Skriv inn en tittel for notatet og det vil bli lagret på serveren.
* **Lag todo-lister**: Klikk på "Make a new to-do tab" for å lage en todo-liste. Du kan legge til oppgaver og markere dem som fullførte.
* **Oppdater notater**: Etter å ha gjort endringer, trykk på "Update" for å lagre endringene tilbake til serveren.
* **Slett notater**: Klikk på "Delete" for å fjerne et notat eller todo-liste fra serveren.

### Konfigurasjon av server IP og port

Du kan endre hvor serveren lytter etter HTTP-forespørsler ved å justere serverinnstillingene i `server2.py`.

* **Endre IP-adresse**:
  Hvis du ønsker at serveren bare skal lytte på lokale forespørsler fra samme maskin (localhost), kan du endre serverens IP til `localhost` i koden:

  ```python
  server = HTTPServer(("localhost", 8000), Handler)
  ```

  Hvis du vil at serveren skal kunne nås fra andre maskiner på nettverket ditt, kan du endre IP-en til `0.0.0.0`, som lytter på alle tilgjengelige nettverksgrensesnitt:

  ```python
  server = HTTPServer(("0.0.0.0", 8000), Handler)
  ```

* **Endre port**:
  Hvis du ønsker å bruke en annen port, kan du endre portnummeret i samme linje:

  ```python
  server = HTTPServer(("0.0.0.0", 8000), Handler)  # Bytt ut 8000 med ønsket port
  ```

* **Endre IP/port i klienten**:
  Pass på at klienten (`applet_final.py`) også er konfigurert til å kommunisere med riktig serveradresse. Juster `ip` og `port` i klientkoden:

  ```python
  ip = "193.69.217.172"  # Bytt til serverens IP
  port = 8000             # Bytt til serverens portnummer
  ```

  Hvis du prøver å koble til serveren over WAN, må du sette opp port-forwarding på ruteren.


---

## Funksjoner

* **GUI-basert app** for å opprette og redigere notater.
* **Server-backend** som bruker SQLite for lagring av notater.
* Mulighet for å lage både vanlige **notater** og **todo-lister**.
* Mulighet for å oppdatere innhold, samt lagre todo-elementer med avkrysningsbokser.

---

## To-do / Videreutvikling

* **Brukergodkjenning**: Legg til mulighet for at brukere kan logge inn med et brukernavn og passord.
* **Passordhashing**: Implementer sikker passordlagring med hashing (f.eks. bcrypt).
* **Automatisk lagring**: Lagre endringer automatisk uten å måtte trykke på "Update"-knappen for standar notatfelt.
* **Bytte til MariaDB**: Bytte fra SQLite3 til mariaDB for bedre skalering.
* **Responsiv design**: Forbedre GUI-en for å gjøre den mer responsiv og brukervennlig på forskjellige skjermstørrelser.
* **Grafisk design**: Forbedre GUI-en sinn visuel stil.

---

# Notes App



## Funksjoner



---