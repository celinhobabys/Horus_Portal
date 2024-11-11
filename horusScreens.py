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

keyboards = {}

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

def gravar():

    global state, root
    state = False

    def destruir():
        gravar.destroy()
    
    gravar = tk.Toplevel()
    gravar.configure(bg='#2e2b2b')
    gravar.resizable(False, False)
    gravar.overrideredirect(True)
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

    button = tk.Button(gravar, text="Gravar", width = 10, height = 2, **button_Style)
    button.place(x=800, y=350, width = 300 , height = 150)
    
    def toggle_record():
        global state
        if state:
            destruir()
        else:
            button.config(text="Parar", bg="#a1392d",activebackground="#943a2f")
            state = True
    
    button.config(command=toggle_record)

    gravar.wait_window(gravar)

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

    global root

    teclas_in = "teclado_espiao/teclas_in"
    topic_handlers = {}

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
        step_mqtt()

    def step_mqtt():
        global mqtt_client
        mqtt_client.loop_read()
        mqtt_client.loop_write()
        mqtt_client.loop_misc()
        root.after(20, step_mqtt)

    root = tk.Tk()    
    root.configure(bg='green')
    root.title("Horus")
    root.resizable(False, False)

    icon_path = "icon.ico"
    root.iconbitmap(icon_path)

    hf.centralize_Window(root)

    start_mqtt()

    #Globais

    global Confirmar
    global Dom
    global NameText
    global ContextText

    Dom = False

    #Logica de estados
    
    def change_state():
        global Dom
        global Confirmar
        if Dom:
            user_Area.config(bg='#252525')
            rotinas_botoes.config(bg='#252525')
            Dom = False
            hf.on_Click_Dom_Off()
        else:
            confirm("Tem Certeza?","Sim","Não")
            if Confirmar:
                user_Area.config(bg='#502525')
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

    user_Area = tk.Frame(root, width=1030, height=720, bg="#252525")
    user_Area.place(x=250,y = 0)

    #Estilos da Home

    home_Principal = tk.Frame(user_Area, width=801, height=550, bd=1, relief="solid", bg="#3a3a3a")
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

    set_topic_handler(teclas_in, key_listener_factory(keyboards["Home"], home_Principal_GUI_keyboardInput_dump_Text, home_Principal_GUI_keyboardInput_format_Text))

    #Estilo das Rotinas
    
    rotinas_Lista = hf.ScrollableFrame(user_Area, width=400, height=550)
    rotinas_Lista.place(x = 115,y = 85)

    rotinas_Detalhes = tk.Frame(user_Area, width=300, height=250, bd=1, relief="solid", bg="#242323")
    rotinas_Detalhes.pack_propagate(False)
    rotinas_Detalhes_Text = tk.Text(rotinas_Detalhes, font=("Anonymous Pro", 11), bg="#252525", fg="white", highlightthickness=0, bd=0)
    rotinas_Detalhes_Text.pack(fill="both",expand=True)
    rotinas_Detalhes_Text.config(state="disabled")
    rotinas_Detalhes.place(x=615,y=85)

    rotinas_botoes = tk.Frame(user_Area, width=300, height=250, bg="#252525")
    rotinas_botoes.place(x = 615, y = 388)
    
    #Estilo da Criar - Texto

    criar_Nome_Label = tk.Label(user_Area, text="Nome: ", font=("Anonymous Pro", 20, "bold"), bg = "#252525", fg = "white")
    criar_Nome_Label.place(x=115, y = 85)

    criar_Nome = tk.Text(user_Area, font=("Anonymous Pro", 16), bg="#252525", fg="white", highlightthickness=0, bd=0)
    criar_Nome.place(x=200, y = 90, width = 700, height = 35)

    criar_Nome_Linha = tk.Frame(user_Area, bg = "#000")
    criar_Nome_Linha.place(x=200, y = 115, width = 700, height = 2)

    criar_Contexto_Label = tk.Label(user_Area, text="Contexto: ", font=("Anonymous Pro", 20, "bold"), bg = "#252525", fg = "white")
    criar_Contexto_Label.place(x=115, y = 200)

    criar_Contexto = tk.Text(user_Area, font=("Anonymous Pro", 16), bg="#242323", fg="white", highlightthickness=0, bd=1, relief = "solid")
    criar_Contexto.place(x = 115, y = 250, width = 800, height = 300)

    #Estilos dos Logs



    #Botoes

    button1 = tk.Button(sidebar, text="Home", command=lambda: (hf.on_Click(), carregar_Home()), **button_Style_Sidebar)
    button1.pack(pady=10, padx=10, fill="x")

    button2 = tk.Button(sidebar, text="Rotinas", command=lambda: (hf.on_Click(), carregar_Rotinas()), **button_Style_Sidebar)
    button2.pack(pady=10, padx=10, fill="x")

    button3 = tk.Button(sidebar, text="Logs", command=lambda: (hf.on_Click(), carregar_Logs()), **button_Style_Sidebar)
    button3.pack(pady=10, padx=10, fill="x")

    button4 = tk.Button(sidebar, text="Configurações", command=lambda: (hf.on_Click(), carregar_configuracoes()), **button_Style_Sidebar)
    button4.pack(pady=10, padx=10, fill="x")

    button5 = tk.Button(user_Area, text="Dominar", command=change_state, width = 10, height = 2, **button_Style_Domidar)
    button5.place(relx=0.5, y=15, anchor="n")

    button6 = tk.Button(rotinas_botoes, text="Criar", command=lambda: (hf.on_Click(), carregar_Criar()), **button_Style_Sidebar)
    button6.place(x=0, y=0, width=300, height=70)

    button7 = tk.Button(rotinas_botoes, text="Agendar", command=lambda: (hf.on_Click(), carregar_configuracoes()), **button_Style_Sidebar)
    button7.place(x=0, y=90, width=300, height=70)

    button8 = tk.Button(rotinas_botoes, text="Play", command=lambda: (hf.on_Click(), carregar_configuracoes()), **button_Style_Sidebar)
    button8.place(x=0, y=180, width=300, height=70)

    button9 = tk.Button(user_Area, text = "Criar", command=lambda: (hf.on_Click(), submit_text()), width = 10, height = 2, **button_Style_Sidebar)
    button9.place(x=715,y=575, width= 200, height= 50)

    button10 = tk.Button(user_Area, text = "Gravar", command=lambda: (hf.on_Click(), gravar()), width = 10, height = 2, **button_Style_Domidar,)
    button10.place(x=465,y=575, width= 200, height= 50)

    buttons_sidebar = [
        button1, 
        button2, 
        button3, 
        button4,
        button5,
        button6,
        button7,
        button8,
        button9,
        button10
    ]
    
    for button in buttons_sidebar:
        button.bind("<Enter>", hf.on_Enter_Sidebar)
        button.bind("<Leave>", hf.on_Leave_Sidebar)

    button5.bind("<Enter>", hf.on_Enter_Dominar)
    button5.bind("<Leave>", hf.on_Leave_Dominar)
    button10.bind("<Enter>", hf.on_Enter_Dominar)
    button10.bind("<Leave>", hf.on_Leave_Dominar)

    #Troca de paginas

    def limpar_User_Area():
        elementos_lista = [
            home_Principal,
            button5,
            rotinas_Lista,
            rotinas_Detalhes,
            rotinas_botoes,
            criar_Nome_Label,
            criar_Nome,
            criar_Nome_Linha,
            criar_Contexto_Label,
            criar_Contexto,
            button9,
            button10
        ]

        for elemento in elementos_lista:
            elemento.place_forget()

        criar_Nome.delete("1.0",tk.END)
        criar_Contexto.delete("1.0",tk.END)


    def carregar_Home():
        limpar_User_Area()
        home_Principal.place(x = 115,y = 85)
        button5.place(relx=0.5, y=15, anchor="n")
    
    def carregar_Rotinas():
        limpar_User_Area()
        rotinas_Lista.place(x = 115,y = 85)
        rotinas_Detalhes.place(x=615,y=85)
        rotinas_botoes.place(x = 615, y = 388)

    def carregar_Logs():
        limpar_User_Area()

    def carregar_configuracoes():
        limpar_User_Area()

    def carregar_Criar():
        limpar_User_Area()
        criar_Nome_Label.place(x=115, y = 85)
        criar_Nome.place(x=200, y = 90, width = 700, height = 35)
        criar_Nome_Linha.place(x=200, y = 115, width = 700, height = 2)
        criar_Contexto_Label.place(x=115, y = 200)
        criar_Contexto.place(x = 115, y = 250, width = 800, height = 300)
        button9.place(x=715,y=575, width= 200, height= 50)
        button10.place(x=465,y=575, width= 200, height= 50)

    limpar_User_Area()

    def submit_text():
        global NameText
        global ContextText
        global Confirmar
        confirm("Tem Certeza?","Sim","Não")
        if Confirmar:
            NameText = criar_Nome.get("1.0", tk.END).strip()
            ContextText = criar_Contexto.get("1.0", tk.END).strip()
            adicionar_Item()
            carregar_Rotinas()

    def adicionar_Item():
        global NameText
        global ContextText
        if NameText:
            button = tk.Button(
                rotinas_Lista.scrollable_frame,
                text=NameText,
                command=lambda c=ContextText: mostrar_contexto(c),
                **button_Style_Sidebar
            )
            button.pack(pady=5, padx=0, fill="x", expand=True)

    def mostrar_contexto(contexto):
        rotinas_Detalhes_Text.config(state="normal")
        rotinas_Detalhes_Text.delete('1.0', tk.END)
        rotinas_Detalhes_Text.insert(tk.END, contexto)
        rotinas_Detalhes_Text.config(state="disabled")

    root.mainloop()