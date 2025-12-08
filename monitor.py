# -*- coding: utf-8 -*-
import psutil
import time
import logging
import threading
import os
import sys

# Definir o intervalo de amostragem em segundos
SAMPLE_INTERVAL = 1 


def setup_logger(logger_name, log_file):
    """Configura o logger que grava em CSV"""
    log_setup = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(message)s')  # saída pura em CSV
    
    # Garantir que o diretório exista se necessário, e usar caminho absoluto
    filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), log_file)
    
    # 'w' mode é mais seguro para iniciar um novo arquivo a menos que precise de append
    # No seu código original você usava 'a', vou manter o 'a' (append) como você pretendia.
    fileHandler = logging.FileHandler(filename, mode='a', encoding='utf-8')
    fileHandler.setFormatter(formatter)
    log_setup.setLevel(logging.INFO)
    
    # Adicionar o handler apenas se ainda não tiver sido adicionado (evita duplicatas)
    if not log_setup.handlers:
        log_setup.addHandler(fileHandler)


def aguardar_tempo(stop_event, timeOut):
    """Para automaticamente após o tempo definido"""
    print(f"\nColetando por {timeOut} segundos...")
    time.sleep(timeOut)
    stop_event.set()


def aguardar_enter(stop_event):
    """Para manualmente ao pressionar ENTER"""
    # A função input() bloqueia, o que é o comportamento desejado
    input("\nPressione ENTER para parar...\n")
    stop_event.set()


def monitorar(stop_event):
    """Coleta as métricas e grava no CSV"""
    num = 0

    # Inicializa as medições de rede e disco para calcular as DIIFERENÇAS
    # no intervalo de SAMPLE_INTERVAL
    net_init = psutil.net_io_counters()
    disk_init = psutil.disk_io_counters()

    logMonitor = logging.getLogger('logCPU_MEM')
    logMonitor.info("indice,memoria(%),cpu(%),Disco-uso(%),Disk-Read(bytes),Disk-Write(bytes),Net-in(bytes),Net-out(bytes),TimeStamp")

    # Primeira leitura da CPU com interval=0 (não bloqueia)
    psutil.cpu_percent(interval=None) 
    
    while not stop_event.is_set():
        # Coleta a utilização da CPU (não bloqueia, usa a amostra do último segundo)
        # O intervalo de 1 segundo será controlado pelo time.sleep()
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent

        # Coleta o uso total do disco (percentual)
        # psutil.disk_usage('/') pega o uso do ponto de montagem raiz
        uso_disco_pct = psutil.disk_usage('/').percent 
        
        # Coleta I/O e Rede ANTES do sleep
        disk_io = psutil.disk_io_counters()
        net_io = psutil.net_io_counters()
        
        # Calcula as diferenças de I/O no intervalo
        disk_read = disk_io.read_bytes - disk_init.read_bytes
        disk_write = disk_io.write_bytes - disk_init.write_bytes
        net_in = net_io.bytes_recv - net_init.bytes_recv
        net_out = net_io.bytes_sent - net_init.bytes_sent

        # Atualiza as variáveis de medição para a próxima iteração
        # Isso garante que a diferença calculada seja a do último intervalo
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
        print(linha)
        
        # Aguarda o intervalo de amostragem antes da próxima leitura
        # Verifica se o evento de parada foi acionado antes de dormir
        if not stop_event.is_set():
            time.sleep(SAMPLE_INTERVAL)


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

    print(f"Monitorando ({modo})... Intervalo: {SAMPLE_INTERVAL}s")
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
    
    # O join espera a thread de monitoramento (t2) terminar antes de prosseguir
    t2.join() 
    
    # Garante que a thread de controle (t1) seja interrompida
    if t1.is_alive():
        stop_event.set()
        t1.join(timeout=1) # Join com timeout para não bloquear indefinidamente se input() estiver esperando
    

    print(f"\nMonitoramento finalizado. Arquivo salvo em {logFile}.")