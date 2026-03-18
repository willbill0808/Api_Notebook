import FreeSimpleGUI as sg
import requests, json 

tab_layout1 = [[sg.Button('My first Button!'), sg.Checkbox('My first Checkbox!')],
               [sg.Button('Another Button.')]]
tab_layout2 = [[sg.Button('My third Button!'), sg.Checkbox('My second Checkbox!')]]

layout = [[sg.TabGroup([[sg.Tab("Tab 1", tab_layout1), sg.Tab("Tab 2", tab_layout2)]])]]


layout1 = [
    [sg.Multiline(key='-ML-', write_only=True, size=(60,10))]
]

window = sg.Window('Multiline Example', layout, finalize=True)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

window.close()