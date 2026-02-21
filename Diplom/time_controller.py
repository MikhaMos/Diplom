# time_controller.py
"""
Глобальный контроллер времени для всего проекта.
Все модули импортируют отсюда время вместо datetime.now()
"""

import threading
import datetime as dt
import time
import mmap
import ctypes
import tempfile
import atexit
import signal
import os
import gc
from typing import Optional

class SharedTime(ctypes.Structure):
    _fields_ = [
        ('timestamp', ctypes.c_double), # Unix timestamp
        ('acceleration', ctypes.c_double),
        ('last_real_time', ctypes.c_double),
        ('running', ctypes.c_bool),
        ('lock', ctypes.c_byte*64)  # Простая блокировка
    ]


class GlobalTimeController:
    """Глобальный менеджер времени с ускорением"""

    _instance: Optional['GlobalTimeController'] = None
    _shared_memory: Optional[mmap.mmap] = None
    _mmap_file: Optional[tempfile.NamedTemporaryFile] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_shared_memory()
            cls._instance._start_time_thread()
            atexit.register(cls._instance.cleanup)
            # Перехватываем сигнал SIGINT (Ctrl+C)
            signal.signal(signal.SIGINT, cls._instance.signal_handler)
        return cls._instance
    
    def signal_handler(self, signum, frame):
        """Обработчик Ctrl+C"""
        print("\n Получен сигнал Ctrl+C, останавливаем время...")
        self.stop()
        # Выходим с правильным кодом
        import sys
        sys.exit(0)

    def _init_shared_memory(self):
        """Инициализация разделяемой памяти"""
        # Создаем временный файл для mmap
        self.temp_dir = tempfile.gettempdir()
        self.mmap_path = os.path.join(self.temp_dir, 'shared_time.mmap')

         # Размер структуры SharedTime
        self.struct_size = ctypes.sizeof(SharedTime)

        # Создаем или открываем файл
        if not os.path.exists(self.mmap_path):
            with open(self.mmap_path, 'wb') as f:
                f.write(b'\x00' * self.struct_size)
        
        # Открываем файл и создаем mmap
        self.file = open(self.mmap_path, "r+b")
        self.mmap = mmap.mmap(
            self.file.fileno(), 
            self.struct_size, 
            access=mmap.ACCESS_WRITE
        )

        # Создаем ctypes объект из памяти
        self.shared = SharedTime.from_buffer(self.mmap)

        # Если это первый запуск, инициализируем значения
        if self.shared.timestamp == 0:
            now = time.time()
            self.shared.timestamp = now
            self.shared.acceleration = 1.0
            self.shared.last_real_time = now
            self.shared.running = True
        
        self._lock = threading.Lock()
        self._thread = None
        self._stop_event = threading.Event()  # Добавляем событие для остановки
        self._cleaned_up = False # Флаг для предотвращения двойной очистки

    def _start_time_thread(self):
        """Запустить поток с временем (вызывается автоматически)"""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._time_loop, daemon=True)
        self._thread.start()
        print("GlobalTimeController started")

    def _time_loop(self):
        """Основной цикл времени (выполняется в отдельном потоке)"""
        try:
            while not self._stop_event.is_set():
                # Спим недолго, чтобы время обновлялось плавно
                time.sleep(0.1)
                if not self.shared.running:
                    continue
                # Получаем текущее время ДО блокировки
                current_real = time.time()

                with self._lock:
                    real_delta = current_real - self.shared.last_real_time
                    # Обновляем last_real ДО блокировки (важно!)
                    self.shared.last_real_time = current_real

                    virtual_delta = real_delta * self.shared.acceleration
                    self.shared.timestamp += virtual_delta
        except Exception as e:
            print(f"GlobalTimeController error: {e}")
        finally:
            print("Cleaning up thread resources...")

    def now(self) -> dt.datetime:
        """Текущее виртуальное время (замена datetime.now)"""
        return dt.datetime.fromtimestamp(self.shared.timestamp)

    def configure(self, start_time: dt.datetime, acceleration: float = 1.0):
        """Настроить виртуальное время"""
        with self._lock:
            self.shared.timestamp = start_time.timestamp()
            self.shared.acceleration = acceleration
            self.shared.last_real_time = time.time()


    def jump_to(self, new_time: dt.datetime):
        """Скачкообразно перейти к указанному времени"""
        with self._lock:
            self.shared.timestamp = new_time.timestamp()
            self.shared.last_real_time = time.time()
        

    def fast_forward(self, hours: float = 0, minutes: float = 0):
        """Быстрая перемотка вперёд"""
        seconds = hours * 3600 + minutes * 60
        with self._lock:
            self.shared.timestamp += seconds
            self.shared.last_real_time = time.time()
    
    def pause(self):
        with self._lock:
            self.shared.acceleration = 0
            self.shared.last_real_time = time.time()

    def resume(self):
        with self._lock:
            self.shared.acceleration = 1.0
            self.shared.last_real_time = time.time()

    def stop(self):
        """Остановить течение времени"""
        self.shared.running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            if self._thread.is_alive():
                print("GlobalTimeController failed to stop")
            else:
                print("GlobalTimeController stopped")
            
    
    def cleanup(self):
        """Очистить ресурсы после завершения программы"""
        if hasattr(self, '_cleaned_up') and self._cleaned_up:
            return
        print(f" Cleaning up resources (PID: {os.getpid()})")
        # 1. Сначала останавливаем поток
        self.stop()
        # 2. Удаляем ссылку на shared (ВАЖНО!)
        if hasattr(self, 'shared'):
            del self.shared

        # 3. Принудительный сбор мусора
        gc.collect()

        # 4. Закрываем mmap
        if hasattr(self, 'mmap'):
            try:
                self.mmap.close()
                print("mmap closed")
            except Exception as e:
                print(f"Failed to close mmap: {e}")
        
        # 5. Закрываем файл
        if hasattr(self, 'file') and self.file:
           try:
                self.file.close()
                print("file closed")
           except Exception as e:
                print(f"Failed to close file: {e}")

        # 6. Удаляем временный файл        
        if hasattr(self, 'mmap_path') and os.path.exists(self.mmap_path):
            try:
                os.remove(self.mmap_path)
                print("mmap file removed")
            except Exception as e:
                print(f"Failed to remove mmap file: {e}")
                
        self._cleaned_up = True
        print("cleanup done")

    @property
    def acceleration(self):
        return self.shared.acceleration
    
    @property
    def is_running(self):
        return self.shared.running

    @property
    def  thread_alive(self):
        return self._thread is not None and self._thread.is_alive()


# Глобальный экземпляр для импорта
time_controller = GlobalTimeController()


# Удобные функции для импорта
def now() -> dt.datetime:
    """Использовать вместо datetime.now() во всём проекте"""
    return time_controller.now()


def today() -> dt.date:
    """Использовать вместо datetime.today()"""
    return time_controller.now().date()