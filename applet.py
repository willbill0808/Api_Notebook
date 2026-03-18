import FreeSimpleGUI as sg
import requests, json 

def tabMaker(Tittle):
    Form = [sg.Text(Tittle), sg.Multiline(key='-ML-', write_only=True, size=(60,10))]
    return [Form]

tab_layout1 = [
    [sg.Text("Tab Maker")], 
    [sg.Button("Make new tab")]
    ]

tabs = [sg.Tab("tabOne", tab_layout1), sg.Tab("tabTwo", tabMaker("tab2"))]

layout = [
    [sg.Text("Tittle")],
    #[sg.TabGroup([tabs])],
    #[sg.Button("quit")]
    ]


window = sg.window('Multiline Example', layout)


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

window.close()