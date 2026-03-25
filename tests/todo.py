import FreeSimpleGUI as sg  # GUI library

# Initial layout
layout = [
    [sg.Checkbox('My first Checkbox!', default=True),
     sg.Checkbox('My second Checkbox!'),
     sg.Checkbox('Disabled Checkbox!', disabled=True)],

    [sg.Input(key="-NEW-"), sg.Button("Add")],  # input + add button
    [sg.Button("Quit", key="-Exit-")]
]

window = sg.Window('Todo App', layout, size=(900,500), resizable=True, finalize=True)

# Event loop
while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, "-Exit-"):
        break

    # ➕ Add new checkbox
    if event == "Add":
        text = values["-NEW-"]

        if text:  # only add if not empty
            # Add new checkbox to window
            window.extend_layout(window, [[sg.Checkbox(text)]])
            
            # Clear input field
            window["-NEW-"].update("")

# Close window
window.close()