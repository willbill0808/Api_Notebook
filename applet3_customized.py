import FreeSimpleGUI as sg
import sqlite3

# --- Database ---
server = sqlite3.connect('server.db')   
c = server.cursor()

# --- Theme ---
sg.theme("DarkGrey14")  # More modern than default

# Global font settings
MAIN_FONT = ("Segoe UI", 11)
TITLE_FONT = ("Segoe UI", 18, "bold")
TAB_FONT = ("Segoe UI", 11, "bold")

# --- Functions ---
def tabLoader():
    tabs = []

    # --- New Note Tab ---
    new_tab_layout = [
        [sg.Text('Create a new note', font=("Segoe UI", 13, "bold"))],
        [sg.Text('Title:', font=MAIN_FONT), sg.Input(key='-INPUT-', size=(25,1), font=MAIN_FONT)],
        [sg.Button("Create", key="-Make_tab-", size=(12,1), button_color=("#FFFFFF", "#4a90e2"))]
    ]

    tabs.append(sg.Tab("＋ New", new_tab_layout, font=TAB_FONT))

    # --- Load Notes ---
    c.execute("SELECT * FROM notes")   
    rows = c.fetchall()

    for row in rows:
        tabs.append(
            sg.Tab(
                row[2],  # Title
                [[sg.Multiline(
                    default_text=row[3],
                    size=(90, 20),
                    key=f'-ML-{row[0]}',
                    font=MAIN_FONT,
                    expand_x=True,
                    expand_y=True,
                    border_width=0
                )]],
                font=TAB_FONT
            )
        )

    return tabs

def makeTab(title):
    if not title.strip():
        sg.popup("Please enter a title.")
        return
    
    c.execute("INSERT INTO notes (user_id, title, content) VALUES (?, ?, ?)",
              (1, title, ""))
    server.commit()

    refresh_tabs()

def refresh_tabs():
    window['-TABS-'].update(tabLoader())

# --- Layout ---
layout = [
    [sg.Text("My Notes", font=TITLE_FONT, pad=(10,15))],

    [sg.TabGroup(
        [tabLoader()],
        key='-TABS-',
        expand_x=True,
        expand_y=True,
        tab_location='topleft'
    )],

    [sg.Push(), sg.Button("Exit", key="-Exit-", size=(10,1), button_color=("#FFFFFF", "#d9534f"))]
]

# --- Window ---
window = sg.Window(
    'Notes App',
    layout,
    size=(900, 500),
    resizable=True,
    finalize=True,
    font=MAIN_FONT
)

# --- Event Loop ---
while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, '-Exit-'):
        break

    if event == "-Make_tab-":
        makeTab(values['-INPUT-'])

window.close()