import json #importamos o json que vai ser utilizado para salvarmos informações que queremos acesssar depois
import os #importamos a biblioteca para fazer a manipulação de arquivos

SAVE_FILE = "chat_rooms.json" #nome do arquivo em que queremos salvar as salas

def load_rooms(): #função pra carregar o arquivo
    if os.path.exists(SAVE_FILE): #se o arquivo já existe
        with open(SAVE_FILE, "r") as file:#ele vai ler o ficheiro como sendo file
            data = json.load(file) #vai fazer o load das informações desse file
            for room in data.values(): #pra sala dentro dos dados do ficheiro em que salvamos 
                for msg in room:
                    if "reactions" in msg and isinstance(msg["reactions"], list):
                        msg["reactions"] = {} #transformamos a lista em um dicionario para ser possivel de contar a quantidade de emojis que aparecerão no codigo
            return data
    return {} #caso o arquivo não exista ele retornará um dicionario vazio

def save_rooms(rooms): #função para salvar as salas
    with open(SAVE_FILE, "w") as file: #ele entra no arquivo já existente
        json.dump(rooms, file) #escreve a sala dentro desse arquivo 

#caso o arquivo não exista, quando essa função for chamada ela irá criar um artigo com o nome determinado pela gente e irá escrever as informações existentes no dicionario criado previamente pelo load