import flet as ft
from typing import Dict, List


class Message:
    def __init__(self, user_name: str, text: str, message_type: str, room: str, 
                 file_data=None, file_name=None, reactions: Dict[str, List[str]] = None):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.room = room
        self.file_data = file_data
        self.file_name = file_name
        self.reactions = reactions or {}

    def add_reaction(self, emoji: str, user_name: str):
        if emoji not in self.reactions:
            self.reactions[emoji] = []
        if user_name not in self.reactions[emoji]:
            self.reactions[emoji].append(user_name)
    
    def remove_reaction(self, emoji: str, user_name: str):
        if emoji in self.reactions and user_name in self.reactions[emoji]:
            self.reactions[emoji].remove(user_name)
            if not self.reactions[emoji]:
                del self.reactions[emoji]

class ChatMessage(ft.Row):
    def __init__(self, message: Message, on_edit, on_delete, on_reaction, current_user: str, highlight: bool = False):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.message = message
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_reaction = on_reaction
        self.current_user = current_user
        self.highlight = highlight
        self.emoji_picker = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(text="👍", on_click=lambda e: self.add_or_remove_reaction("👍")),
                ft.PopupMenuItem(text="❤️", on_click=lambda e: self.add_or_remove_reaction("❤️")),
                ft.PopupMenuItem(text="😂", on_click=lambda e: self.add_or_remove_reaction("😂")),
                ft.PopupMenuItem(text="😮", on_click=lambda e: self.add_or_remove_reaction("😮")),
                ft.PopupMenuItem(text="😢", on_click=lambda e: self.add_or_remove_reaction("😢")),
                ft.PopupMenuItem(text="🎉", on_click=lambda e: self.add_or_remove_reaction("🎉")),
            ]
        )

        self.build_controls()

    def build_controls(self):
        bg_color = ft.colors.AMBER_100 if self.highlight else None
        border = ft.border.all(2, ft.colors.AMBER_400) if self.highlight else None
        
        message_content = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(self.message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(self.message.user_name),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text(self.message.user_name, weight="bold"),
                        ft.Text(self.message.text, selectable=True),
                    ],
                    tight=True,
                    spacing=5,
                ),
                bgcolor=bg_color,
                border=border,
                border_radius=5,
                padding=5,
            ),
            ft.Row(
                [
                    self.emoji_picker,
                    ft.IconButton(
                        icon=ft.icons.EDIT,
                        tooltip="Edit",
                        on_click=self.edit_message,
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        tooltip="Delete",
                        on_click=self.delete_message,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
        ]

        if self.message.file_data:
            if self.message.file_name.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                file_control = ft.Image(
                    src_base64=self.message.file_data,
                    width=300,
                    height=200,
                    fit=ft.ImageFit.CONTAIN,
                )
            else:
                file_control = ft.Text(f"File: {self.message.file_name}", color=ft.Colors.BLUE, selectable=True)
            message_content[1].content.controls.append(file_control)

        if self.message.reactions:
            reactions_row = ft.Row(wrap=True, spacing=5)
            for emoji, users in self.message.reactions.items():
                count = len(users)
                reacted = self.current_user in users
                reactions_row.controls.append(
                    ft.TextButton(
                        content=ft.Row([
                            ft.Text(emoji),
                            ft.Text(str(count), size=12)
                        ], spacing=2),
                        style=ft.ButtonStyle(
                            color=ft.colors.BLUE if reacted else None,
                            bgcolor=ft.colors.BLUE_100 if reacted else ft.colors.GREY_200,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        ),
                        on_click=lambda e, emoji=emoji: self.add_or_remove_reaction(emoji),
                    )
                )
            message_content[1].content.controls.append(reactions_row)

        self.controls = message_content

    def add_or_remove_reaction(self, emoji: str):
        if emoji in self.message.reactions and self.current_user in self.message.reactions[emoji]:
            self.message.remove_reaction(emoji, self.current_user)
        else:
            self.message.add_reaction(emoji, self.current_user)
        self.on_reaction(self.message)
        self.build_controls()
        self.update()

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize()

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.Colors.AMBER, ft.Colors.BLUE, ft.Colors.BROWN, ft.Colors.CYAN,
            ft.Colors.GREEN, ft.Colors.INDIGO, ft.Colors.LIME, ft.Colors.ORANGE,
            ft.Colors.PINK, ft.Colors.PURPLE, ft.Colors.RED, ft.Colors.TEAL, ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

    def edit_message(self, e):
        self.on_edit(self.message)

    def delete_message(self, e):
        self.on_delete(self.message)