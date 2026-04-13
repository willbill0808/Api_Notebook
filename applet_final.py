import FreeSimpleGUI as sg  # GUI library for creating windows and controls
import requests, json, os   # requests for HTTP calls, json for parsing data


headers = {"X-API-Key": "mysecret123"}


CONFIG_FILE = "applet_config.txt"

def save_config(ip=None, port=None, username=None, user_id=None):
    config = load_config() or {}

    if ip is not None:
        config["ip"] = ip
    if port is not None:
        config["port"] = port
    if username is not None:
        config["username"] = username
    if user_id is not None:
        config["user_id"] = user_id

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        default = {
            "ip": "192.168.20.88",
            "port": 8000,
            "username": "Guest",
            "user_id": 0
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(default, f, indent=4)
        return default

    with open(CONFIG_FILE) as f:
        return json.load(f)

def tabLoader():
    config = load_config()

    """
    Fetches existing notes from the server and creates tabs in the GUI.

    Returns:
        tabs (list): List of sg.Tab objects
        tab_data (dict): Maps tab names to note ID and GUI key
        rows (list): Raw data from the server
    """
    tabs = []

    # Menu tab for creating new notes or todo lists
    tabs.append(
        sg.Tab(
            "Menu",
            [[sg.Text('What do you want to call your note tab')],
             [sg.Input(key='-INPUT-note-'), sg.Button("Make a new note", key="-Make_note-")],
             [sg.Input(key='-INPUT-todo-'), sg.Button("Make a new to-do list", key="-Make_todo-")],
             [sg.Text("login")],
             [sg.Input(key='-INPUT-user-', default_text=config["username"]), sg.Text("What is your username")],
             [sg.Input(key='-INPUT-password-'), sg.Text("What is your password")],
             [sg.Button("login", key="-login-")],
             [sg.Text("Create user")],
             [sg.Input(key='-INPUT-user-new-'), sg.Text("What do you want your username to be")],
             [sg.Input(key='-INPUT-password-new-'), sg.Text("What do you want your password to be")],
             [sg.Input(key='-INPUT-password-new_2-'), sg.Text("Confirm password")],
             [sg.Button("Create user", key="-create_user-")],
             [sg.Text("Server settings")],
             [sg.Input(key='-INPUT-IP-', default_text=config["ip"]), sg.Text("What is the ip of your preferred server")],
             [sg.Input(key='-INPUT-port-', default_text=config["port"]), sg.Text("What is the port of your preferred server")],
             [sg.Button("Update preferences", key="-change_server-")],
             ]
        )
    )

    if config["user_id"] == 0:
        return tabs, None, None

    # Fetch all notes from the server
    r = requests.post(f"http://{config["ip"]}:{config["port"]}/notes", headers=headers, json=config["user_id"])  

    rows = r.json()["data"]

    tab_data = {}  # Keeps track of note id and GUI key

    # Create a tab for each note
    for row in rows:
        note_id = row[0]        # ID in the database
        title = row[2]          # Note title
        content = row[3]        # Content
        key = f"-ML-{note_id}"  # Unique key for the Multiline field
        note_type = row[4]      # "note" or "todo"

        if note_type == "note":
            # Regular text note
            tabs.append(
                sg.Tab(title, [
                    [sg.Multiline(key=key, default_text=content, size=(120,20))], 
                    [sg.Button("Delete", key=f"-Delete-{note_id}-"), sg.Text(f"type: {note_type}")]
                ])
            )

            # Store mapping for later updates
            tab_data[title] = {"id": note_id, "key": key}
        
        if note_type == "todo":
            # Todo list with input field for new tasks
            checkbox_tabs = [
                [sg.Input(key=f'-INPUT-checkbox-{title}-'), 
                 sg.Button("Add checkbox", key=f"-Make_checkbox-{title}-")]
            ]
            
            # Convert JSON string to list
            try:
                todo_items = json.loads(content)
            except Exception:
                todo_items = []

            # Create checkboxes for each task
            for i, item in enumerate(todo_items):
                checkbox_tabs.append([
                    sg.Checkbox(
                        item["title"], 
                        default=item.get("complete", False), 
                        key=f"-CB-{note_id}-{i}-", 
                        enable_events=True  # makes clicks trigger events
                    )
                ])

            # Delete button at the bottom
            checkbox_tabs.append([
                sg.Button("Delete", key=f"-Delete-{note_id}-"), 
                sg.Text(f"type: {note_type}")
            ])

            tabs.append(sg.Tab(title, checkbox_tabs))

    return tabs, tab_data, rows

def reload(window):
    window.close()
    tabs, tab_data, original_content = tabLoader()

    layout = [
        [sg.TabGroup([tabs])],
        [sg.Button("Update", key="-Update-"), sg.Button("Quit", key="-Exit-")]
    ]

    return sg.Window('Notat-app', layout, size=(900,500), resizable=True, finalize=True)


def login(username, password):
    print(username)
    print(password)

    r = requests.post(f"http://{config["ip"]}:{config["port"]}/login", headers=headers, json=username)
    rows = r.json()["data"]
    print(rows)

    if username == rows[0][1] and password == rows[0][2]:
        save_config(username=rows[0][1], user_id=rows[0][0])
        return
    else:
        return "wrong username or password"

def create_user(username, password, password2):
    print(username)
    print(password)
    print(password2)

    if password != password2:
        return "passwords don't match"

    r = requests.post(f"http://{config["ip"]}:{config["port"]}/create_user", headers=headers, json=[username, password, password2])

# Load data on startup
tabs, tab_data, original_content = tabLoader()

# GUI layout
layout = [
    [sg.TabGroup([tabs])],
    [sg.Button("Update", key="-Update-"), sg.Button("Quit", key="-Exit-")]
]

# Create window
window = sg.Window('Notat-app', layout, size=(900,500), resizable=True, finalize=True)

# Main loop
while True:
    event, values = window.read()

    config = load_config()

    print(f"Latest event: {event}")

    # Exit the program
    if event in (sg.WIN_CLOSED, "-Exit-"):
        break
    
    # Create new note
    if event == "-Make_note-":
        r = requests.post(f"http://{config["ip"]}:{config["port"]}/make-note", headers=headers, json=[values["-INPUT-note-"], config["user_id"]])
        window = reload(window)

    # Create new todo list
    if event == "-Make_todo-":
        r = requests.post(f"http://{config["ip"]}:{config["port"]}/make-todo", headers=headers, json=[values["-INPUT-todo-"], config["user_id"]])
        window = reload(window)
    
    # Add checkbox to todo
    if event.startswith("-Make_checkbox-"):
        todo_name = event.replace("-Make_checkbox-", "")[:-1]

        todo_box = [todo_name, values[f"-INPUT-checkbox-{todo_name}-"], False]

        r = requests.post(f"http://{config["ip"]}:{config["port"]}/add-todo", headers=headers, json=todo_box)
        print(r.json())

        window = reload(window)

    # Checkbox changed
    if event.startswith("-CB-"):
        parts = event.split('-')
        note_id = int(parts[2])
        cb_index = int(parts[3])
        new_state = values[event]

        payload = [note_id, cb_index, new_state]
        r = requests.post(f"http://{config["ip"]}:{config["port"]}/update-CB", headers=headers, json=payload)
        print(r.json())

    # Update text notes
    if event == "-Update-":
        notes_to_send = []

        if tab_data:
            for title, info in tab_data.items():
                note_id = info['id']
                key = info['key']
                content = values.get(key, "")

                notes_to_send.append({
                    "id": note_id,
                    "title": title,
                    "content": content
                })

            r = requests.post(f"http://{config["ip"]}:{config["port"]}/update", headers=headers, json=notes_to_send)
            print(r.json())
    
    # Delete note
    if event.startswith("-Delete-"):
        note_id = int(event.replace("-Delete-", "").replace("-", ""))

        r = requests.post(f"http://{config["ip"]}:{config["port"]}/delete-tab", headers=headers, json=note_id)
        print(r.json())

        window = reload(window)

    if event == "-login-":
        auth = login(values["-INPUT-user-"], values["-INPUT-password-"])
        print(auth)

        window = reload(window)

    if event == "-create_user-":
        auth = create_user(values["-INPUT-user-new-"], values["-INPUT-password-new-"], values["-INPUT-password-new_2-"])
        print(auth)
    
    if event == "-change_server-":
        save_config(ip=values["-INPUT-IP-"], port=values["-INPUT-port-"])
        
        window = reload(window)

# Close window
window.close()
