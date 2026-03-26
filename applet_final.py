import FreeSimpleGUI as sg  # GUI-bibliotek for å lage vinduer og kontroller
import requests, json       # requests for HTTP-kall, json for parsing av data

# Brukerinformasjon (hardkodet foreløpig)
user = "test"
user_id = 1

# Server-tilkobling
ip = "192.168.20.169"
port = 8000
headers = {"X-API-Key": "mysecret123"}


def tabLoader():
    """
    Henter eksisterende notater fra serveren og lager faner (tabs) i GUI-et.

    Returnerer:
        tabs (list): Liste med sg.Tab-objekter
        tab_data (dict): Kobler fanenavn til note-ID og GUI-key
        rows (list): Rådata fra serveren
    """
    tabs = []

    # Meny-fane for å opprette nye notater eller todo-lister
    tabs.append(
        sg.Tab(
            "menu",
            [[sg.Text('Hva vil du kalle den nye notatfanen din?')],
             [sg.Input(key='-INPUT-note-'), sg.Button("Lag ny notatfane", key="-Make_note-")],
             [sg.Input(key='-INPUT-todo-'), sg.Button("Lag ny todo-fane", key="-Make_todo-")]]
        )
    )

    # Hent alle notater fra server
    r = requests.get(f"http://{ip}:{port}/notes", headers=headers)  
    rows = r.json()["data"]

    tab_data = {}  # Holder oversikt over note-id og GUI-key

    # Lag en fane for hvert notat
    for row in rows:
        note_id = row[0]        # ID i databasen
        title = row[2]          # Navn på notatet
        content = row[3]        # Innhold
        key = f"-ML-{note_id}"  # Unik key til Multiline-feltet
        note_type = row[4]      # "note" eller "todo"

        if note_type == "note":
            # Vanlig tekstnotat
            tabs.append(
                sg.Tab(title, [
                    [sg.Multiline(key=key, default_text=content, size=(120,20))], 
                    [sg.Button("Slett", key=f"-Delete-{note_id}-"), sg.Text(f"type: {note_type}")]
                ])
            )

            # Lagre kobling for senere oppdatering
            tab_data[title] = {"id": note_id, "key": key}
        
        if note_type == "todo":
            # Todo-liste med inputfelt for nye oppgaver
            checkbox_tabs = [
                [sg.Input(key=f'-INPUT-checkbox-{title}-'), 
                 sg.Button("Legg til checkbox", key=f"-Make_checkbox-{title}-")]
            ]
            
            # Konverter JSON-string til liste
            try:
                todo_items = json.loads(content)
            except Exception:
                todo_items = []

            # Lag checkboxes for hver oppgave
            for i, item in enumerate(todo_items):
                checkbox_tabs.append([
                    sg.Checkbox(
                        item["title"], 
                        default=item.get("complete", False), 
                        key=f"-CB-{note_id}-{i}-", 
                        enable_events=True  # gjør at klikk trigger event
                    )
                ])

            # Slett-knapp nederst
            checkbox_tabs.append([
                sg.Button("Slett", key=f"-Delete-{note_id}-"), 
                sg.Text(f"type: {note_type}")
            ])

            tabs.append(sg.Tab(title, checkbox_tabs))

    return tabs, tab_data, rows


# Last inn data ved oppstart
tabs, tab_data, original_content = tabLoader()

# GUI-layout
layout = [
    [sg.TabGroup([tabs])],
    [sg.Button("Oppdater", key="-Update-"), sg.Button("Avslutt", key="-Exit-")]
]

# Opprett vindu
window = sg.Window('Notat-app', layout, size=(900,500), resizable=True, finalize=True)

# Hoved-loop
while True:
    event, values = window.read()

    print(f"Siste event: {event}")

    # Avslutt programmet
    if event in (sg.WIN_CLOSED, "-Exit-"):
        break
    
    # Lag nytt notat
    if event == "-Make_note-":
        r = requests.post(f"http://{ip}:{port}/make-note", headers=headers, json=values["-INPUT-note-"])
        print(r.json())

        # Reload GUI (enkelt men ikke optimalt)
        window.close()
        tabs, tab_data, original_content = tabLoader()

        layout = [
            [sg.TabGroup([tabs])],
            [sg.Button("Oppdater", key="-Update-"), sg.Button("Avslutt", key="-Exit-")]
        ]

        window = sg.Window('Notat-app', layout, size=(900,500), resizable=True, finalize=True)

    # Lag ny todo-liste
    if event == "-Make_todo-":
        r = requests.post(f"http://{ip}:{port}/make-todo", headers=headers, json=values["-INPUT-todo-"])
        print(r.json())

        # Reload GUI
        window.close()
        tabs, tab_data, original_content = tabLoader()

        layout = [
            [sg.TabGroup([tabs])],
            [sg.Button("Oppdater", key="-Update-"), sg.Button("Avslutt", key="-Exit-")]
        ]

        window = sg.Window('Notat-app', layout, size=(900,500), resizable=True, finalize=True)
    
    # Legg til checkbox i todo
    if event.startswith("-Make_checkbox-"):
        todo_name = event.replace("-Make_checkbox-", "")[:-1]

        todo_box = [todo_name, values[f"-INPUT-checkbox-{todo_name}-"], False]

        r = requests.post(f"http://{ip}:{port}/add-todo", headers=headers, json=todo_box)
        print(r.json())

        # Reload GUI
        window.close()
        tabs, tab_data, original_content = tabLoader()

        layout = [
            [sg.TabGroup([tabs])],
            [sg.Button("Oppdater", key="-Update-"), sg.Button("Avslutt", key="-Exit-")]
        ]

        window = sg.Window('Notat-app', layout, size=(900,500), resizable=True, finalize=True)

    # Checkbox endret
    if event.startswith("-CB-"):
        parts = event.split('-')
        note_id = int(parts[2])
        cb_index = int(parts[3])
        new_state = values[event]

        payload = [note_id, cb_index, new_state]
        r = requests.post(f"http://{ip}:{port}/update-CB", headers=headers, json=payload)
        print(r.json())

    # Oppdater tekstnotater
    if event == "-Update-":
        notes_to_send = []

        for title, info in tab_data.items():
            note_id = info['id']
            key = info['key']
            content = values.get(key, "")

            notes_to_send.append({
                "id": note_id,
                "title": title,
                "content": content
            })

        r = requests.post(f"http://{ip}:{port}/update", headers=headers, json=notes_to_send)
        print(r.json())
    
    # Slett notat
    if event.startswith("-Delete-"):
        note_id = int(event.replace("-Delete-", "").replace("-", ""))

        r = requests.post(f"http://{ip}:{port}/delete-tab", headers=headers, json=note_id)
        print(r.json())

        # Reload GUI
        window.close()
        tabs, tab_data, original_content = tabLoader()

        layout = [
            [sg.TabGroup([tabs])],
            [sg.Button("Oppdater", key="-Update-"), sg.Button("Avslutt", key="-Exit-")]
        ]

        window = sg.Window('Notat-app', layout, size=(900,500), resizable=True, finalize=True)

# Lukk vindu
window.close()