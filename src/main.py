import flet as ft
import json
import os

SAVE_FILE = "chat_rooms.json"

def load_rooms():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return json.load(file)
    return {}

def save_rooms(rooms):
    with open(SAVE_FILE, "w") as file:
        json.dump(rooms, file)

class Message:
    def __init__(self, user_name: str, text: str, message_type: str, room: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type
        self.room = room

class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.Colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize() if user_name else "Unknown"

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.Colors.AMBER, ft.Colors.BLUE, ft.Colors.BROWN, ft.Colors.CYAN,
            ft.Colors.GREEN, ft.Colors.INDIGO, ft.Colors.LIME, ft.Colors.ORANGE,
            ft.Colors.PINK, ft.Colors.PURPLE, ft.Colors.RED, ft.Colors.TEAL, ft.Colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]

def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.title = "Flet Chat with Rooms"

    rooms = load_rooms()
    current_room = page.session.get("room")
    user_name = page.session.get("user_name")
    room_title = ft.Text(f"Room: {current_room}" if current_room else "No room selected", size=18, weight="bold")
    room_list = ft.Column(scroll=ft.ScrollMode.AUTO, width=220) 

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
        nonlocal current_room
        current_room = room
        page.session.set("room", current_room)
        room_title.value = f"Room: {current_room}"
        room_title.update()
        chat_container.content = ft.ListView(expand=True, spacing=10, auto_scroll=True)
        
        if current_room in rooms:
            for message_data in rooms[current_room]:
                message = Message(**message_data)
                if message.message_type == "chat_message":
                    m = ChatMessage(message)
                elif message.message_type == "login_message":
                    m = ft.Text(message.text, italic=True, color=ft.Colors.BLACK45, size=12)
                chat_container.content.controls.append(m)
        
        page.update()

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

    def create_new_room(e):
        create_room_dlg.open = True
        if create_room_dlg not in page.overlay:
            page.overlay.append(create_room_dlg)
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

    def on_message(message: Message):
        if message.room in rooms:
            if message.message_type == "chat_message":
                m = ChatMessage(message)
            elif message.message_type == "login_message":
                m = ft.Text(message.text, italic=True, color=ft.Colors.BLACK45, size=12)
            chat_container.content.controls.append(m)
            page.update()

    page.pubsub.subscribe(on_message)

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
        actions=[ft.ElevatedButton(text="Create Room", on_click=create_room_click)],
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
                        ft.ElevatedButton(text="Create New Room", on_click=create_new_room),
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