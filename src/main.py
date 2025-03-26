import flet as ft
import json
import os
import base64
from typing import Dict, List

SAVE_FILE = "chat_rooms.json"

def load_rooms():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            data = json.load(file)
            for room in data.values():
                for msg in room:
                    if "reactions" in msg and isinstance(msg["reactions"], list):
                        msg["reactions"] = {}
            return data
    return {}

def save_rooms(rooms):
    with open(SAVE_FILE, "w") as file:
        json.dump(rooms, file)

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

def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Flet Chat with Rooms"

    dark_mode = False
    page.theme_mode = ft.ThemeMode.LIGHT
    page.update()

    def toggle_theme(e):
        nonlocal dark_mode
        dark_mode = not dark_mode
        page.theme_mode = ft.ThemeMode.DARK if dark_mode else ft.ThemeMode.LIGHT
        theme_icon_button.icon = ft.icons.DARK_MODE if dark_mode else ft.icons.LIGHT_MODE
        theme_icon_button.tooltip = "Modo escuro" if dark_mode else "Modo claro"
        page.update()

    theme_icon_button = ft.IconButton(
        icon=ft.icons.LIGHT_MODE,
        tooltip="Modo escuro",
        on_click=toggle_theme,
    )

    rooms = load_rooms()
    current_room = page.session.get("room")
    user_name = page.session.get("user_name")
    room_title = ft.Text(f"Room: {current_room}" if current_room else "No room selected", size=18, weight="bold")
    room_list = ft.Column(scroll=ft.ScrollMode.AUTO, width=220)
    search_active = False

    def update_room_list():
        room_list.controls.clear()
        for room in rooms.keys():
            room_list.controls.append(
                ft.Row(
                    [
                        ft.TextButton(room, on_click=lambda e, r=room: select_room(r)),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            tooltip="Delete room",
                            on_click=lambda e, r=room: delete_room(r),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
        room_list.update()

    def select_room(room):
        nonlocal current_room, search_active
        current_room = room
        search_active = False
        page.session.set("room", current_room)
        room_title.value = f"Room: {current_room}"
        room_title.update()
        chat_container.content = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        
        if current_room in rooms:
            for message_data in rooms[current_room]:
                message = Message(**message_data)
                if message.message_type == "chat_message":
                    m = ChatMessage(
                        message, 
                        on_edit=edit_message, 
                        on_delete=delete_message,
                        on_reaction=update_reactions,
                        current_user=user_name,
                        highlight=False
                    )
                elif message.message_type == "login_message":
                    m = ft.Text(message.text, italic=True, color=ft.Colors.GREY_500, size=12)
                chat_container.content.controls.append(m)
        
        page.update()

    def update_reactions(message: Message):
        for idx, msg_data in enumerate(rooms[message.room]):
            if msg_data.get("text") == message.text and msg_data.get("user_name") == message.user_name:
                rooms[message.room][idx]["reactions"] = message.reactions
                break
        save_rooms(rooms)

    def delete_room(room):
        if room in rooms:
            del rooms[room]
            save_rooms(rooms)
            if current_room == room:
                page.session.remove("room")
                room_title.value = "No room selected"
                chat_container.content.controls.clear()
            update_room_list()
            page.update()

    def join_chat_click(e):
        nonlocal current_room, user_name
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
        else:
            user_name = join_user_name.value
            page.session.set("user_name", user_name)

            if not rooms:
                if not room_name.value:
                    room_name.error_text = "Room cannot be blank!"
                    room_name.update()
                    return
                current_room = room_name.value
                page.session.set("room", current_room)
                rooms[current_room] = []
                save_rooms(rooms)
            else:
                current_room = list(rooms.keys())[0]
                page.session.set("room", current_room)

            room_title.value = f"Room: {current_room}"
            room_title.update()
            welcome_dlg.open = False
            new_message.prefix = ft.Text(f"{user_name}: ")
            page.pubsub.send_all(Message(user_name, f"{user_name} has joined the room {current_room}.", "login_message", current_room))
            chat_container.content = ft.ListView(expand=True, spacing=10, auto_scroll=True)
            update_room_list()
            page.update()

    def create_room_click(e):
        nonlocal current_room, user_name
        if not create_room_user_name.value:
            create_room_user_name.error_text = "Name cannot be blank!"
            create_room_user_name.update()
        elif not create_room_name.value:
            create_room_name.error_text = "Room name cannot be blank!"
            create_room_name.update()
        else:
            user_name = create_room_user_name.value
            page.session.set("user_name", user_name)

            current_room = create_room_name.value
            page.session.set("room", current_room)
            rooms[current_room] = []
            save_rooms(rooms)

            room_title.value = f"Room: {current_room}"
            room_title.update()
            create_room_dlg.open = False
            new_message.prefix = ft.Text(f"{user_name}: ")
            page.pubsub.send_all(Message(user_name, f"{user_name} has created and joined the room {current_room}.", "login_message", current_room))
            chat_container.content = ft.ListView(expand=True, spacing=10, auto_scroll=True)
            update_room_list()
            page.update()

    def close_create_room_dlg():
        create_room_dlg.open = False
        page.update()

    create_room_user_name = ft.TextField(label="Enter your name", autofocus=True)
    create_room_name = ft.TextField(label="Enter new room name")
    create_room_dlg = ft.AlertDialog(
        open=False,
        modal=True,
        title=ft.Text("Create New Room"),
        content=ft.Column(
            [create_room_user_name, create_room_name],
            width=300,
            height=120,
            tight=True,
        ),
        actions=[
            ft.ElevatedButton(text="Create Room", on_click=create_room_click),
            ft.IconButton(icon=ft.icons.CLOSE, on_click=lambda e: close_create_room_dlg()),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: close_create_room_dlg(),
    )

    def create_new_room(e): 
        create_room_dlg.open = True
        if create_room_dlg not in page.overlay:
            page.overlay.append(create_room_dlg)
        page.update()

    def send_message_click(e):
        if new_message.value and current_room:
            message = Message(
                user_name,
                new_message.value,
                message_type="chat_message",
                room=current_room,
            )
            page.pubsub.send_all(message)
            
            rooms[current_room].append(message.__dict__)
            save_rooms(rooms)
            
            new_message.value = ""
            new_message.focus()
            page.update()

    def on_file_pick(e: ft.FilePickerResultEvent):
        if e.files and current_room:
            for file in e.files:
                with open(file.path, "rb") as f:
                    file_data = base64.b64encode(f.read()).decode("utf-8")
                message = Message(
                    user_name,
                    "",
                    message_type="chat_message",
                    room=current_room,
                    file_data=file_data,
                    file_name=file.name,
                )
                page.pubsub.send_all(message)
                rooms[current_room].append(message.__dict__)
                save_rooms(rooms)
            page.update()

    file_picker = ft.FilePicker(on_result=on_file_pick)
    page.overlay.append(file_picker)

    def edit_message(message: Message):
        def on_edit(e):
            new_text = ft.TextField(value=message.text, autofocus=True)
            edit_dlg = ft.AlertDialog(
                open=True,
                modal=True,
                title=ft.Text("Edit Message"),
                content=new_text,
                actions=[
                    ft.ElevatedButton(
                        text="Save",
                        on_click=lambda e: save_edit(message, new_text.value),
                    ),
                    ft.ElevatedButton(
                        text="Cancel",
                        on_click=lambda e: close_edit_dlg()),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.overlay.append(edit_dlg)
            page.update()
    
        def save_edit(message: Message, new_text: str):
            for idx, msg in enumerate(rooms[message.room]):
                if isinstance(msg, dict) and msg.get("text") == message.text and msg.get("user_name") == message.user_name:
                    msg["text"] = new_text
                    break
                elif isinstance(msg, Message) and msg.text == message.text and msg.user_name == message.user_name:
                    msg.text = new_text
                    rooms[message.room][idx] = msg.__dict__
                    break
                
            save_rooms(rooms)
            close_edit_dlg()
            select_room(message.room)
    
        def close_edit_dlg():
            page.overlay.pop()
            page.update()
    
        on_edit(None)

    def delete_message(message: Message):
        def on_delete(e):
            rooms[message.room] = [msg for idx, msg in enumerate(rooms[message.room]) if idx != message_index(message)]
            save_rooms(rooms)
            select_room(message.room)

        def message_index(message: Message):
            for idx, msg in enumerate(rooms[message.room]):
                if isinstance(msg, dict) and msg.get("text") == message.text and msg.get("user_name") == message.user_name:
                    return idx
                elif isinstance(msg, Message) and msg.text == message.text and msg.user_name == message.user_name:
                    return idx
            return -1

        on_delete(None)

    def on_message(message: Message):
        if message.room in rooms:
            if message.message_type == "chat_message":
                m = ChatMessage(
                    message, 
                    on_edit=edit_message, 
                    on_delete=delete_message,
                    on_reaction=update_reactions,
                    current_user=user_name,
                    highlight=False
                )
            elif message.message_type == "login_message":
                m = ft.Text(message.text, italic=True, color=ft.Colors.GREY_500, size=12)
            chat_container.content.controls.append(m)
            page.update()

    page.pubsub.subscribe(on_message)

    # Search functionality
    search_query = ft.TextField(label="Search for...", autofocus=True)
    search_active = False

    def open_search(e):
        search_dialog.open = True
        page.update()

    def perform_search(e):
        nonlocal search_active
        query = search_query.value.strip().lower()
        
        if not query or not current_room:
            return

        search_active = True
        chat_container.content.controls.clear()
        
        for message_data in rooms[current_room]:
            message = Message(**message_data)
            matches = query in message.text.lower() or query in message.user_name.lower()
            
            if message.message_type == "chat_message":
                m = ChatMessage(
                    message, 
                    on_edit=edit_message, 
                    on_delete=delete_message,
                    on_reaction=update_reactions,
                    current_user=user_name,
                    highlight=matches
                )
            elif message.message_type == "login_message":
                m = ft.Text(message.text, italic=True, color=ft.Colors.GREY_500, size=12)
            
            chat_container.content.controls.append(m)
        
        search_dialog.open = False
        page.update()

    def clear_search(e):
        nonlocal search_active
        search_active = False
        search_query.value = ""
        select_room(current_room)
        page.update()

    def close_dialog(e):
        search_dialog.open = False
        page.update()

    search_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Search Messages"),
        content=ft.Column(
            [
                search_query,
            ],
            width=400,
        ),
        actions=[
            ft.TextButton("Search", on_click=perform_search),
            ft.TextButton("Clear", on_click=clear_search),
            ft.TextButton("Close", on_click=close_dialog),
        ],
    )
    page.overlay.append(search_dialog)

    join_user_name = ft.TextField(label="Enter your name", autofocus=True)
    room_name = ft.TextField(label="Enter room name", visible=not rooms)
    welcome_dlg = ft.AlertDialog(
        open=not user_name,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column(
            [join_user_name, room_name] if not rooms else [join_user_name],
            width=300,
            height=120 if not rooms else 80,
            tight=True,
        ),
        actions=[ft.ElevatedButton(text="Join Room", on_click=join_chat_click)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    if not user_name:
        page.overlay.append(welcome_dlg)

    chat_container = ft.Container(
        content=ft.ListView(expand=True, spacing=10, auto_scroll=True),
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=5,
        padding=10,
        expand=True,
    )

    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    page.add(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.ElevatedButton(text="Create New Room", on_click=create_new_room),
                                theme_icon_button,
                                ft.IconButton(
                                    icon=ft.icons.SEARCH,
                                    tooltip="Search messages",
                                    on_click=open_search,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        room_list,
                    ],
                    width=220,
                    scroll=ft.ScrollMode.AUTO,
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Column(
                    [
                        room_title,
                        chat_container,
                        ft.Row(
                            [
                                new_message,
                                ft.IconButton(icon=ft.Icons.SEND_ROUNDED, tooltip="Send message", on_click=send_message_click),
                                ft.IconButton(icon=ft.icons.ATTACH_FILE, tooltip="Send file", on_click=lambda e: file_picker.pick_files(allow_multiple=True)),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        )
    )

    update_room_list()

ft.app(target=main)