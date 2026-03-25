import FreeSimpleGUI as sg
import requests, json 
user = "test"
user_id = 1

def tabLoader():

    tabs = [sg.Tab("menu", [[sg.Text('What do you want you new note space to be called:')], [sg.Input(key='-INPUT-'), sg.Button("Make new tab", key=("-Make_tab-"))]])]

    print("hi")

    r = requests.get("http://193.69.217.172:8000/notes")  
    print(r.json())

    rows = r.json()["data"]

    for row in rows:
        print(row)
        tabs.append(sg.Tab(row[2], [[sg.Multiline(key=f'-ML-', default_text=row[3], write_only=True, size=(120,20))]]))
    return tabs

def makeTab(Tittle):
    print(Tittle)

layout = [
    [sg.Text("Tittle")],
    [sg.TabGroup([tabLoader()])],
    [sg.Button("Quit", key="-Exit-")]
    ]

window = sg.Window(
    'Notes App',
    layout,
    size=(900, 500),
    resizable=True,
    finalize=True
)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == '-Exit-':
        break
    if event =="-Make_tab-":
        makeTab(values['-INPUT-'])

window.close()

