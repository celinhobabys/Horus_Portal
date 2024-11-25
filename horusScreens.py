import tkinter as tk
from tkinter import font
import horusFunc as hf
from horusKeyboard import QWERTYKeyboard
import pygame
import paho.mqtt.client as mqtt
import certifi

global Confirmar
global mqtt_client
mqtt_client = None

teclas_in = "teclado_espiao/teclas_in"
teclas_out = "teclado_espiao/teclas_out"
routine_topic = "teclado_espiao/routine"

keyboards = {}

def action_handler_factory(text_box, f_text_box):
    def handle_action(action):
        print(action)
        if action[1] == "PRESSED":
            text_box.insert("end", str(action) + " ")
        elif action[1] == "RELEASED":
            text_box.insert("end", str(action) + " ")

            letter = action[0]
            
            if letter == "SPACE":
                letter = " "
            if letter == "CONTROL":
                letter = ""

            f_text_box.insert("end", letter)
        else:
            print(f"ERROR {action}")
    return handle_action
    
def key_listener_factory(keyboard, text_box, f_text_box): 
    def listener(msg):
        msg = msg.payload.decode('utf-8')
        print(msg)
        msg = msg.strip("()")
        msg = msg.replace(" ", "")
        msg = msg.replace("'", "")
        action = msg.split(",")
        print(action)
        if action[1] == "PRESSED":
            keyboard.highlight_key(action[0])
            text_box.insert("end", str(action) + " ")
        elif action[1] == "RELEASED":
            keyboard.reset_key(action[0])
            text_box.insert("end", str(action) + " ")

            letter = action[0]
            
            if letter == "SPACE":
                letter = " "
            if letter == "CONTROL":
                letter = ""

            f_text_box.insert("end", letter)
        else:
            print(f"ERROR {action}")
    return listener

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

def intro_Screen():
    
    font_path = "resources/AnonymousPro-Bold.ttf"
    hf.install_font(font_path)
    musica = hf.resource_path("resources/Intro_song.mp3")
    imagem_caminho = hf.resource_path("resources/Horus_intro.png")


    pygame.mixer.init()
    pygame.mixer.music.load(musica)
    pygame.mixer.music.play(loops=0)
    
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

    global root, frames, routines, selected_routine

    topic_handlers = {}

    frames = {}
    routines = {}

    selected_routine = None

    def set_topic_handler( topic, func):
        topic_handlers[topic] = func

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect( client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(teclas_in)

        # The callback for when a PUBLISH message is received from the server.
    def on_message( client, userdata, msg):
        topic = str(msg.topic)
        message = str(msg.payload.decode("utf-8"))
        print(topic + " " + message)
        if topic in topic_handlers:
            topic_handlers[topic](msg)

    def start_mqtt():
        global mqtt_client
        print("starting mqtt...")
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

    root = tk.Tk()    
    root.configure(bg='#252525')
    root.title("Horus")
    root.resizable(False, False)

    icon_path = "icon.ico"
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

    imagem_search_path = hf.resource_path("resources/search_icon.png")
    imagem_search = tk.PhotoImage(file=imagem_search_path)

    #Logica de estados
    
    def paint_frames(color):
        global frames

        for frame in frames:
            frames[frame].config(bg=color)

    def change_state():
        global Dom
        global Confirmar
        if Dom:
            paint_frames('#252525')
            rotinas_botoes.config(bg='#252525')
            Dom = False
            hf.on_Click_Dom_Off()
        else:
            confirm("Tem Certeza?","Sim","Não")
            if Confirmar:
                paint_frames('#502525')
                rotinas_botoes.config(bg='#502525')
                Dom = True
                hf.on_Click_Dom_On()
        
    
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

    home_Principal_GUI_keyboardInput_dump = tk.Frame(home_Principal, width=300, height=250, bd=1, relief="solid", bg="#242323")
    home_Principal_GUI_keyboardInput_dump.place(x=500,y=0)

    home_Principal_GUI_keyboardInput_realTime = tk.Frame(home_Principal, width=800, height=250, bd=1, relief="solid", bg="#242323")
    home_Principal_GUI_keyboardInput_realTime.place(x=0,y=250)
    
    home_Principal_GUI_keyboardInput_format_Text = tk.Text(home_Principal_GUI_keyboardInput_format, font=("Anonymous Pro", 11), bg="#242323", fg="white", highlightthickness=0, bd=0)
    home_Principal_GUI_keyboardInput_format_Text.pack(fill="both",expand=True)
    home_Principal_GUI_keyboardInput_format_Text.config(state="normal")

    home_Principal_GUI_keyboardInput_dump_Text = tk.Text(home_Principal_GUI_keyboardInput_dump, font=("Anonymous Pro", 11), bg="#242323", fg="white", highlightthickness=0, bd=0)
    home_Principal_GUI_keyboardInput_dump_Text.pack(fill="both",expand=True)
    home_Principal_GUI_keyboardInput_dump_Text.config(state="normal")

    keyboards["Home"] = QWERTYKeyboard(root, home_Principal_GUI_keyboardInput_realTime,110, 20)
    keyboards["Home"].set_mode("listen")

    set_topic_handler(teclas_in, key_listener_factory(keyboards["Home"], home_Principal_GUI_keyboardInput_dump_Text, home_Principal_GUI_keyboardInput_format_Text))

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
                    text= routine,
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

    schedule_routine_button = tk.Button(rotinas_botoes, text="Agendar", command=lambda: (hf.on_Click(), carrega_frame("ScheduleRoutine")), **button_Style_Sidebar)
    schedule_routine_button.place(x=0, y=90, width=300, height=70)
    schedule_routine_button.bind("<Enter>", hf.on_Enter_Sidebar)
    schedule_routine_button.bind("<Leave>", hf.on_Leave_Sidebar)

    def play_routine():
        global routines, selected_routine

        print(selected_routine)

        if selected_routine == None:
            return

        routine = routines[selected_routine]
        routine_msg = f"({selected_routine}, NOW, {routine['command']})"

        mqtt_client.publish(routine_topic, routine_msg)

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
        texto_Formatado_Frame_Text.config(state="normal")

        texto_Dump_Frame_Text = tk.Text(texto_Dump_Frame, font=("Anonymous Pro", 11), bg="#242323", fg="white", highlightthickness=0, bd=0)
        texto_Dump_Frame_Text.pack(fill="both",expand=True)
        texto_Dump_Frame_Text.config(state="normal")

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

    #Estilos dos Logs
    # FAZER A TELA DE LOG DENTRO DESTE FRAME (a parte de trocar de pagina e etc ja esta pronta)

    log_frame = tk.Frame(root, width=1030, height=720, bg="#252525")
    log_frame.place(x=250,y = 0)
    
    log_Lista = hf.ScrollableFrame(log_frame, width=300, height=550)
    log_Lista.place(x = 115,y = 85)

    log_visual = tk.Frame(log_frame, width = 415, height = 450, bd=1, relief="solid", bg="#242323")
    log_visual.place(x = 500,y = 85)

    log_lista_search = tk.Text(log_frame, font=("Anonymous Pro", 16), bg="#242323", fg="white", highlightthickness=0, bd=1, relief = "solid", state="normal")
    log_lista_search.place(x = 115, y = 40, width = 270, height = 30)
    log_lista_search.place_forget()

    log_lista_context_search = tk.Text(log_frame, font=("Anonymous Pro", 16), bg="#242323", fg="white", highlightthickness=0, bd=1, relief = "solid", state="normal")
    log_lista_context_search.place(x = 500, y = 40, width = 270, height = 30)
    log_lista_context_search.place_forget()

    log_button_search = tk.Button(log_frame, image=imagem_search, borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click(),habilitar_search_lista_logs()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_search.place(x=85,y=85,width=30,height=30)

    log_button_search_context = tk.Button(log_frame, image=imagem_search, borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click(),habilitar_search_contexto_logs()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_search_context.place(x=915,y=85,width=30,height=30)

    log_lista_search_confirm = log_button_search = tk.Button(log_frame, borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click()), width = 10, height = 2, **button_Style_Sidebar)
    log_lista_search_confirm.place(x = 385, y = 40, width = 30, height = 30)
    log_lista_search_confirm.place_forget()

    log_lista_context_search_confirm = tk.Button(log_frame, borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click()), width = 10, height = 2, **button_Style_Sidebar)
    log_lista_context_search_confirm.place(x = 770, y = 40, width = 30, height = 30)
    log_lista_context_search_confirm.place_forget()

    log_button_AI = tk.Button(log_frame, text="AI", borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_AI.place(x = 605, y = 550, width=150,height=85)

    log_button_baixar = tk.Button(log_frame, text="Download", borderwidth=0, highlightthickness=0, command=lambda: (hf.on_Click()), width = 10, height = 2, **button_Style_Sidebar)
    log_button_baixar.place(x = 765, y = 550, width=150,height=85)

    def habilitar_search_lista_logs():
        if log_lista_search.winfo_ismapped():
            log_lista_search.place_forget()
            log_lista_search_confirm.place_forget()
        else:
            log_lista_search.place(x = 115, y = 40, width = 270, height = 30)
            log_lista_search_confirm.place(x = 385, y = 40, width = 30, height = 30)

    
    def habilitar_search_contexto_logs():
        if log_lista_context_search.winfo_ismapped():
            log_lista_context_search.place_forget()
            log_lista_context_search_confirm.place_forget()
        else:
            log_lista_context_search.place(x = 500, y = 40, width = 270, height = 30)
            log_lista_context_search_confirm.place(x = 770, y = 40, width = 30, height = 30)
        return

    frames["Log"] = log_frame

    #Botoes

    home_button = tk.Button(sidebar, text="Home", command=lambda: (hf.on_Click(), carrega_frame("Home")), **button_Style_Sidebar)
    home_button.pack(pady=10, padx=10, fill="x")

    routine_button = tk.Button(sidebar, text="Rotinas", command=lambda: (hf.on_Click(), carrega_frame("Routine")), **button_Style_Sidebar)
    routine_button.pack(pady=10, padx=10, fill="x")

    log_button = tk.Button(sidebar, text="Logs", command=lambda: (hf.on_Click(), carrega_frame("Log")), **button_Style_Sidebar)
    log_button.pack(pady=10, padx=10, fill="x")

    config_button = tk.Button(sidebar, text="Configurações", command=lambda: (hf.on_Click(), teste()), **button_Style_Sidebar)
    config_button.pack(pady=10, padx=10, fill="x")
    
    #carrega_frame("Config")

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
    
    def teste():
        global routines
        for el in routines:
            print(el)

    carrega_frame("Home")

    root.mainloop()