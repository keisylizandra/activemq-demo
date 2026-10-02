# ActiveMQ: produtor e consumidor em Python

Um produtor envia pedidos de compra para uma fila do ActiveMQ, e um consumidor lê e processa esses pedidos.

- **Broker:** Apache ActiveMQ Classic 6.2 (Docker)
- **Cliente:** Python 3 + `stomp.py` (protocolo STOMP, porta 61613)
- **Fila:** `/queue/pedidos`

## Arquivos

| Arquivo | O que faz |
|---|---|
| `broker.py` | Código comum aos dois scripts: opções de linha de comando e conexão com o ActiveMQ |
| `producer.py` | Monta pedidos de exemplo e envia para a fila |
| `consumer.py` | Escuta a fila, processa cada pedido e confirma o recebimento |
| `docker-compose.yml` | Sobe o ActiveMQ |
| `requirements.txt` | Dependência Python (`stomp.py`) |

Detalhes de funcionamento:

- **Mensagens persistentes:** o broker grava cada pedido em disco, então ele não se perde se o ActiveMQ reiniciar.
- **ACK individual:** o consumidor só confirma a mensagem depois de processá-la. Se cair no meio, o broker entrega de novo.
- **Mensagem inválida:** se o corpo não for um pedido válido, o consumidor rejeita a mensagem (NACK) e o ActiveMQ a move para a fila `ActiveMQ.DLQ`.
- **Queda do broker:** se o ActiveMQ estiver fora do ar ou cair, os scripts avisam e encerram.

## Como executar

### 1. Subir o ActiveMQ

```powershell
docker compose up -d
```

Console web: http://localhost:8161/admin (usuário `admin`, senha `admin`). Em **Queues** aparecem a fila `pedidos` e os contadores de mensagens enfileiradas e consumidas.

### 2. Instalar a dependência

```powershell
python -m pip install -r requirements.txt
```

### 3. Produzir e consumir

Terminal 1, o consumidor fica escutando:

```powershell
python consumer.py
```

Terminal 2, o produtor envia os pedidos:

```powershell
python producer.py --count 10
```

Opções comuns: `--host`, `--port`, `--queue`, `--user`, `--password`.
O produtor aceita `--count` e `--interval`; o consumidor aceita `--timeout N` para encerrar depois de N segundos sem mensagens.
`python producer.py --help` mostra todas.

### 4. Parar

```powershell
docker compose down
```

## Roteiro de demonstração

1. Com o consumidor **desligado**, rode `python producer.py --count 5`. No console web, a fila `pedidos` mostra 5 mensagens pendentes: o broker guarda as mensagens enquanto ninguém consome.
2. Rode `python consumer.py`. Ele recebe os 5 pedidos de uma vez e a fila zera.
3. Com o consumidor rodando, envie mais pedidos e veja cada um chegar na hora.

## Alternativa: ActiveMQ numa EC2 (Amazon Linux 2023)

1. Crie a instância. No Security Group, libere a entrada TCP **61613** e **8161** apenas para o seu IP.
2. Na instância:
   ```bash
   sudo dnf install -y docker && sudo systemctl enable --now docker
   sudo docker run -d --name activemq -p 61613:61613 -p 61616:61616 -p 8161:8161 apache/activemq-classic:latest
   ```
3. Na sua máquina:
   ```powershell
   python consumer.py --host <IP_PUBLICO_EC2>
   python producer.py --host <IP_PUBLICO_EC2>
   ```
   O console fica em `http://<IP_PUBLICO_EC2>:8161/admin`.

**Atenção:** o `admin/admin` protege só o console web. Na configuração padrão, as portas de mensagens (61613 e 61616) aceitam conexão com qualquer senha. Por isso as portas devem ficar liberadas apenas para o seu IP.
