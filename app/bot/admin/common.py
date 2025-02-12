state_dict = {
    "small_deskript": "краткое описание проекта",
    "large_deskript": "полное описание проекта",
    "telegram_bot_link": "ссылку на бота",
    "github_link": "ссылку на репозиторий",
}
async def add_project_final_msg(data:dict) -> str:
    return "\n".join(
    [
        f"<b>Имя проекта</b>: {data.get('name')}" if data.get('name') else "",
        f"<b>Краткое описание проекта</b>: {data.get('small_deskript')}" if data.get('small_deskript') else "",
        f"<b>Полное описание проекта</b>: {data.get('large_deskript')}" if data.get('large_deskript') else "",
        f"<b>Ссылка на бота</b>: {data.get('telegram_bot_link')}" if data.get('telegram_bot_link') else "",
        f"<b>Ссылка на репозиторий</b>: {data.get('github_link')}" if data.get('github_link') else ""
    ]
    ).strip()