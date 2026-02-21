# time_master.py
"""
Отдельный скрипт для управления временем во всём проекте.
Запускается параллельно с основным приложением.
"""
import datetime as dt
import signal
from time_controller import time_controller


class TimeMaster:
    """Мастер-контроллер времени с Web UI или консольным интерфейсом"""

    def __init__(self):
        self.running = True
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Обработка Ctrl+C"""
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

    def _shutdown(self, signum, frame):
        print("\nЗавершение Time Master...")
        self.running = False

    def _print_status(self):
        print(f"Текущее время: {time_controller.now():%Y-%m-%d %H:%M:%S}")
        print(f"Ускорение: {time_controller.acceleration}x")
        print(f"Состояние {'запущено' if time_controller.is_running else 'приостановлено'}")

    def _reset_to_real_time(self):
        """Сброс к реальному времени"""
        real_now = dt.datetime.now()
        time_controller.configure(
            start_time=real_now,
            acceleration=1.0
        )

    def run(self):
        """Консольный интерфейс управления временем"""
        print("=" * 60)
        print("TIME MASTER - Глобальный контроллер времени")
        print("=" * 60)
        print(f"Текущее время: {time_controller.now():%Y-%m-%d %H:%M:%S}")
        print(f"Ускорение: {time_controller.acceleration}x")
        print("Команды:")
        print("status  - текущее состояние")
        print("  now     - текущее виртуальное время")
        print("  jump HH:MM - перейти к указанному времени")
        print("  ff N    - перемотать N часов вперёд")
        print("  speed X - установить ускорение X")
        print("  pause   - приостановить время")
        print("  resume  - возобновить время")
        print("  exit    - выход")
        print("=" * 60)

        self._print_status()

        while self.running:
            try:
                command = input("\nВведите команду: ").strip().lower()

                if not command:
                    continue

                if command == 'now':
                    print(f"Виртуальное время: {time_controller.now():%Y-%m-%d %H:%M:%S}")
                    print(f"Ускорение: {time_controller.acceleration}x")

                elif command == 'status':
                    self._print_status()

                elif command.startswith('jump '):
                    try:
                        time_str = command.split(' ', 1)[1]
                        hour, minute = map(int, time_str.split(':'))
                        current = time_controller.now()
                        new_time = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        time_controller.jump_to(new_time)
                        print(f"Переход к {new_time:%H:%M}")
                        self._print_status()
                    except (ValueError, IndexError):
                        print("Ошибка формата. Используйте: jump HH:MM")

                elif command.startswith('ff '):
                    try:
                        hours = float(command.split(' ', 1)[1])
                        time_controller.fast_forward(hours=hours)
                        print(f"Перемотка на {hours} часов")
                        self._print_status()
                    except (ValueError, IndexError):
                        print("Ошибка формата. Используйте: ff 1.5")

                elif command.startswith('speed '):
                    try:
                        speed = float(command.split(' ', 1)[1])
                        time_controller.configure(
                            time_controller.now(),
                            acceleration=speed
                        )
                        print(f"Ускорение установлено: {speed}x")
                        self._print_status()
                    except (ValueError, IndexError):
                        print("Ошибка формата. Используйте: speed 60")
                        
                elif command == 'reset':
                    self._reset_to_real_time()
                    self._print_status()


                elif command == 'pause':
                    time_controller.pause()
                    print("Время приостановлено")
                    self._print_status()

                elif command == 'resume':
                    time_controller.resume()
                    print("Время возобновлено")
                    self._print_status()
                
                elif command == 'exit':
                    self.running = False

                else:
                    print("Неизвестная команда")

            except (EOFError, KeyboardInterrupt):
                self.running = False
            except Exception as e:
                print(f"Ошибка: {e}")
        time_controller.stop()
        print("Завершение Time Master...")

    


def main():
    master = TimeMaster()
    try:
        master.run()
    except KeyboardInterrupt:
        print("\n Пока!")

if __name__ == '__main__':
    main()