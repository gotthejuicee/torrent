import time
import os
import random


def clear_screen():
    """Очищает экран терминала"""
    os.system('cls' if os.name == 'nt' else 'clear')


def beating_heart():
    """Создает анимированное бьющееся сердце"""
    # Разные фазы сердца для анимации
    heart_frames = [
        """
         ♥♥♥  
        ♥♥♥♥♥ 
        ♥♥♥♥♥ 
         ♥♥♥  
          ♥   
        """,
        """
         ♥♥♥  
        ♥♥♥♥♥ 
        ♥♥♥♥♥ 
         ♥♥♥  
          ♥   
        """,
        """
         ♡♡♡  
        ♡♡♡♡♡ 
        ♡♡♡♡♡ 
         ♡♡♡  
          ♡   
        """
    ]

    colors = ['\033[91m', '\033[95m', '\033[93m']  # Красный, розовый, желтый

    try:
        while True:
            for frame in heart_frames:
                clear_screen()
                color = random.choice(colors)
                print(color + frame + '\033[0m')  # \033[0m сбрасывает цвет
                time.sleep(0.5)
    except KeyboardInterrupt:
        clear_screen()
        print("💝 Счастливого кодинга!")


if __name__ == "__main__":
    beating_heart()