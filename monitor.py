# -*- coding: utf-8 -*-
import psutil
import time
import logging
import threading
import os
import sys


def setup_logger(logger_name, log_file):
    """Configura o logger que grava em CSV"""
    log_setup = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(message)s')  # saída pura em CSV
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), log_file)
    fileHandler = logging.FileHandler(filename, mode='a')
    fileHandler.setFormatter(formatter)
    log_setup.setLevel(logging.INFO)
    log_setup.addHandler(fileHandler)


def aguardar_tempo(stop_event, timeOut):
    """Para automaticamente após o tempo definido"""
    time.sleep(timeOut)
    stop_event.set()


def aguardar_enter(stop_event):
    """Para manualmente ao pressionar ENTER"""
    input("\nPressione ENTER para parar...\n")
    stop_event.set()


def monitorar(stop_event):
    """Coleta as métricas e grava no CSV"""
    num = 0

    # Inicializa as medições de rede e disco
    net_init = psutil.net_io_counters()
    disk_init = psutil.disk_io_counters()

    logMonitor = logging.getLogger('logCPU_MEM')
    logMonitor.info("indice,memoria(%),cpu(%),Disco-uso(%),Disk-Read(bytes),Disk-Write(bytes),Net-in(bytes),Net-out(bytes),TimeStamp")

    while not stop_event.is_set():
        # Coleta a utilização da CPU e memória
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent

        # Coleta uso do disco total e I/O
        uso_disco_pct = psutil.disk_usage('/').percent
        disk_io = psutil.disk_io_counters()
        disk_read = disk_io.read_bytes - disk_init.read_bytes
        disk_write = disk_io.write_bytes - disk_init.write_bytes

        # Coleta a rede (bytes recebidos e enviados)
        net_io = psutil.net_io_counters()
        net_in = net_io.bytes_recv - net_init.bytes_recv
        net_out = net_io.bytes_sent - net_init.bytes_sent

        # Atualiza as variáveis de medição para a próxima iteração
        net_init = net_io
        disk_init = disk_io

        # Marca o timestamp
        timestamp = int(time.time())
        num += 1

        # Formatação da linha de dados
        linha = "{},{},{},{},{},{},{},{},{}".format(
            num, mem, cpu, uso_disco_pct, disk_read, disk_write, net_in, net_out, timestamp
        )

        # Grava a linha no log e imprime
        logMonitor.info(linha)
        print(num, '-', linha)


if __name__ == "__main__":
    # === Tratamento dos argumentos ===
    args = sys.argv[1:]

    if not args:
        print("Uso:")
        print("  python3 monitor.py <tempo_em_segundos> <nome_arquivo.csv>")
        print("  python3 monitor.py <nome_arquivo.csv>   (modo contínuo)")
        sys.exit(1)

    # Detecta se o primeiro argumento é o tempo
    if args[0].isdigit():
        timeOut = int(args[0])
        logFile = args[1] if len(args) > 1 else "TxMonitor.csv"
        modo = "temporizado"
    else:
        timeOut = None
        logFile = args[0]
        modo = "contínuo"

    # === Configuração do logger ===
    setup_logger('logCPU_MEM', logFile)

    print(f"Monitorando ({modo})...")
    print("indice,memoria(%),cpu(%),Disco-uso(%),Disk-Read(bytes),Disk-Write(bytes),Net-in(bytes),Net-out(bytes),TimeStamp")

    stop_event = threading.Event()

    # Define modo de parada
    if timeOut:
        t1 = threading.Thread(target=aguardar_tempo, args=(stop_event, timeOut))
    else:
        t1 = threading.Thread(target=aguardar_enter, args=(stop_event,))

    t2 = threading.Thread(target=monitorar, args=(stop_event,))

    t1.start()
    t2.start()
    t2.join()

    print(f"\nMonitoramento finalizado. Arquivo salvo em {logFile}.")
