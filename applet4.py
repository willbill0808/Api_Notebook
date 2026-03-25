import FreeSimpleGUI as sg
import requests, json 
user = "test"
user_id = 1

ip = "193.69.217.172"
port = 8000

def tabLoader():
    tabs = []

    # Menu tab
    tabs.append(
        sg.Tab(
            "menu",
            [[sg.Text('What do you want your new note space to be called:')],
             [sg.Input(key='-INPUT-'), sg.Button("Make new tab", key="-Make_tab-")]]
        )
    )

    # Load notes from server
    r = requests.get(f"http://{ip}:{port}/notes")  
    rows = r.json()["data"]

    tab_data = {}

    for row in rows:
        note_id = row[0]
        title = row[2]
        content = row[3]
        key = f"-ML-{note_id}"  # unique key for this tab's multiline

        # Add tab to GUI
        tabs.append(
            sg.Tab(title, [[sg.Multiline(key=key, default_text=content, size=(120,20))]])
        )

        # Save mapping
        tab_data[title] = {"id": note_id, "key": key}

    return tabs, tab_data, rows

tabs, tab_data, original_content = tabLoader()

layout = [
    [sg.TabGroup([tabs])],
    [sg.Button("Update", key="-Update-"), sg.Button("Quit", key="-Exit-")]
]

window = sg.Window('Notes App', layout, size=(900,500), resizable=True, finalize=True)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "-Exit-"):
        break
    
    if event == "-Make_tab-":
        r = requests.post(f"http://{ip}:{port}/make-note", json=values["-INPUT-"])
        print(r.json())

        window.close()

        tabs, tab_data, original_content = tabLoader()

        layout = [
            [sg.TabGroup([tabs])],
            [sg.Button("Update", key="-Update-"), sg.Button("Quit", key="-Exit-")]
        ]

        window = sg.Window('Notes App', layout, size=(900,500), resizable=True, finalize=True)


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

        r = requests.post(f"http://{ip}:{port}/update", json=notes_to_send)
        print(r.json())

window.close()

