import flet as ft
from typing import Dict, List
from dataclasses import dataclass, field
import time

@dataclass
class Message:
    user_name: str
    text: str
    message_type: str
    room: str
    file_data: str = None
    file_name: str = None
    reactions: Dict[str, List[str]] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: time.time())

    def add_reaction(self, emoji: str, user_name: str) -> bool:
        if emoji not in self.reactions:
            self.reactions[emoji] = []
        if user_name not in self.reactions[emoji]:
            self.reactions[emoji].append(user_name)
            return True
        return False

    def remove_reaction(self, emoji: str, user_name: str) -> bool:
        if emoji in self.reactions and user_name in self.reactions[emoji]:
            self.reactions[emoji].remove(user_name)
            if not self.reactions[emoji]:
                del self.reactions[emoji]
            return True
        return False

    def to_dict(self):
        return {
            'user_name': self.user_name,
            'text': self.text,
            'message_type': self.message_type,
            'room': self.room,
            'file_data': self.file_data,
            'file_name': self.file_name,
            'reactions': self.reactions,
            'timestamp': self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            user_name=data['user_name'],
            text=data['text'],
            message_type=data['message_type'],
            room=data['room'],
            file_data=data.get('file_data'),
            file_name=data.get('file_name'),
            reactions=data.get('reactions', {}),
            timestamp=data.get('timestamp', time.time())
        )

class ChatMessage(ft.Row):
    def __init__(self, message: Message, on_edit, on_delete, on_reaction, current_user: str, highlight: bool = False):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.spacing = 10
        self.message = message
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_reaction = on_reaction
        self.current_user = current_user
        self.highlight = highlight
        
        self.build_controls()

    def build_controls(self):
        bg_color = ft.colors.AMBER_100 if self.highlight else None
        border = ft.border.all(2, ft.colors.AMBER_400) if self.highlight else None
        
        message_content = ft.Column(
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

        if self.message.file_data:
            if self.message.file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                file_control = ft.Image(
                    src_base64=self.message.file_data,
                    width=300,
                    height=200,
                    fit=ft.ImageFit.CONTAIN,
                )
            else:
                file_control = ft.TextButton(
                    text=f"📄 {self.message.file_name}",
                    on_click=self.download_file,
                )
            message_content.controls.append(file_control)

        if self.message.reactions:
            reactions_row = ft.Row(
                wrap=True, 
                spacing=5,
                run_spacing=5,
            )
            
            for emoji, users in sorted(self.message.reactions.items()):
                count = len(users)
                has_reacted = self.current_user in users
                
                reaction_btn = ft.TextButton(
                    content=ft.Row([
                        ft.Text(emoji),
                        ft.Text(str(count), size=10)
                    ], spacing=2),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                        bgcolor=ft.colors.BLUE_100 if has_reacted else ft.colors.GREY_200,
                        overlay_color=ft.colors.TRANSPARENT,
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

    def format_timestamp(self):
        now = time.time()
        diff = now - self.message.timestamp
        if diff < 60:
            return "agora"
        elif diff < 3600:
            return f"{int(diff/60)} min atrás"
        elif diff < 86400:
            return f"{int(diff/3600)} h atrás"
        else:
            return time.strftime("%d/%m/%Y", time.localtime(self.message.timestamp))