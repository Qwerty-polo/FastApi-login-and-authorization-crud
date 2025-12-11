from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

# Використовуємо APIRouter, щоб підключити це до main.py
router = APIRouter()

# --- База де лежать усі зєднання всі сайти які зайшли на нашу апі ---
class ConnectionManager:
    def __init__(self):
        # Тут ми зберігаємо список всіх підключених "кухарів"
        self.active_connections: List[WebSocket] = []

    #приймає нові сайти які заходять і записує у нашу базу список
    async def connect(self, websocket: WebSocket):
        # Приймаємо з'єднання
        await websocket.accept()
        # Додаємо кухаря в список
        self.active_connections.append(websocket)

    #якшо хтось вийшов то ми його зразу викреслюєм з нашої бази списку
    def disconnect(self, websocket: WebSocket):
        # Якщо кухар пішов - видаляємо зі списку
        self.active_connections.remove(websocket)

    #проходимся по всім нашим сайтам і кожному відправляєм повідомлення ро замовлення
    async def broadcast(self, message: str):
        # Ця функція найважливіша!
        # Вона біжить по списку active_connections і кожному відправляє повідомлення
        for connection in self.active_connections:
            await connection.send_text(message)

#Коротко: Цей рядок створює єдиний спільний "блокнот", у який всі записуються і з якого всі читають.
# Якби цього рядка не було, або він був би в іншому місці — у кожного був би свій власний пустий блокнот,
# і магія б не спрацювала.
manager = ConnectionManager()

# --- ЕНДПОІНТ (Куди стукають кухарі) ---
@router.websocket("/ws/kitchen")
async def websocket_endpoint(websocket: WebSocket):
    # Як тільки хтось зайшов - реєструємо його
    await manager.connect(websocket)
    try:
        while True:
            # Тримаємо канал відкритим (слухаємо)
            # Кухар зазвичай мовчить, але нам треба while True, щоб зв'язок не розірвався
            await websocket.receive_text()
    except WebSocketDisconnect:
        # Якщо з'єднання розірвалось - видаляємо зі списку
        manager.disconnect(websocket)