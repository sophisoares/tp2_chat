import flet as ft #importa flet como sendo ft
from typing import Dict, List 
from dataclasses import dataclass, field
import time 

@dataclass #decorador que nos permite utilizar o init sem que escrevemos ele a mão, atributo por atributo
class Message: 
    user_name: str #so definimos o valor que será dado a cada um dos atributos
    text: str
    message_type: str
    room: str
    file_data: str = None #pro conteudo do arquivo que analisaremos depois, ou no caso se não houver nenhum conteudo
    file_name: str = None #pro nome do arquivo que for anexado e analisaremos depois no arquivo main com o base 64
    reactions: Dict[str, List[str]] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: time.time())

    def add_reaction(self, emoji: str, user_name: str) -> bool: #adiciona uma reação, caso a operação seja feita de forma correta passará um valor em booleano, true ou false
        if emoji not in self.reactions: #se o emoji não estiver dentro do dicionario de reação (lembrando que o emoji é uma chave)
            self.reactions[emoji] = [] #ele cria um espaço para que essa chave de emoji seja armazenada
        if user_name not in self.reactions[emoji]: #verifica se o nome do usuario não está no espaço dedicado a chave de emoji
            self.reactions[emoji].append(user_name) #se não houver e a pessoa tiver interagido com o emoji, será feito o append do nome dela
            return True #se tudo for feito de forma correta, retornará true
        return False #caso contrário retorna false

    def remove_reaction(self, emoji: str, user_name: str) -> bool: #o mesmo esquema se seguirá nessa função
        if emoji in self.reactions and user_name in self.reactions[emoji]: #verifica se já existe aquele emoji no ambiente das reações, e tambem se tem o nome de usuario, indicando que houve interação com o emoji
            self.reactions[emoji].remove(user_name) #faz a remoção do nome do usuario vinculada com aquele emoji
            if not self.reactions[emoji]: #verifica se a chave do emoji contem algum nome, indicando que mais uma pessoa interagiu com ele 
                del self.reactions[emoji] #se não houver ele apaga aquele espaço dedicado ao emoji
            return True #se tudo ocorrer bem retorna true
        return False #caso contrario retorna false

    def to_dict(self): #transforma um objeto da classe em um dicionario, no nosso caso será para trabalhar posteriormente com o arquivo em json
        return {
            'user_name': self.user_name,
            'text': self.text,
            'message_type': self.message_type, #varia entre ser text ou o file
            'room': self.room,
            'file_data': self.file_data,
            'file_name': self.file_name,
            'reactions': self.reactions,
            'timestamp': self.timestamp #determina o momento em que a mensagem foi criada
        }

    @classmethod #decorador que possibilita primeiramente referenciar a classe ao inves de uma instancia da mesma para poder ser feita a criação de objeto
    def from_dict(cls, data):
        return cls(
            user_name=data['user_name'], #são valores obrigatorios
            text=data['text'],
            message_type=data['message_type'],
            room=data['room'],
            file_data=data.get('file_data'), #ja esses pode ocorrer de não existirem então por isso irão retornar none ou qualquer coisa desse genero
            file_name=data.get('file_name'),
            reactions=data.get('reactions', {}),
            timestamp=data.get('timestamp', time.time()) #caso o timestamp não exista ele ainda cria um novo timestamp, para garantir que o objeto tenha um valor valido
        )

#não utiliza o decorador do dataclass por estár herdando o init da classe ft.Row que é do flet e utilizaremos para mexer com a parte visual do trabalho
class ChatMessage(ft.Row):
    def __init__(self, message: Message, on_edit, on_delete, on_reaction, current_user: str, highlight: bool = False):
        super().__init__() # quando utilizamos o super, pedimos para que a classe passe as configurações bases e a partir dela conseguimos fazer modificações com base naquilo que queremos e precisamos
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.spacing = 10
        self.message = message
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_reaction = on_reaction
        self.current_user = current_user
        self.highlight = highlight
        
        self.build_controls() #metodo que vai construir visualemnte os elementos da mensagem, quando o atributo highlight for true

    def build_controls(self): #contorna e modifica a cor da mensagem quando ela for encontrada no momento do search
        bg_color = ft.colors.AMBER_100 if self.highlight else None 
        border = ft.border.all(2, ft.colors.AMBER_400) if self.highlight else None
        
        message_content = ft.Column( #define a construção visual da mensagem
            spacing=5,
            tight=True,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(self.message.user_name, weight="bold"),
                        ft.Text(self.format_timestamp(), size=12, color=ft.colors.GREY),
                    ],
                    spacing=10,
                ),
                ft.Text(self.message.text, selectable=True),
            ]
        )

        if self.message.file_data: #verifica se a mensagem te um arquivo de imagem
            if self.message.file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')): #verifica a extenção do arquivo
                file_control = ft.Image(
                    src_base64=self.message.file_data,
                    width=300,
                    height=200,
                    fit=ft.ImageFit.CONTAIN,
                ) #se o arquivo for uma das extenções definidas a mensagem é ajustada as dimensões definidas, utilizando o contain para manter as propoções
            else:
                file_control = ft.TextButton( #se o arquivo não for uma mensagem, exemplo pdf ele mostra um botão com a funcionalidade de fazer o download do arquivo
                    text=f"📄 {self.message.file_name}",
                    on_click=self.download_file,
                )
            message_content.controls.append(file_control)

        if self.message.reactions: #verifica se a mensagem tem reações se não de contrario n faz nada
            reactions_row = ft.Row(
                wrap=True, #se não houver espaço sufiente, as reações podem quebrar para outras linhas
                spacing=5, #espaçamento entre controles
                run_spacing=5,
            )
            
            for emoji, users in sorted(self.message.reactions.items()): #ordena a aparição dos emojis por ordem alfabetica
                count = len(users) #conta quantas pessoas reagiram com aquele emoji
                has_reacted = self.current_user in users #verifica se o usuario atual interagiu com o emoji, caso sim a reação ficará azul, caso contrário se manterá cinza
                
                reaction_btn = ft.TextButton( #cria botão para mostrar as reações emoji+quantidade
                    content=ft.Row([ #aqui definimos o conteudo do botçao que será o emoji em si e a quantidade de vezes em que ele aparece
                        ft.Text(emoji),
                        ft.Text(str(count), size=10)
                    ], spacing=2),
                    style=ft.ButtonStyle( #aqui definimos a estrutura do botão
                        shape=ft.RoundedRectangleBorder(radius=10), #formato
                        padding=ft.padding.symmetric(horizontal=6, vertical=2), #espaçamento
                        bgcolor=ft.colors.BLUE_100 if has_reacted else ft.colors.GREY_200, #cor de fundo
                        overlay_color=ft.colors.TRANSPARENT, #desativa efeito visual do botão
                    ),
                    on_click=lambda e, emoji=emoji: self.toggle_reaction(emoji),
                    tooltip=f"{', '.join(users)}" if users else None,
                )
                reactions_row.controls.append(reaction_btn)
            
            message_content.controls.append(reactions_row)

        reaction_picker = ft.PopupMenuButton(
            icon=ft.icons.ADD_REACTION_OUTLINED,
            tooltip="Add reaction",
            items=[
                ft.PopupMenuItem(
                    text=emoji,
                    on_click=lambda e, emoji=emoji: self.toggle_reaction(emoji)
                ) for emoji in ["👍", "❤️", "😂", "😮", "😢", "🎉"]
            ]
        )

        action_buttons = ft.Row(
            controls=[
                reaction_picker,
                ft.IconButton(
                    icon=ft.icons.EDIT,
                    tooltip="Edit",
                    on_click=lambda e: self.on_edit(self.message),
                    visible=self.message.user_name == self.current_user,
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE,
                    tooltip="Delete",
                    on_click=lambda e: self.on_delete(self.message),
                    visible=self.message.user_name == self.current_user,
                ),
            ],
            spacing=5,
        )

        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(self.message.user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(self.message.user_name),
            ),
            ft.Column(
                controls=[
                    ft.Container(
                        content=message_content,
                        bgcolor=bg_color,
                        border=border,
                        border_radius=10,
                        padding=10,
                    ),
                    ft.Container(
                        content=action_buttons,
                        padding=ft.padding.only(left=10),
                    )
                ],
                spacing=5,
            )
        ]

    def toggle_reaction(self, emoji: str):
        if emoji in self.message.reactions and self.current_user in self.message.reactions[emoji]:
            self.message.remove_reaction(emoji, self.current_user)
        else:
            self.message.add_reaction(emoji, self.current_user)
        
        self.on_reaction(self.message)

    def get_initials(self, name: str):
        return ''.join([part[0].upper() for part in name.split()[:2]])

    def get_avatar_color(self, name: str):
        colors = [
            ft.colors.AMBER, ft.colors.BLUE, ft.colors.BROWN, ft.colors.CYAN,
            ft.colors.GREEN, ft.colors.INDIGO, ft.colors.LIME, ft.colors.ORANGE,
            ft.colors.PINK, ft.colors.PURPLE, ft.colors.RED, ft.colors.TEAL, 
            ft.colors.YELLOW, ft.colors.DEEP_ORANGE, ft.colors.DEEP_PURPLE,
        ]
        return colors[hash(name) % len(colors)]

    def format_timestamp(self): #essa função é pra mostrar em que momento a mensagem foi enviada
        now = time.time() #pegamos tempo atual da conversa
        diff = now - self.message.timestamp #subtraimos pelo tempo que foi registrado no momento em que a mensagem foi enviada 
        if diff < 60: #até 1 min
            return "agora"
        elif diff < 3600:
            return f"{int(diff/60)} min atrás" #1hora
        elif diff < 86400:
            return f"{int(diff/3600)} h atrás" #24 horas
        else:
            return time.strftime("%d/%m/%Y", time.localtime(self.message.timestamp)) #quando passa das 24 horas mostramos o o dia em que a mensagem foi enviada