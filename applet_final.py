import FreeSimpleGUI as sg  # GUI library for building windows and controls
import requests, json       # requests for HTTP communication, json for parsing

# User information (currently hardcoded)
user = "test"
user_id = 1

# Server connection details
ip = "193.69.217.172"
port = 8000
headers = {"X-API-Key": "mysecret123"}


def tabLoader():
    """
    Loads existing notes from the server and creates tabs for the GUI.
    
    Returns:
        tabs (list): List of sg.Tab objects for the TabGroup
        tab_data (dict): Mapping of tab titles to note metadata (id and key)
        rows (list): Raw note rows returned from the server
    """
    tabs = []

    # Add the menu tab where the user can create a new note
    tabs.append(
        sg.Tab(
            "menu",
            [[sg.Text('What do you want your new note space to be called:')],
             [sg.Input(key='-INPUT-'), sg.Button("Make new tab", key="-Make_tab-")]]
        )
    )

    # Fetch notes from the server
    r = requests.get(f"http://{ip}:{port}/notes", headers=headers)  
    rows = r.json()["data"]  # Extract note data from server response

    tab_data = {}  # Dictionary to map tab titles to their note ID and GUI key

    # Create a tab for each note returned from the server
    for row in rows:
        note_id = row[0]        # ID of the note in the database
        title = row[2]          # Note title
        content = row[3]        # Note content
        key = f"-ML-{note_id}"  # Unique key for the Multiline input field

        # Add the tab with a multiline box containing the note content
        tabs.append(
            sg.Tab(title, [[sg.Multiline(key=key, default_text=content, size=(120,20))], [sg.Button("Delete", key=f"-Delete-{note_id}-")]])
        )

        # Save mapping of title to note metadata for easy updates later
        tab_data[title] = {"id": note_id, "key": key}

    return tabs, tab_data, rows

# Load tabs and data from server at startup
tabs, tab_data, original_content = tabLoader()

# Define the GUI layout with tabs and control buttons
layout = [
    [sg.TabGroup([tabs])],  # TabGroup containing all tabs
    [sg.Button("Update", key="-Update-"), sg.Button("Quit", key="-Exit-")]  # Control buttons
]

# Create the main window
window = sg.Window('Notes App', layout, size=(900,500), resizable=True, finalize=True)

# Event loop for GUI
while True:
    event, values = window.read()  # Read user actions and input values

    # Exit the program if window is closed or "Quit" button is pressed
    if event in (sg.WIN_CLOSED, "-Exit-"):
        break
    
    # Event triggered when user creates a new tab/note
    if event == "-Make_tab-":
        # Send the new note title to the server
        r = requests.post(f"http://{ip}:{port}/make-note", headers=headers, json=values["-INPUT-"])
        print(r.json())  # Print server response

        # Close current window to reload with new tab
        window.close()

        # Reload all tabs from the server including the new note
        tabs, tab_data, original_content = tabLoader()

        # Rebuild the layout with the updated tabs
        layout = [
            [sg.TabGroup([tabs])],
            [sg.Button("Update", key="-Update-"), sg.Button("Quit", key="-Exit-")]
        ]

        # Recreate the window with updated tabs
        window = sg.Window('Notes App', layout, size=(900,500), resizable=True, finalize=True)

    # Event triggered when user wants to update existing notes
    if event == "-Update-":
        notes_to_send = []

        # Prepare note data to send to server
        for title, info in tab_data.items():
            note_id = info['id']
            key = info['key']
            content = values.get(key, "")  # Get current content from the Multiline field

            notes_to_send.append({
                "id": note_id,
                "title": title,
                "content": content
            })

        # Send updated notes to server
        r = requests.post(f"http://{ip}:{port}/update", headers=headers, json=notes_to_send)
        print(r.json())  # Print server response
    
    if event.startswith("-Delete-"):

        note_id = int(event.replace("-Delete-", "").replace("-", ""))

        r = requests.post(f"http://{ip}:{port}/delete-tab", headers=headers, json=note_id)
        print(r.json())  # Print server response

        # Close current window to reload with new tab
        window.close()

        # Reload all tabs from the server including the new note
        tabs, tab_data, original_content = tabLoader()

        # Rebuild the layout with the updated tabs
        layout = [
            [sg.TabGroup([tabs])],
            [sg.Button("Update", key="-Update-"), sg.Button("Quit", key="-Exit-")]
        ]

        # Recreate the window with updated tabs
        window = sg.Window('Notes App', layout, size=(900,500), resizable=True, finalize=True)




# Close the window when exiting the loop
window.close()