STORY = {
    "start": {
        "text": ("На севере пещера, на юге река."),
        "choices": {"north": "cave", "south": "river"},
    },
    "cave": {
        "text": "Перед вами вход в пещеру. Можно зайти или уйти.",
        "choices": {"enter": "hall", "leave": "start"},
    },
    "hall": {
        "text": "В пещере спит дракон, а рядом сокровище.",
        "choices": {"sneak": "treasure", "attack": "dragon"},
    },
    "river": {
        "text": "У реки стоит старая лодка, а чуть выше по течению переброшен ветхий мост.",
        "choices": {"boat": "waterfall", "bridge": "village", "back": "start"},
    },
    "treasure": {
        "text": "Вы тихо забираете сундук и выходите из пещеры. Победа: вы богаты!",
        "choices": {},
    },
    "dragon": {
        "text": "Дракон просыпается и вспыхивает огнём. Конец: вы умерли.",
        "choices": {},
    },
    "waterfall": {
        "text": "Течение уносит лодку к водопаду. Конец: вы умерли.",
        "choices": {},
    },
    "village": {
        "text": "Мост выдерживает, и вы выходите к деревне. Победа: вы выжилив безопасности",
        "choices": {},
    },
}

START_NODE = "start"


def next_node(story, current, choice):
    if current not in story:
        raise ValueError(f"неизвестная сцена: {current}")
    choices = story[current]["choices"]
    if choice not in choices:
        raise ValueError(f"недопустимый выбор: {choice}")
    return choices[choice]


def is_ending(story, node_id):
    if node_id not in story:
        raise ValueError(f"неизвестная сцена: {node_id}")
    return not story[node_id]["choices"]


def list_endings(story):
    return [node_id for node_id in story if is_ending(story, node_id)]
