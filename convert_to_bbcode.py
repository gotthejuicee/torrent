import json
from pathlib import Path
from datetime import datetime


def convert_to_bbcode():
    """Конвертирует сгенерированное описание в BB-код для NNM-Club"""

    # Читаем метаданные из JSON
    try:
        with open('release_info/metadata.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Файл metadata.json не найден! Сначала запустите prepare_release.py")
        return

    # Извлекаем данные
    artist = data.get('artist', 'Unknown Artist')
    album = data.get('album_name', 'Unknown Album')
    year = data.get('year', 'Unknown Year')
    total_size = data.get('total_size_mb', 0)
    track_count = data.get('track_count', 0)
    tracks = data.get('tracks', [])

    # Определяем жанр (берем из первого трека)
    genre = tracks[0].get('metadata', {}).get('genre', 'Unknown Genre') if tracks else 'Unknown Genre'

    # Определяем качество (берем из первого трека)
    quality_info = tracks[0].get('quality', {}) if tracks else {}
    bitrate = quality_info.get('bitrate', 'Unknown')
    quality_label = quality_info.get('quality', 'Unknown Quality')

    # Генерируем BB-код
    bbcode = f"""[center][size=4][b]🎵 МУЗЫКАЛЬНЫЙ РЕЛИЗ 🎵[/b][/size][/center]

[MUSIC]{artist} - {album} ({year})[/MUSIC]

[INFO]
Исполнитель: {artist}
Альбом: {album}
Год выхода: {year}
Жанр: {genre}
Качество: MP3, {bitrate} kbps
Размер: {total_size} MB
Треков: {track_count}
[/INFO]

[b]ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ:[/b]
• Формат: MP3
• Битрейт: {bitrate} kbps
• Качество: {quality_label}
• Общий размер: {total_size} MB
• Количество треков: {track_count}

[b]ТРЕКЛИСТ:[/b]
[list]
"""

    # Добавляем треки в список
    for i, track in enumerate(tracks, 1):
        track_meta = track.get('metadata', {})
        track_quality = track.get('quality', {})
        duration = track_quality.get('length', 'Unknown')

        bbcode += f"[*] [b]{i:02d}.[/b] {track_meta.get('title', 'Unknown Title')} - {track.get('size_mb', 0)} MB\n"
        bbcode += f"    Битрейт: {track_quality.get('bitrate', 'Unknown')} kbps | "
        bbcode += f"Длительность: {duration} сек\n"

    bbcode += "[/list]\n\n"

    # Добавляем контрольные суммы
    bbcode += "[b]КОНТРОЛЬНЫЕ СУММЫ:[/b]\n"
    bbcode += "[code]\n"

    for track in tracks:
        checksums = track.get('checksums', {})
        bbcode += f"Файл: {track.get('filename', 'Unknown')}\n"
        bbcode += f"MD5:  {checksums.get('md5', 'Unknown')}\n"
        bbcode += f"SHA1: {checksums.get('sha1', 'Unknown')}\n\n"

    bbcode += "[/code]\n\n"

    # Добавляем информацию об источнике
    bbcode += f"""[b]ИСТОЧНИК:[/b] Digital / CD (укажите ваш источник)
[b]РИП:[/b] Exact Audio Copy / iTunes (укажите чем риповали)
[b]ДАТА ПОДГОТОВКИ:[/b] {datetime.now().strftime('%d.%m.%Y %H:%M')}

[center][color=green][b]✅ Проверено: оригинальный рип, контрольные суммы, полная информация[/b][/color][/center]

[center][size=3][b]Раздавайте столько, сколько скачали![/b][/size][/center]"""

    # Сохраняем BB-код в файл
    output_file = Path("release_info/description_bbcode.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(bbcode)

    print("✅ BB-код успешно сгенерирован!")
    print(f"📄 Файл: {output_file}")

    # Показываем превью
    print("\n" + "=" * 60)
    print("ПРЕВЬЮ BB-КОДА ДЛЯ NNM-CLUB:")
    print("=" * 60)
    print(bbcode[:2000] + "..." if len(bbcode) > 2000 else bbcode)


def create_simple_bbcode():
    """Простая конвертация существующего description.txt в BB-код"""

    try:
        with open('release_info/description.txt', 'r', encoding='utf-8') as f:
            description = f.read()
    except FileNotFoundError:
        print("❌ Файл description.txt не найден!")
        return

    # Простая конвертация в BB-код
    bbcode = description

    # Заменяем форматирование
    bbcode = bbcode.replace("🎵 МУЗЫКАЛЬНЫЙ РЕЛИЗ 🎵", "[center][size=4][b]🎵 МУЗЫКАЛЬНЫЙ РЕЛИЗ 🎵[/b][/size][/center]")
    bbcode = bbcode.replace("📊 ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ:", "[b]ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ:[/b]")
    bbcode = bbcode.replace("📁 ТРЕКЛИСТ:", "[b]ТРЕКЛИСТ:[/b]")
    bbcode = bbcode.replace("🔍 КОНТРОЛЬНЫЕ СУММЫ:", "[b]КОНТРОЛЬНЫЕ СУММЫ:[/b]")

    # Добавляем теги для NNM-Club в начало
    lines = bbcode.split('\n')
    if lines[0].startswith('[center]'):
        # Вставляем тег [MUSIC] после первого блока
        for i, line in enumerate(lines):
            if line.strip() == '':
                artist_album = lines[2].replace('Исполнитель: ', '').strip() + " - " + lines[3].replace('Альбом: ',
                                                                                                        '').strip()
                year = lines[4].replace('Год: ', '').strip()
                lines.insert(i, f"[MUSIC]{artist_album} ({year})[/MUSIC]")
                lines.insert(i + 1, "")
                lines.insert(i + 2, "[INFO]")

                # Находим конец технической информации для закрытия [INFO]
                for j in range(i + 3, len(lines)):
                    if lines[j].startswith('📊') or lines[j].startswith('[b]ТЕХНИЧЕСКАЯ'):
                        lines.insert(j, "[/INFO]")
                        lines.insert(j + 1, "")
                        break
                break

    bbcode = '\n'.join(lines)

    # Сохраняем простую версию
    output_file = Path("release_info/description_simple_bbcode.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(bbcode)

    print(f"📄 Простой BB-код сохранен в: {output_file}")

    return bbcode


if __name__ == "__main__":
    print("🔄 Конвертация в BB-код для NNM-Club...")
    print("=" * 50)

    # Пробуем создать детализированный BB-код
    convert_to_bbcode()

    print("\n" + "=" * 50)
    print("Создаю упрощенную версию...")

    # И простую версию
    simple_bbcode = create_simple_bbcode()

    print("\n🎯 ИНСТРУКЦИЯ ДЛЯ NNM-CLUB:")
    print("1. Скопируйте содержимое из release_info/description_bbcode.txt")
    print("2. Вставьте в поле описания на NNM-Club")
    print("3. Прикрепите .torrent файл")
    print("4. Установите заголовок: [MP3] Artist - Album (Year) [NNM-Club]")
    print("5. Опубликуйте релиз!")