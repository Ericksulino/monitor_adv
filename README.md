# Monitor de Recursos (CPU/Memória/Disco/IO/Rede)

Script em Python para monitorar recursos locais e salvar métricas em **CSV**.  
Suporta dois modos: **temporizado** (para após N segundos) e **contínuo** (para manualmente com `ENTER`).

## ✨ Recursos

- CPU (%)  
- Memória RAM (%)  
- **Disco usado (%)**  
- **Disk I/O**: bytes lidos e escritos desde o início  
- **Rede**: bytes recebidos e enviados desde o início  
- Timestamp (UNIX)

Grava em arquivo **CSV puro**, fácil de abrir no Excel/LibreOffice.

---

## 📦 Requisitos

- **Python 3.6+** (recomendado `python3`)  
- Biblioteca: `psutil`

Instalação:
```bash
pip install psutil
```

> Se o arquivo tiver acentos, mantenha a primeira linha:  
> `# -*- coding: utf-8 -*-`

---

## 🚀 Uso

### 1) Modo temporizado (para automaticamente após N segundos)
```
python3 monitor.py <tempo_em_segundos> <nome_arquivo.csv>
```
**Exemplo:**
```bash
python3 monitor.py 30 log30.csv
```

### 2) Modo contínuo (para ao pressionar ENTER)
```
python3 monitor.py <nome_arquivo.csv>
```
**Exemplo:**
```bash
python3 monitor.py log_continuo.csv
```
Durante a execução contínua, pressione **ENTER** para encerrar com segurança.

---

## 🧾 Saída (CSV)

Cabeçalho:
```
indice,memoria(%),cpu(%),Disco-uso(%),Disk-Read(bytes),Disk-Write(bytes),Net-in(bytes),Net-out(bytes),TimeStamp
```

Exemplo (ilustrativo):
```
1,9.1,1.0,35.9,0,0,9920,8348,1762604545
2,9.1,1.3,35.9,0,0,18845,17040,1762604546
...
```

### Notas sobre as métricas
- `Disk-Read(bytes)` / `Disk-Write(bytes)`: **cumulativas desde o início do script**.  
- `Net-in(bytes)` / `Net-out(bytes)`: **cumulativas desde o início do script**.  
- `Disco-uso(%)`: percentual de ocupação do ponto de montagem `/` no momento da leitura.  
- `indice`: contador de linhas (1 por segundo, pois `cpu_percent(interval=1)`).

---

## 🧠 Como funciona (resumo técnico)

- Thread de **parada**:
  - Temporizado: dorme por `N` segundos e sinaliza stop.
  - Contínuo: aguarda `ENTER` e sinaliza stop.
- Thread de **coleta**:
  - A cada ~1s coleta métricas via `psutil` e escreve CSV.
- Uso de `threading.Event` para **finalização segura**.

---

## 🔍 Exemplos práticos

Rodar 5 minutos e salvar em `prod.csv`:
```bash
python3 monitor.py 300 prod.csv
```

Rodar continuamente (observando um teste de carga) e parar manualmente:
```bash
python3 monitor.py carga.csv
# ... execute seu teste ...
# pressione ENTER para encerrar
```

Abrir no Linux com `column` só pra visualizar tabulado no terminal:
```bash
column -s, -t < prod.csv | less -S
```

---

## 📈 (Opcional) Explorando o CSV depois

Exemplo rápido em Python para ver CPU e Memória:
```python
import pandas as pd
df = pd.read_csv("log30.csv")
print(df[['cpu(%)','memoria(%)']].describe())
```

---

## 🆘 Solução de problemas

**Erro de acentuação (Non-ASCII / PEP 0263)**  
Adicione na primeira linha do arquivo:
```python
# -*- coding: utf-8 -*-
```

**`SyntaxError` em f-strings**  
Você está usando Python 2. Rode com Python 3:
```bash
python3 monitor.py 10 log.csv
```

**Permissões / Disco**  
Se monitorar caminhos diferentes de `/`, ajuste no código `psutil.disk_usage('<ponto>')`.  
Para contêineres, pode ser necessário montar o filesystem do host.

---

## 🛠 Estrutura do código (arquivos)

- `monitor.py` — script principal  
- `README.md` — este arquivo

---

## 📄 Licença

Use livremente. Se redistribuir, mantenha os créditos e este README.

---

## 🤝 Contribuições

Sugestões/melhorias são bem-vindas: métricas por processo, múltiplos discos, exportação JSON/Prometheus, etc.
