import FreeSimpleGUI as sg
import requests, json 

def tabMaker2(tabCount):

    tabs = [sg.Tab("menu", [[sg.Button("Make new tab", key=("-Make_tab-"))]])]

    for i in range(tabCount):
        tabs.append(sg.Tab(f"Tab{i +1 }", [[sg.Multiline(key='-ML-', write_only=True, size=(60,10))]]))
    
    return tabs

real_tabs = tabMaker2(2)

layout = [
    [sg.Text("Tittle")],
    [sg.TabGroup([real_tabs])],
    [sg.Button("Quit", key="-Exit-")]
    ]

window = sg.Window('Multiline Example', layout, finalize=True)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == '-Exit-':
        break

window.close()