from subprocess import Popen
import tkinter as tk
from tkinter import font
import horusFunc as hf
from horusKeyboard import QWERTYKeyboard
import paho.mqtt.client as mqtt
import certifi
from datetime import datetime
import os
import ngrok
import google.generativeai as genai
import threading
from tkinter import filedialog
import sqlite3
from dotenv import load_dotenv

global Confirmar
global mqtt_client
global log_api
global api_process
global Data_start
global Data_finish

mqtt_client = None
load_dotenv('secreto.env')

teclas_in = "teclado_espiao/teclas_in"
teclas_out = "teclado_espiao/teclas_out"
routine_topic = "teclado_espiao/routine"
command_request_topic = "teclado_espiao/command_request"
command_response_topic = "teclado_espiao/command_response"

# COMANDOS
def send_cmd(cmd, params):
    global mqtt_client
    cmd_message = f"{cmd} {' '.join(params)}"

    mqtt_client.publish(command_request_topic, cmd_message)

def cmd_schedule(routine_cmd, date):

    send_cmd("SCHEDULE", [date, routine_cmd])

def cmd_routine(routine_cmd):

    send_cmd("ROUTINE", [routine_cmd])

def cmd_sync_log():
    global log_api

    send_cmd("SYNC_LOG", [log_api])

def cmd_change_mode():

    send_cmd("CHANGE_MODE", [])

keyboards = {}

def action_handler_factory(text_box, f_text_box):
    def handle_action(action, formatted):
        global Dom, mqtt_client
        print(action)
        text_box.config(state="normal")
        f_text_box.config(state="normal")
        
        action_mode = action[2].strip("'")
        print("action_mode", action_mode)
        if action_mode == "p":
            print("formatted", formatted)
            if formatted == None:
                f_text_box.delete("end-2c", "end-1c")
            else:
                f_text_box.insert("end", formatted)
        
        text_box.insert("end", str(action) + " ")
        text_box.config(state="disabled")
        f_text_box.config(state="disabled")

        if Dom:
            tecla_text = f"{action[1]} {action_mode};;"
            mqtt_client.publish(teclas_in, tecla_text)
    return handle_action

def confirm(text, text_Y, text_N):
    global Confirmar
    Confirmar = False

    def confirm_Aux(state):
        global Confirmar
        if state:
            Confirmar = True
            confirmW.destroy()
        else:
            confirmW.destroy()

    confirmW = tk.Toplevel()
    confirmW.configure(bg='#3a3a3a')
    confirmW.resizable(False, False)
    confirmW.overrideredirect(True)
    confirmW.pack_propagate(False)
    confirmW.attributes("-topmost", True)
    confirmW.grab_set()
    hf.centralize_Window(confirmW,300,150)

    button_Yes = {
        "font": ("Anonymous Pro", 16, "bold"),
        "bg": "#4CAF50",
        "fg": "white",
        "bd": 0,
        "activebackground": "#45A049",
        "activeforeground": "white"
    }

    button_No = {
        "font": ("Anonymous Pro", 16, "bold"),
        "bg": "#a1392d",
        "fg": "white",
        "bd": 0,
        "activebackground": "#943a2f",
        "activeforeground": "white"
    }

    texto_pos = tk.Frame(confirmW, width=300, height=70, bg="#3a3a3a")
    texto_pos.place(relx=0.5, anchor="n")

    texto = tk.Label(texto_pos, text=text, font=("Anonymous Pro", 16, "bold"), bg = "#3a3a3a", fg = "white")
    texto.pack(expand=True, padx=10, pady=20)

    button1 = tk.Button(confirmW, text=text_Y, command=lambda: (hf.on_Click(), confirm_Aux(True)), **button_Yes)
    button1.place(x=180,y=80, width = 100, height = 50)

    button2 = tk.Button(confirmW, text=text_N, command=lambda: (hf.on_Click(), confirm_Aux(False)), **button_No)
    button2.place(x=20,y=80, width = 100, height = 50)

    confirmW.wait_window(confirmW)

def janela_erro(texto, janela_principal=None):
    def sub_janela():
        if janela_principal is not None:
            janela_principal.destroy()

    hf.error_sound()
    if janela_principal is not None:
        janela_principal.withdraw()
    errorW = tk.Toplevel()
    errorW.configure(bg='#3a3a3a')
    errorW.resizable(False, False)
    errorW.overrideredirect(True)
    errorW.pack_propagate(False)
    errorW.attributes("-topmost", True)
    errorW.grab_set()
    hf.centralize_Window(errorW, 300, 150)

    button_ok = {
        "font": ("Anonymous Pro", 16, "bold"),
        "bg": "#a1392d",
        "fg": "white",
        "bd": 0,
        "activebackground": "#943a2f",
        "activeforeground": "white"
    }

    texto_pos = tk.Frame(errorW, width=300, height=70, bg="#3a3a3a")
    texto_pos.place(relx=0.5, anchor="n")

    texto = tk.Label(texto_pos, text=texto, font=("Anonymous Pro", 16, "bold"), bg = "#3a3a3a", fg = "white")
    texto.pack(expand=True, padx=10, pady=20)

    button1 = tk.Button(errorW, text="confirmar", command=lambda: (hf.on_Click(), errorW.destroy(), sub_janela()), **button_ok)
    button1.place(x=90, y=80, width=120, height=50)

def intro_Screen():
    hf.start_audio()
    musica = hf.play_music("resources/audio/music/Intro_song.mp3")
    imagem_caminho = hf.resource_path("resources/images/Horus_intro.png")
    
    intro = tk.Tk()
    intro.title("Welcome to Horus")
    hf.centralize_Window(intro, 500, 500)
    intro.overrideredirect(True)

    imagem = tk.PhotoImage(file=imagem_caminho)
    label_intro = tk.Label(intro, image=imagem)
    label_intro.pack(expand=True)

    intro.attributes("-alpha", 0.1)
    alpha = 0.0
    delta = 0.005
    
    def fade_in():
        nonlocal alpha
        if alpha < 1.0 :
            alpha += delta
            intro.attributes("-alpha", alpha)
            intro.after(25, fade_in)
        else:
            intro.attributes("-alpha", alpha)

    fade_in()

    intro.after(12000, lambda: [intro.destroy(), main_Screen()])
    intro.mainloop()
    
def main_Screen():

    global root, frames, routines, selected_routine, logs, logs_sorted, selected_log, Data_start, Data_finish, Search_word

    temp = 0

    topic_handlers = {}

    frames = {}
    routines = {
        "teste": {
            "desc": "isso é um teste",
            "command": "('T', 'PRESSED', '0.40') ('E', 'PRESSED', '30.04') ('S', 'RELEASED', '19.73') ('T', 'RELEASED', '30.69') ('G', 'RELEASED', '51.84') ('S', 'PRESSED', '61.99') ('G', 'PRESSED', '29.85') ('E', 'RELEASED', '20.29') ('E', 'PRESSED', '69.66') ('S', 'RELEASED', '125.01') ('E', 'RELEASED', '52.24') ('G', 'RELEASED', '98.22')"
        }
    }
    logs = {}

    logs_sorted = {}

    selected_routine = None
    selected_log = None

    
    api_key = os.getenv('API_KEY')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    def set_topic_handler( topic, func):
        topic_handlers[topic] = func

    hf.start_audio()

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect( client, userdata, flags, rc):
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(teclas_out)
        client.subscribe(command_response_topic)

        # The callback for when a PUBLISH message is received from the server.
    def on_message( client, userdata, msg):
        topic = str(msg.topic)
        message = str(msg.payload.decode('utf-8'))
        print("MESSAGE:", message)
        if topic in topic_handlers:
            topic_handlers[topic](message)

    def start_mqtt():
        global mqtt_client
        mqtt_client = mqtt.Client()
        mqtt_client.tls_set(certifi.where())
        mqtt_client.username_pw_set(username="aula", password= "zowmad-tavQez")
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message

        mqtt_client.connect("mqtt.janks.dev.br", 8883, 60)
        #mqtt_client.connect("mqtt.janks.dev.br", 1883, 70)
        step_mqtt()

    def step_mqtt():
        global mqtt_client
        mqtt_client.loop_read()
        mqtt_client.loop_write()
        mqtt_client.loop_misc()
        root.after(20, step_mqtt)

    # Log api start
    def setup_api():
        global log_api, api_process
        api_command = ["python","log_api.py"]
        api_process = Popen(api_command)

        ngrok.set_auth_token("2pKQ7D8bWrRMQKk5LFue3scb4o1_32UcALS4fAWgkyhz6UryW")

        listener = ngrok.forward("localhost:8000")

        log_api = listener.url()
    
    setup_api()

    root = tk.Tk()    
    root.configure(bg='#252525')
    root.title("Horus")
    root.resizable(False, False)

    icon_path = "resources/images/icon.ico"
    #root.iconbitmap(icon_path)

    hf.centralize_Window(root)

    start_mqtt()

    #Globais

    global Confirmar
    global Dom
    global NameText
    global ContextText

    Dom = False

    #media

    imagem_search_path = hf.resource_path("resources/images/search_icon.png")
    imagem_search = tk.PhotoImage(file=imagem_search_path)

    imagem_clear_path = hf.resource_path("resources/images/clear_icon.png")
    imagem_clear = tk.PhotoImage(file=imagem_clear_path)

    imagem_up_path = hf.resource_path("resources/images/arrow_up.png")
    imagem_up = tk.PhotoImage(file=imagem_up_path)

    imagem_down_path = hf.resource_path("resources/images/arrow_down.png")
    imagem_down = tk.PhotoImage(file=imagem_down_path)

    imagem_sync_path = hf.resource_path("resources/images/sync_button.png")
    imagem_sync = tk.PhotoImage(file=imagem_sync_path)

    #Logica de estados
    
    def paint_frames(color):
        global frames

        for frame in frames:
            frames[frame].config(bg=color)

    def dominate():
        print("DOMINATION MODE")
        paint_frames('#502525')
        rotinas_botoes.config(bg='#502525')
        keyboards["Home"].bind_keys()
        hf.on_Click_Dom_On()

    def release():
        print("RELEASE MODE")
        paint_frames('#252525')
        rotinas_botoes.config(bg='#252525')
        keyboards["Home"].unbind_keys()
        hf.on_Click_Dom_Off()

    def change_state():
        global Dom
        global Confirmar
        if Dom:
            release()
            Dom = False
            cmd_change_mode()
        else:
            confirm("Tem Certeza?","Sim","Não")
            if Confirmar:
                dominate()
                Dom = True
                cmd_change_mode()
        
    
    #Estilos dos Botões

    button_Style_Sidebar = {
        "font": ("Anonymous Pro", 16, "bold"),
        "bg": "#4CAF50",
        "fg": "white",
        "bd": 0,
        "activebackground": "#45A049",
        "activeforeground": "white"
    }

    button_Style_Domidar = {
        "font": ("Anonymous Pro", 16, "bold"),
        "bg": "#a1392d",
        "fg": "white",
        "bd": 0,
        "activebackground": "#943a2f",
        "activeforeground": "white"
    }
    
    #Estilos Globais

    sidebar = tk.Frame(root, width=250, bg='#3a3a3a')
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    #Estilos da Home

    home_frame = tk.Frame(root, width=1030, height=720, bg="#252525")
    home_frame.place(x=250,y = 0)

    frames["Home"] = home_frame

    button_dominate = tk.Button(home_frame, text="Dominar", command=change_state, width = 10, height = 2, **button_Style_Domidar)
    button_dominate.place(relx=0.5, y=15, anchor="n")
    button_dominate.bind("<Enter>", hf.on_Enter_Dominar)
    button_dominate.bind("<Leave>", hf.on_Leave_Dominar)

    home_Principal = tk.Frame(home_frame, width=801, height=550, bd=1, relief="solid", bg="#3a3a3a")
    home_Principal.place(x = 115,y = 85)

    home_Principal_GUI_userInput = tk.Frame(home_Principal, width=800, height=50, bd=1, relief="solid", bg="#000")
    home_Principal_GUI_userInput.place(x=0,y=500)

    home_Principal_GUI_keyboardInput_format = tk.Frame(home_Principal, width=500, height=250, bd=1, relief="solid", bg="#242323")
    home_Principal_GUI_keyboardInput_format.place(x=0,y=0)

    home_Principal_GUI_keyboardInput_dump = tk.Frame(home_Principal, bd=1, relief="solid", bg="#242323")
    home_Principal_GUI_keyboardInput_dump.place(x=500,y=0, width=300, height=250)

    home_Principal_GUI_keyboardInput_realTime = tk.Frame(home_Principal, width=800, height=250, bd=1, relief="solid", bg="#242323")
    home_Principal_GUI_keyboardInput_realTime.place(x=0,y=250)
    
    home_Principal_GUI_keyboardInput_format_Text = tk.Text(home_Principal_GUI_keyboardInput_format, font=("Anonymous Pro", 11), bg="#242323", fg="white", highlightthickness=0, bd=0)
    home_Principal_GUI_keyboardInput_format_Text.pack(fill="both",expand=True)
    home_Principal_GUI_keyboardInput_format_Text.config(state="normal")

    home_Principal_GUI_keyboardInput_dump_Text = tk.Text(home_Principal_GUI_keyboardInput_dump, font=("Anonymous Pro", 11), bg="#242323", fg="white", highlightthickness=0, bd=0)
    home_Principal_GUI_keyboardInput_dump_Text.pack(fill="both",expand=True)
    home_Principal_GUI_keyboardInput_dump_Text.config(state="normal")

    keyboards["Home"] = QWERTYKeyboard(root, home_Principal_GUI_keyboardInput_realTime,110, 20)
    keyboards["Home"].set_mode("typing", action_handler_factory(home_Principal_GUI_keyboardInput_dump_Text, home_Principal_GUI_keyboardInput_format_Text))

    def label_received(msg):
        if len(msg.strip(" ")) == 0:
            return
        print("KEY OUT: ", msg)
        msg = msg.strip(";")
        msg = msg.replace("'", "")

        params = msg.split(" ")
        label = params[0]
        action = params[1]

        print("LABEL", label)
        print("ACTION", action)

        if action == "p":
            keyboards["Home"].label_pressed(label)
        else:
            keyboards["Home"].label_released(label)

    set_topic_handler(teclas_out, label_received)

    #Estilo das Rotinas

    routine_frame = tk.Frame(root, width=1030, height=720, bg="#252525")
    routine_frame.place(x=250,y = 0)

    frames["Routine"] = routine_frame

    rotinas_Lista = hf.ScrollableFrame(routine_frame, width=400, height=550)
    rotinas_Lista.place(x = 115,y = 85)


    rotinas_Detalhes = tk.Frame(routine_frame, width=300, height=250, bd=1, relief="solid", bg="#242323")
    rotinas_Detalhes.pack_propagate(False)

    rotinas_Detalhes_Text = tk.Text(rotinas_Detalhes, font=("Anonymous Pro", 11), bg="#242323", fg="white", highlightthickness=0, bd=0)
    rotinas_Detalhes_Text.pack(fill="both",expand=True)
    rotinas_Detalhes_Text.config(state="disabled")

    rotinas_Detalhes.place(x=615,y=85)

    rotinas_botoes = tk.Frame(routine_frame, width=300, height=250, bg="#252525")
    rotinas_botoes.place(x = 615, y = 388)
    def get_button_details(routine):
        def show_details():
            global selected_routine
            
            selected_routine = routine
            insere_texto(rotinas_Detalhes_Text, routines[routine]["command"])
        return show_details
    
    def build_routine_list():
        global routines
        
        for child in rotinas_Lista.scrollable_frame.winfo_children():
            child.destroy()

        for routine in routines:
        
            button = tk.Button(
                    rotinas_Lista.scrollable_frame,
                    text = routine,
                    command=get_button_details(routine),
                    **button_Style_Sidebar
                )
            button.pack(pady=5, padx=0, fill="x", expand=True)

    create_routine_button = tk.Button(rotinas_botoes, text="Criar", command=lambda: (hf.on_Click(), carrega_frame("CreateRoutine")), **button_Style_Sidebar)
    create_routine_button.place(x=0, y=0, width=300, height=70)
    create_routine_button.bind("<Enter>", hf.on_Enter_Sidebar)
    create_routine_button.bind("<Leave>", hf.on_Leave_Sidebar)

    #schedule_routine_frame = tk.Frame(root, width=1030, height=720, bg="#252525")
    #schedule_routine_frame.place(x=250,y = 0)

    schedule_routine_button = tk.Button(rotinas_botoes, text="Agendar", command=lambda: (hf.on_Click(), open_schedule_popup(selected_routine)), **button_Style_Sidebar)
    schedule_routine_button.place(x=0, y=90, width=300, height=70)
    schedule_routine_button.bind("<Enter>", hf.on_Enter_Sidebar)
    schedule_routine_button.bind("<Leave>", hf.on_Leave_Sidebar)

    def play_routine():
        global routines, selected_routine

        if selected_routine == None:
            return

        routine = routines[selected_routine]

        cmd_routine(routine["command"])

    play_routine_button = tk.Button(rotinas_botoes, text="Play", command=lambda: (hf.on_Click(), play_routine()), **button_Style_Sidebar)
    play_routine_button.place(x=0, y=180, width=300, height=70)
    play_routine_button.bind("<Enter>", hf.on_Enter_Sidebar)
    play_routine_button.bind("<Leave>", hf.on_Leave_Sidebar)

    #Estilo da Criar - Texto

    create_routine_frame = tk.Frame(root, width=1030, height=720, bg="#252525")
    create_routine_frame.place(x=250,y = 0)

    frames["CreateRoutine"] = create_routine_frame

    criar_Nome_Label = tk.Label(create_routine_frame, text="Nome: ", font=("Anonymous Pro", 20, "bold"), bg = "#252525", fg = "white")
    criar_Nome_Label.place(x=115, y = 85)

    criar_Nome = tk.Text(create_routine_frame, font=("Anonymous Pro", 16), bg="#252525", fg="white", highlightthickness=0, bd=0)
    criar_Nome.place(x=200, y = 90, width = 700, height = 35)

    criar_Nome_Linha = tk.Frame(create_routine_frame, bg = "#000")
    criar_Nome_Linha.place(x=200, y = 115, width = 700, height = 2)

    criar_Descricao_Label = tk.Label(create_routine_frame, text="Descrição: ", font=("Anonymous Pro", 20, "bold"), bg = "#252525", fg = "white")
    criar_Descricao_Label.place(x=115, y = 200)

    criar_Descricao = tk.Text(create_routine_frame, font=("Anonymous Pro", 16), bg="#242323", fg="white", highlightthickness=0, bd=1, relief = "solid")
    criar_Descricao.place(x = 115, y = 250, width = 400, height = 300)

    command_Label = tk.Label(create_routine_frame, text="Rotina: ", font=("Anonymous Pro", 20, "bold"), bg = "#252525", fg = "white")
    command_Label.place(x=515, y=200)

    command_Text = tk.Text(create_routine_frame, font=("Anonymous Pro", 16), bg="#242323", fg="white", highlightthickness=0, bd=1, relief = "solid", state="disable")
    command_Text.place(x = 515, y = 250, width = 400, height = 300)

    def adicionar_rotina(nome, desc, cmd):
        global routines
        
        routines[nome] = {"name": nome, "desc": desc, "command": cmd}
        build_routine_list() 

    def submit_text():
        confirm("Tem Certeza?","Sim","Não")
        if Confirmar:
            nome = criar_Nome.get("1.0", tk.END).strip()
            descricao = criar_Descricao.get("1.0", tk.END).strip()
            command = command_Text.get("1.0", tk.END).strip()
            adicionar_rotina(nome, descricao, command)
            insere_texto(criar_Nome, "")
            criar_Nome.config(state="normal")
            insere_texto(criar_Descricao, "")
            criar_Descricao.config(state="normal")
            insere_texto(command_Text, "")
            command_Text.config(state="normal")
            carrega_frame("Routine")

    confirm_routine_button = tk.Button(create_routine_frame, text = "Criar", command=lambda: (hf.on_Click(), submit_text()), width = 10, height = 2, **button_Style_Sidebar)
    confirm_routine_button.place(x=715,y=575, width= 200, height= 50)
    confirm_routine_button.bind("<Enter>", hf.on_Enter_Sidebar)
    confirm_routine_button.bind("<Leave>", hf.on_Leave_Sidebar)

    def gravar_screen():
        global state, root
        state = False

        def destruir():
            gravar.destroy()
        
        gravar = tk.Toplevel()
        gravar.configure(bg='#2e2b2b')
        gravar.resizable(False, False)
        #gravar.overrideredirect(True)
        gravar.pack_propagate(False)
        gravar.attributes("-topmost", True)
        gravar.grab_set()
        hf.centralize_Window(gravar,1100,500)

        button_Style = {
            "font": ("Anonymous Pro", 16, "bold"),
            "bg": "#4CAF50",
            "fg": "white",
            "bd": 0,
            "activebackground": "#45A049",
            "activeforeground": "white"
        }

        Keyboard_Frame = tk.Frame(gravar, bd=1, relief="solid", bg="#242323")
        Keyboard_Frame.place(x=0,y=0, width=800,height= 350)

        keyboards["Routine"] = QWERTYKeyboard(gravar, Keyboard_Frame, 100, 10)

        texto_Formatado_Frame = tk.Frame(gravar, bd=1, relief="solid", bg="#242323")
        texto_Formatado_Frame.place(x=800,y=0, width=300,height= 350)

        texto_Dump_Frame = tk.Frame(gravar, bd=1, relief="solid", bg="#242323")
        texto_Dump_Frame.place(x=0,y=350, width=800,height= 150)

        texto_Formatado_Frame_Text = tk.Text(texto_Formatado_Frame, font=("Anonymous Pro", 11), bg="#242323", fg="white", highlightthickness=0, bd=0)
        texto_Formatado_Frame_Text.pack(fill="both",expand=True)
        texto_Formatado_Frame_Text.config(state="disabled")

        texto_Dump_Frame_Text = tk.Text(texto_Dump_Frame, font=("Anonymous Pro", 11), bg="#242323", fg="white", highlightthickness=0, bd=0)
        texto_Dump_Frame_Text.pack(fill="both",expand=True)
        texto_Dump_Frame_Text.config(state="disabled")

        button = tk.Button(gravar, text="START", width = 10, height = 2, **button_Style)
        button.place(x=800, y=350, width = 300 , height = 150)
        
        def toggle_record():
            global state
            if state:
                insere_texto(command_Text, texto_Dump_Frame_Text.get("1.0", "end"))
                destruir()
            else:
                keyboards["Routine"].bind_keys()
                keyboards["Routine"].set_mode("typing", action_handler_factory(texto_Dump_Frame_Text, texto_Formatado_Frame_Text))
                button.config(text="STOP", bg="#a1392d",activebackground="#943a2f")
                state = True
        
        button.config(command=toggle_record)

        gravar.wait_window(gravar)
    
    record_routine_button = tk.Button(create_routine_frame, text = "Gravar", command=lambda: (hf.on_Click(), gravar_screen()), width = 10, height = 2, **button_Style_Domidar,)
    record_routine_button.place(x=465,y=575, width= 200, height= 50)
    record_routine_button.bind("<Enter>", hf.on_Enter_Dominar)
    record_routine_button.bind("<Leave>", hf.on_Leave_Dominar)

    build_routine_list()
    
    # Agendamento de rotinas

    def open_schedule_popup(routine):
        if routine is None:
            janela_erro("Selecione uma rotina!")
            return
        def on_confirm():
            try:
                diaS = dia.get()
                mesS = mes.get()
                anoS = "20" + ano.get()
                horaS = hora.get()
                minutoS = minuto.get()

                secure_date = datetime.strptime(f"{diaS}/{mesS}/{anoS}", "%d/%m/%Y").strftime("%y-%m-%d")
                secure_time = datetime.strptime(f"{horaS}:{minutoS}", "%H:%M").strftime("%H-%M")
            except:
                janela_erro("Inválido!")
                agendarW.destroy()
                return

            cmd_schedule(routines[routine]["command"], f"{secure_date}_{secure_time}")
            agendarW.destroy()

        agendarW = tk.Toplevel()
        agendarW.configure(bg='#3a3a3a')
        agendarW.resizable(False, False)
        agendarW.overrideredirect(True)
        agendarW.pack_propagate(False)
        agendarW.attributes("-topmost", True)
        agendarW.grab_set()
        hf.centralize_Window(agendarW,300,300)

        hf.make_draggable(agendarW)

        vcmd = (agendarW.register(hf.validate_input), '%d', '%P')

        button_confirm = {
            "font": ("Anonymous Pro", 16, "bold"),
            "bg": "#4CAF50",
            "fg": "white",
            "bd": 0,
            "activebackground": "#45A049",
            "activeforeground": "white"
        }

        entry_options = {
        "validate": "key",
        "validatecommand": vcmd,
        "font": ("Arial", 16),
        "justify": "center",
        "bg": "#242323",              # Cor de fundo
        "fg": "#ffffff",             # Cor do texto
        "relief": "solid",           # Borda sólida
        "highlightbackground": "#4CAF50",  # Cor da borda
        "highlightthickness": 2      # Espessura da borda
        }

        texto_pos_data = tk.Frame(agendarW, bg="#3a3a3a")
        texto_pos_data.place(x = 10, y = 10, width=290, height=20)

        texto_data = tk.Label(texto_pos_data, text="Insira a data", font=("Anonymous Pro", 16, "bold"), bg = "#3a3a3a", fg = "white")
        texto_data.pack(expand=True)

        dia = tk.Entry(agendarW, **entry_options)
        dia.place(x=70, y=50, width=40, height=40)

        barrinha1_ini = tk.Label(agendarW, text="/", bg="#3a3a3a", fg="white", font=("Anonymous Pro", 24))
        barrinha1_ini.place(x=120, y=50)

        mes = tk.Entry(agendarW, **entry_options)
        mes.place(x=140, y=50, width=40, height=40)

        barrinha2_ini = tk.Label(agendarW, text="/", bg="#3a3a3a", fg="white", font=("Anonymous Pro", 24))
        barrinha2_ini.place(x=190, y=50)

        ano = tk.Entry(agendarW, **entry_options)
        ano.place(x=210, y=50, width=40, height=40)

        texto_pos_hora = tk.Frame(agendarW, bg="#3a3a3a")
        texto_pos_hora.place(x = 10, y = 110, width=290, height=20)

        texto_hora = tk.Label(texto_pos_hora, text="Insira a hora", font=("Anonymous Pro", 16, "bold"), bg = "#3a3a3a", fg = "white")
        texto_hora.pack(expand=True)

        hora = tk.Entry(agendarW, **entry_options)
        hora.place(x=105, y=150, width=40, height=40)

        barrinha1_fim = tk.Label(agendarW, text=":", bg="#3a3a3a", fg="white", font=("Anonymous Pro", 24))
        barrinha1_fim.place(x=147, y=150)

        minuto = tk.Entry(agendarW, **entry_options)
        minuto.place(x=165, y=150, width=40, height=40)

        button1 = tk.Button(agendarW, text="confirmar", command=lambda: (on_confirm()), **button_confirm)
        button1.place(x=90,y=230, width = 120, height = 50)

        agendarW.wait_window(agendarW)

    #Estilos dos Logs

    log_frame = tk.Frame(root, width=1030, height=720, bg="#252525")
    log_frame.place(x=250,y = 0)
    
    log_Lista = hf.ScrollableFrame(log_frame, width=300, height=550)
    log_Lista.place(x = 115,y = 85)

    log_visual = tk.Frame(log_frame, width = 415, height = 450, bd=1, relief="solid", bg="#242323")
    log_visual.place(x = 500,y = 85)
    log_visual_text = hf.ScrollableText(log_visual,width=415,height=450)
    log_visual_text.pack(fill="both", expand=True)

    log_button_search = tk.Button(log_frame, image=imagem_search, borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click(), inserir_datas()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_search.place(x=80,y=85,width=30,height=30)

    log_button_clear = tk.Button(log_frame, image=imagem_clear, borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click(), build_log_list(1)), width = 10, height = 2, **button_Style_Sidebar)
    log_button_clear.place(x=80,y=120,width=30,height=30)
    log_button_clear.place_forget()

    log_button_search_context = tk.Button(log_frame, image=imagem_search, borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click(), procurar_texto()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_search_context.place(x=930,y=85,width=30,height=30)

    log_button_context_next = tk.Button(log_frame, image=imagem_down, borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click(), log_visual_text.go_next()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_context_next.place(x=930,y=155,width=30,height=30)

    log_button_context_back = tk.Button(log_frame, image=imagem_up, borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click(), log_visual_text.go_back()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_context_back.place(x=930,y=120,width=30,height=30)

    log_button_Sync = tk.Button(log_frame, image=imagem_sync, borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click(), sync_logs()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_Sync.place(x=500,y=550, width = 95, height=85)

    log_button_AI = tk.Button(log_frame, text="AI", borderwidth=0, highlightthickness=0, command=lambda: (run_contexto_AI()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_AI.place(x = 605, y = 550, width=150,height=85)

    log_button_baixar = tk.Button(log_frame, text="Download", borderwidth=0, highlightthickness=0, command=lambda: (download_log()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_baixar.place(x = 765, y = 550, width=150,height=85)

    def download_log():
        if selected_log is not None:
            def escreve_log(file_path,text):
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(text)
            
            hf.on_Click()
            file_name = selected_log[0] + ".txt"
            file_name = file_name.replace("/", "_")
            if not os.path.exists(file_name):
                escreve_log(file_name,selected_log[1])
            else:
                contador = 1
                base, extension = os.path.splitext(file_name)
                while os.path.exists(base + f"({contador})" + extension):
                    contador+=1
                escreve_log(base + f"({contador})" + extension, selected_log[1])
        else:
            janela_erro("Selecione um log!")
    
    def contexto_AI():
        global selected_log
        log_button_AI.place_forget()
        pergunta = "Eu tenho esse log aqui, me de tudo de importante sobre ele como pontos chaves (sempre de os pontos chaves), possiveis senhas e informaçoes importantes: "
        pergunta += selected_log[1]
        resposta = model.generate_content(pergunta).text
        button_Style_Ai = {}
        for key, value in button_Style_Sidebar.items():
            button_Style_Ai[key] = value
        button_Style_Ai["bg"] = '#2478ff'
        button_Style_Ai["activebackground"] = '#1961d4'
        hf.response_sound()
        log_button_AI_response = tk.Button(log_frame, text="AI", borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click(), janela_AI(resposta, log_button_AI_response)), width = 10, height = 2, **button_Style_Ai)
        log_button_AI_response.place(x = 605, y = 550, width=150,height=85)
        

    def janela_AI(resposta,widget):
        def proxima_resposta():
            widget.place_forget()
            log_button_AI.place(x = 605, y = 550, width=150,height=85)
            aiW.destroy()
        aiW = tk.Toplevel()
        aiW.configure(bg='#3a3a3a')
        aiW.resizable(False, False)
        aiW.overrideredirect(True)
        aiW.pack_propagate(False)
        aiW.attributes("-topmost", True)
        aiW.grab_set()
        hf.centralize_Window(aiW,300,300)

        hf.make_draggable(aiW)

        button_confirm = {
            "font": ("Anonymous Pro", 16, "bold"),
            "bg": "#4CAF50",
            "fg": "white",
            "bd": 0,
            "activebackground": "#45A049",
            "activeforeground": "white"
        }

        texto_pos = tk.Frame(aiW, bg="#3a3a3a")
        texto_pos.place(x = 10, y = 10, width=280, height=230)

        texto = hf.ScrollableText(texto_pos, width=50,height=50)
        texto.pack(fill="both", expand=True)

        button1 = tk.Button(aiW, text="confirmar", command=lambda: (hf.on_Click(), proxima_resposta()), **button_confirm)
        button1.place(x=100,y=250, width = 100, height = 40)

        insere_texto(texto, resposta)

        aiW.wait_window(aiW)

    def run_contexto_AI():
        global selected_log
        if selected_log is None:
            janela_erro("Selecione um log!")
            return
        hf.on_Click()
        threading.Thread(target=contexto_AI).start()

    def update_logs():
        try:
            global logs
            conn = sqlite3.connect('logs.db')
            cursor = conn.cursor()
            cursor.execute("SELECT date, file_content FROM log")
            linhas = cursor.fetchall()
            datas = [linha[0] for linha in linhas]
            texto = [linha[1] for linha in linhas]
            for (i,el) in enumerate(datas):
                logs[datas[i]] = {"desc": texto[i]}
            conn.close()
            build_log_list(1)
        except:
            print("error")
            pass

    def sync_logs():
        def watch_sync_finished(msg):
            print("finishing logs")
            if msg == "Sync terminado.":
                update_logs()
                set_topic_handler(command_response_topic, lambda msg: print(msg))
            
        set_topic_handler(command_response_topic, watch_sync_finished)
        cmd_sync_log()

    def build_log_list(case):
        def get_button_details_log(date, log):
            global selected_log
            texto = log["desc"].strip()
            selected_log = date, texto
            insere_texto(log_visual_text, texto)

        global logs, logs_sorted
        for child in log_Lista.scrollable_frame.winfo_children():
            child.destroy()

        if case == 1:
            lista = logs
            log_button_clear.place_forget()
            
        else:
            lista = logs_sorted
            log_button_clear.place(x=80,y=120,width=30,height=30)
        for date, log in lista.items():
            button = tk.Button(
                    log_Lista.scrollable_frame,
                    text = date,
                    command = lambda log = log: get_button_details_log(date, log),
                    **button_Style_Sidebar
                )
            button.pack(pady=5, padx=0, fill="x", expand=True)
    
    def sort_logs():
        global logs, logs_sorted, Data_start, Data_finish
        logs_sorted = {}
        for chave, valor in logs.items():
            ano, mes, dia = chave.split("-")
            data = datetime.strptime(f"{dia}/{mes}/{ano}", "%d/%m/%Y")
            if data >= Data_start and data <= Data_finish:
                logs_sorted[chave] = valor
        build_log_list(0)

    def inserir_datas():
        global Data_start
        global Data_finish

        Data_start = datetime.min
        Data_finish = datetime.max
        
        def validar_data(dia1,dia2,mes1,mes2,ano1,ano2):
            global Data_start
            global Data_finish
            try:
                ano1 = "20" + ano1
                ano2 = "20" + ano2
                data_date_ini = datetime.strptime(f"{dia1}/{mes1}/{ano1}", "%d/%m/%Y")
                data_date_fim = datetime.strptime(f"{dia2}/{mes2}/{ano2}", "%d/%m/%Y")
                if data_date_fim < data_date_ini:
                    raise Exception()
                Data_start = data_date_ini
                Data_finish = data_date_fim
                hf.on_Click()
                sort_logs()
                dataW.destroy()
            except:
                janela_erro("Digite uma data valida!", dataW)

        dataW = tk.Toplevel()
        dataW.configure(bg='#3a3a3a')
        dataW.resizable(False, False)
        dataW.overrideredirect(True)
        dataW.pack_propagate(False)
        dataW.attributes("-topmost", True)
        dataW.grab_set()
        hf.centralize_Window(dataW,300,300)

        hf.make_draggable(dataW)

        vcmd = (dataW.register(hf.validate_input), '%d', '%P')

        button_confirm = {
            "font": ("Anonymous Pro", 16, "bold"),
            "bg": "#4CAF50",
            "fg": "white",
            "bd": 0,
            "activebackground": "#45A049",
            "activeforeground": "white"
        }

        entry_options = {
        "validate": "key",
        "validatecommand": vcmd,
        "font": ("Arial", 16),
        "justify": "center",
        "bg": "#242323",              # Cor de fundo
        "fg": "#ffffff",             # Cor do texto
        "relief": "solid",           # Borda sólida
        "highlightbackground": "#4CAF50",  # Cor da borda
        "highlightthickness": 2      # Espessura da borda
        }

        texto_pos_ini = tk.Frame(dataW, bg="#3a3a3a")
        texto_pos_ini.place(x = 10, y = 10, width=290, height=20)

        texto_ini = tk.Label(texto_pos_ini, text="Insira a data Inicial", font=("Anonymous Pro", 16, "bold"), bg = "#3a3a3a", fg = "white")
        texto_ini.pack(expand=True)

        dia_ini = tk.Entry(dataW, **entry_options)
        dia_ini.place(x=70, y=50, width=40, height=40)

        barrinha1_ini = tk.Label(dataW, text="/", bg="#3a3a3a", fg="white", font=("Anonymous Pro", 24))
        barrinha1_ini.place(x=120, y=50)

        mes_ini = tk.Entry(dataW, **entry_options)
        mes_ini.place(x=140, y=50, width=40, height=40)

        barrinha2_ini = tk.Label(dataW, text="/", bg="#3a3a3a", fg="white", font=("Anonymous Pro", 24))
        barrinha2_ini.place(x=190, y=50)

        ano_ini = tk.Entry(dataW, **entry_options)
        ano_ini.place(x=210, y=50, width=40, height=40)

        texto_pos_fim = tk.Frame(dataW, bg="#3a3a3a")
        texto_pos_fim.place(x = 10, y = 110, width=290, height=20)

        texto_fim = tk.Label(texto_pos_fim, text="Insira a data final", font=("Anonymous Pro", 16, "bold"), bg = "#3a3a3a", fg = "white")
        texto_fim.pack(expand=True)

        dia_fim = tk.Entry(dataW, **entry_options)
        dia_fim.place(x=70, y=150, width=40, height=40)

        barrinha1_fim = tk.Label(dataW, text="/", bg="#3a3a3a", fg="white", font=("Anonymous Pro", 24))
        barrinha1_fim.place(x=120, y=150)

        mes_fim = tk.Entry(dataW, **entry_options)
        mes_fim.place(x=140, y=150, width=40, height=40)

        barrinha2_fim = tk.Label(dataW, text="/", bg="#3a3a3a", fg="white", font=("Anonymous Pro", 24))
        barrinha2_fim.place(x=190, y=150)

        ano_fim = tk.Entry(dataW, **entry_options)
        ano_fim.place(x=210, y=150, width=40, height=40)

        formato_ini = tk.Label(dataW, text="Formato: dd / mm / yy", font=("Anonymous Pro", 10), bg="#3a3a3a", fg="white")
        formato_ini.place(x=80, y=200)

        button1 = tk.Button(dataW, text="confirmar", command=lambda: (validar_data(dia_ini.get(),dia_fim.get(),mes_ini.get(),mes_fim.get(),ano_ini.get(),ano_fim.get())), **button_confirm)
        button1.place(x=90,y=230, width = 120, height = 50)

        dataW.wait_window(dataW)

    def perform_search():
        global Search_word
        log_visual_text.search_text(Search_word)

    def procurar_texto():
        def confirm_text():
            global Search_word
            Search_word = texto.get()
            perform_search()
            searchW.destroy()
        searchW = tk.Toplevel()
        searchW.configure(bg='#3a3a3a')
        searchW.resizable(False, False)
        searchW.overrideredirect(True)
        searchW.pack_propagate(False)
        searchW.attributes("-topmost", True)
        searchW.grab_set()
        hf.centralize_Window(searchW,300,300)

        hf.make_draggable(searchW)

        button_confirm = {
            "font": ("Anonymous Pro", 16, "bold"),
            "bg": "#4CAF50",
            "fg": "white",
            "bd": 0,
            "activebackground": "#45A049",
            "activeforeground": "white"
        }

        texto_pos = tk.Frame(searchW, bg="#3a3a3a")
        texto_pos.place(x = 10, y = 10, width=280, height=230)

        texto = hf.ScrollableText(texto_pos, width=50,height=50)
        texto.pack(fill="both", expand=True)

        button1 = tk.Button(searchW, text="confirmar", command=lambda: (hf.on_Click(), confirm_text()), **button_confirm)
        button1.place(x=100,y=250, width = 100, height = 40)

        searchW.wait_window(searchW)

    update_logs()
    frames["Log"] = log_frame

    #Estilos das configuracoes
    global download_path_default
    download_path_default = os.path.abspath(__file__)
    pular_intro = 0

    scale_config = {
        "from_": 0,
        "to": 100,
        "orient": "horizontal",
        "command": hf.ajustar_volume,
        "bg": "#252525",
        "length": 300,
        "bd": 0,
        "highlightthickness": 0,
        "showvalue": False,
        "resolution": 10
    }

    def mudar_path():
        global download_path_default
        download_path = filedialog.askdirectory(title="Escolher um diretório")
        if not download_path:
            download_path = download_path_default
        config_label_download_path.config(text=download_path)
        download_path_default = download_path

    conf_frame = tk.Frame(root, width=1030, height=720, bg="#252525")
    conf_frame.place(x=250,y = 0)

    config_label_download = tk.Label(conf_frame, text="Path de download:", font=("Anonymous Pro", 16, "bold"), bg = "#252525", fg = "white")
    config_label_download.place(x=115, y=85)
    
    config_label_download_path = tk.Label(conf_frame, text=download_path_default, font=("Anonymous Pro", 11, "bold"), bg = "#252525", fg = "gray")
    config_label_download_path.place(x=115, y=120)

    config_label_download_button = tk.Button(conf_frame, text="Mudar", command=lambda: (hf.on_Click(), mudar_path()), **button_Style_Sidebar)
    config_label_download_button.place(x=115, y=150, width=100,height=30)

    config_label_volume = tk.Label(conf_frame, text="Volume:", font=("Anonymous Pro", 16, "bold"), bg = "#252525", fg = "white")
    config_label_volume.place(x=115, y=200)

    config_label_volume_slider = tk.Scale(conf_frame,**scale_config)
    config_label_volume_slider.set(100)
    config_label_volume_slider.place(x=210, y=210)

    config_label_intro = tk.Label(conf_frame, text="Pular Intro:", font=("Anonymous Pro", 16, "bold"), bg = "#252525", fg = "white")
    config_label_intro.place(x=115,y=250)

    config_label_intro_checkbox = tk.Checkbutton(conf_frame, variable=pular_intro, bg="#252525",highlightthickness=0,activebackground="#252525",)
    config_label_intro_checkbox.place(x=235,y=255)

    frames["Config"] = conf_frame

    #Botoes

    home_button = tk.Button(sidebar, text="Home", command=lambda: (hf.on_Click(), carrega_frame("Home")), **button_Style_Sidebar)
    home_button.pack(pady=10, padx=10, fill="x")

    routine_button = tk.Button(sidebar, text="Rotinas", command=lambda: (hf.on_Click(), carrega_frame("Routine")), **button_Style_Sidebar)
    routine_button.pack(pady=10, padx=10, fill="x")

    log_button = tk.Button(sidebar, text="Logs", command=lambda: (hf.on_Click(), carrega_frame("Log")), **button_Style_Sidebar)
    log_button.pack(pady=10, padx=10, fill="x")

    config_button = tk.Button(sidebar, text="Configurações", command=lambda: (hf.on_Click(), carrega_frame("Config")), **button_Style_Sidebar)
    config_button.pack(pady=10, padx=10, fill="x")
    

    buttons_sidebar = [
        home_button,
        routine_button,
        log_button,
        config_button
    ]
    
    for button in buttons_sidebar:
        button.bind("<Enter>", hf.on_Enter_Sidebar)
        button.bind("<Leave>", hf.on_Leave_Sidebar)

    def carrega_frame(frame):
        global frames

        frames[frame].place(x = 250, y = 0)
        
        for f in frames:
            if f != frame:
                frames[f].place_forget()

    def insere_texto(widget, contexto):
        widget.config(state="normal")
        widget.delete('1.0', tk.END)
        widget.insert(tk.END, contexto)
        widget.config(state="disabled")

    carrega_frame("Home")
    try:
        root.mainloop()
    except KeyboardInterrupt:
        api_process.terminate()
        ngrok.disconnect()