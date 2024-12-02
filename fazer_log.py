superstring = ""
with open("texto_raw.txt",'r', encoding="utf-8") as arq:
    texto = arq.read()
superstring = texto.replace('#', '').replace('\n', '')
print(superstring)