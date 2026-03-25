import FreeSimpleGUI as sg
import requests, json 

def tabMaker2(tabCount):

    tabs = [sg.Tab("menu", [[sg.Button("Make new tab", key=("-Make_tab-"))]])]
    for i in range(tabCount):
        newTab = [sg.Tab(f"Tab{i}", [sg.Multiline(key='-ML-', write_only=True, size=(60,10))])]
        tabs.append(newTab)
    
    return tabs

    

def tabMaker():
    Form = [
        [sg.Multiline(key='-ML-', write_only=True, size=(60,10))]
        ]
    return Form

tab_layout1 = [
    [sg.Text("Tab Maker")], 
    [sg.Button("Make new tab")]
    ]

real_tabs = tabMaker2(2)
tabs = [sg.Tab("tabOne", tab_layout1), sg.Tab("tabTwo", tabMaker())]

layout = [
    [sg.Text("Tittle")],
    [sg.TabGroup([real_tabs])],
    [sg.Button("Quit", key="-Exit-", )]
    ]


window = sg.Window('Multiline Example', layout, finalize=True)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == '-Exit-':
        break

window.close()