import config


# Функция создания своего текста для поста
def create_caption(text: str):
    try:
        # Разделение строки на список строк
        lines = text.splitlines()

        if len(lines) > 1:
            # Удаление последней строчки с ссылкой на канал
            lines.pop()

            # Добавление собственной ссылки на канал
            lines.append(f'<b><a href="{config.CHANNEL_URL}">{config.INVITE_TEXT}</a></b>')

        # Объединение оставшихся строк в пост
        new_text = "\n".join(lines)
        return new_text
    
    except Exception as error:
        print(f'ERROR create_caption(): {error}')