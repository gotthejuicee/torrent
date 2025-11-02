import os
import json
from pathlib import Path
import hashlib
import mutagen
from mutagen.easyid3 import EasyID3
from datetime import datetime


class MusicReleasePreparer:
    def __init__(self, album_path):
        self.album_path = Path(album_path)
        self.release_info = {}

    def analyze_audio_quality(self, file_path):
        """Анализ качества аудиофайла"""
        try:
            audio = mutagen.File(file_path)
            if audio:
                bitrate = audio.info.bitrate // 1000 if hasattr(audio.info, 'bitrate') else 'Unknown'
                length = round(audio.info.length) if hasattr(audio.info, 'length') else 'Unknown'
                sample_rate = audio.info.sample_rate if hasattr(audio.info, 'sample_rate') else 'Unknown'

                quality = 'Unknown'
                if bitrate != 'Unknown':
                    if bitrate >= 320:
                        quality = 'Высокое (320 kbps)'
                    elif bitrate >= 256:
                        quality = 'Хорошее (256 kbps)'
                    elif bitrate >= 192:
                        quality = 'Среднее (192 kbps)'
                    else:
                        quality = 'Низкое'

                return {
                    'bitrate': bitrate,
                    'length': length,
                    'sample_rate': sample_rate,
                    'quality': quality
                }
        except Exception as e:
            print(f"Ошибка анализа {file_path}: {e}")
        return {'bitrate': 'Unknown', 'length': 'Unknown', 'sample_rate': 'Unknown', 'quality': 'Unknown'}

    def get_checksums(self, file_path):
        """Вычисление контрольных сумм"""
        hashes = {}
        try:
            with open(file_path, 'rb') as f:
                md5_hash = hashlib.md5()
                sha1_hash = hashlib.sha1()

                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hash.update(chunk)
                    sha1_hash.update(chunk)

                hashes['md5'] = md5_hash.hexdigest()
                hashes['sha1'] = sha1_hash.hexdigest()
        except Exception as e:
            print(f"Ошибка вычисления хэшей {file_path}: {e}")

        return hashes

    def extract_metadata(self):
        """Извлечение метаданных из аудиофайлов"""
        metadata = []
        total_size = 0

        # Ищем все MP3 файлы в папке и подпапках
        for file_path in self.album_path.glob('**/*.mp3'):
            if file_path.is_file():
                print(f"🔍 Анализ: {file_path.name}")

                quality = self.analyze_audio_quality(file_path)
                checksums = self.get_checksums(file_path)

                try:
                    audio = EasyID3(file_path)
                    track_metadata = {
                        'title': audio.get('title', [file_path.stem])[0],
                        'artist': audio.get('artist', ['Unknown'])[0],
                        'album': audio.get('album', ['Unknown'])[0],
                        'date': audio.get('date', ['Unknown'])[0],
                        'tracknumber': audio.get('tracknumber', ['Unknown'])[0],
                        'genre': audio.get('genre', ['Unknown'])[0]
                    }
                except:
                    track_metadata = {
                        'title': file_path.stem,
                        'artist': 'Unknown',
                        'album': 'Unknown',
                        'date': 'Unknown',
                        'tracknumber': 'Unknown',
                        'genre': 'Unknown'
                    }

                file_info = {
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size': file_path.stat().st_size,
                    'size_mb': round(file_path.stat().st_size / 1024 / 1024, 2),
                    'quality': quality,
                    'checksums': checksums,
                    'metadata': track_metadata
                }

                metadata.append(file_info)
                total_size += file_path.stat().st_size

        return metadata, total_size

    def generate_description(self, metadata, total_size):
        """Генерация описания для трекера"""

        if not metadata:
            return "❌ Не найдено MP3 файлов для анализа"

        # Определяем общую информацию об альбоме
        artist = metadata[0]['metadata']['artist']
        album = metadata[0]['metadata']['album']
        year = metadata[0]['metadata']['date']
        genre = metadata[0]['metadata']['genre']
        quality = metadata[0]['quality']['quality']
        bitrate = metadata[0]['quality']['bitrate']

        description = f"""🎵 МУЗЫКАЛЬНЫЙ РЕЛИЗ 🎵

Исполнитель: {artist}
Альбом: {album}
Год: {year}
Стиль: {genre}
Качество: {quality}

📊 ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ:
Формат: MP3
Битрейт: {bitrate} kbps
Размер: {round(total_size / 1024 / 1024, 2)} MB
Треков: {len(metadata)}

📁 ТРЕКЛИСТ:
"""

        # Добавляем информацию о треках
        for i, track in enumerate(metadata, 1):
            duration = f"{track['quality']['length']} сек" if track['quality']['length'] != 'Unknown' else 'Unknown'
            description += f"{i:02d}. {track['metadata']['title']} - {track['size_mb']} MB\n"
            description += f"    Битрейт: {track['quality']['bitrate']} kbps | Длительность: {duration}\n"

        description += "\n🔍 КОНТРОЛЬНЫЕ СУММЫ:\n"

        # Добавляем контрольные суммы
        for track in metadata:
            description += f"\nФайл: {track['filename']}\n"
            description += f"MD5:  {track['checksums']['md5']}\n"
            description += f"SHA1: {track['checksums']['sha1']}\n"

        description += f"\n💾 ОБЩИЙ РАЗМЕР: {round(total_size / 1024 / 1024, 2)} MB"
        description += f"\n📅 ПОДГОТОВЛЕНО: {datetime.now().strftime('%d.%m.%Y %H:%M')}"

        return description

    def save_release_info(self, metadata, total_size, description):
        """Сохранение информации о релизе"""
        output_dir = Path("release_info")
        output_dir.mkdir(exist_ok=True)

        # Сохраняем описание
        with open(output_dir / "description.txt", "w", encoding="utf-8") as f:
            f.write(description)

        # Сохраняем JSON с метаданными
        release_data = {
            'album_name': metadata[0]['metadata']['album'] if metadata else 'Unknown',
            'artist': metadata[0]['metadata']['artist'] if metadata else 'Unknown',
            'year': metadata[0]['metadata']['date'] if metadata else 'Unknown',
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'track_count': len(metadata),
            'tracks': metadata,
            'preparation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(release_data, f, indent=2, ensure_ascii=False)

        # Сохраняем техническую информацию
        tech_info = f"""ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ

Папка альбома: {self.album_path}
Всего файлов: {len(metadata)}
Общий размер: {round(total_size / 1024 / 1024, 2)} MB
Дата анализа: {datetime.now().strftime('%d.%m.%Y %H:%M')}

ФАЙЛЫ:
"""
        for track in metadata:
            tech_info += f"\n{track['filename']}"
            tech_info += f"\n  Размер: {track['size_mb']} MB"
            tech_info += f"\n  Битрейт: {track['quality']['bitrate']} kbps"
            tech_info += f"\n  MD5: {track['checksums']['md5']}"
            tech_info += f"\n"

        with open(output_dir / "technical_info.txt", "w", encoding="utf-8") as f:
            f.write(tech_info)

        return output_dir

    def prepare_release(self):
        """Основной метод подготовки релиза"""
        print("🎵 Начинаю анализ музыкальных файлов...")

        metadata, total_size = self.extract_metadata()

        if not metadata:
            print("❌ Не найдено MP3 файлов в указанной папке!")
            return None

        print(f"✅ Найдено треков: {len(metadata)}")
        print(f"💾 Общий размер: {round(total_size / 1024 / 1024, 2)} MB")

        description = self.generate_description(metadata, total_size)
        output_dir = self.save_release_info(metadata, total_size, description)

        return description, output_dir


def main():
    """Основная функция"""
    print("=" * 60)
    print("🎵 ПОДГОТОВКА МУЗЫКАЛЬНОГО РЕЛИЗА ДЛЯ ТРЕКЕРА")
    print("=" * 60)

    # Автоматически ищем папку Sidr
    album_path = "Sidr"

    if not os.path.exists(album_path):
        print(f"❌ Папка '{album_path}' не найдена в текущей директории!")
        print("\n📁 Доступные папки и файлы:")
        for item in Path('.').iterdir():
            if item.is_dir():
                print(f"  📁 {item.name}")
            else:
                print(f"  📄 {item.name}")
        return

    print(f"📁 Найдена папка с музыкой: {album_path}")

    # Проверяем есть ли MP3 файлы
    mp3_files = list(Path(album_path).glob("**/*.mp3"))
    if not mp3_files:
        print(f"❌ В папке '{album_path}' не найдено MP3 файлов!")
        print("Доступные файлы:")
        for file in Path(album_path).iterdir():
            print(f"  - {file.name}")
        return

    print(f"🎵 Найдено MP3 файлов: {len(mp3_files)}")

    try:
        preparer = MusicReleasePreparer(album_path)
        description, output_dir = preparer.prepare_release()

        if description:
            print("\n✅ РЕЛИЗ УСПЕШНО ПОДГОТОВЛЕН!")
            print("=" * 60)
            print(description)
            print("=" * 60)
            print(f"\n📁 Результаты сохранены в папке: {output_dir}")
            print(f"📄 description.txt - описание для трекера")
            print(f"📄 metadata.json - полные метаданные")
            print(f"📄 technical_info.txt - техническая информация")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()