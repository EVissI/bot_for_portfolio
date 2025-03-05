
state_dict = {
    "description_small": "краткое описание проекта",
    "description_large": "полное описание проекта",
    "telegram_bot_url": "ссылку на бота",
}
async def add_project_final_msg(data:dict) -> str:
    return "\n".join(
    [
        f"<b>Имя проекта</b>: {data.get('name')}" if data.get('name') else "",
        f"<b>Краткое описание проекта</b>: {data.get('description_small')}" if data.get('description_small') else "",
        f"<b>Полное описание проекта</b>: {data.get('description_large')}" if data.get('description_large') else "",
        f"<b>Ссылка на бота</b>: {data.get('telegram_bot_url')}" if data.get('telegram_bot_url') else "",
    ]
    ).strip()


telegram_bot_url_pattern = r"^(@[A-Za-z0-9_]{5,32}bot)$"
https_link_pattern = r"^https://.*"


