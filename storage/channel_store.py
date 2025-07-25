channels: set[str] = set(["Chanel_1","Channel_2","Channel_3"])

def add_channel(name: str) -> None:
    name = name.strip().lstrip("@")
    if name:
        channels.add(name)

def remove_channel(name: str) -> bool:
    name = name.strip().lstrip("@")
    if name in channels:
        channels.remove(name)
        return True
    return False

def list_channels() -> list[str]:
    return sorted(channels)

def has_channels() -> bool:
    return bool(channels)
