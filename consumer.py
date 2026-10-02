"""Consumidor: escuta a fila de pedidos do ActiveMQ e processa cada mensagem."""
import json
import sys
import time

import stomp

from broker import connect, create_parser


class OrderListener(stomp.ConnectionListener):
    """Recebe as mensagens da fila. O stomp.py chama on_message numa thread própria."""

    def __init__(self, conn: stomp.Connection) -> None:
        self.conn = conn
        self.last_message_at = time.time()

    def on_message(self, frame) -> None:
        self.last_message_at = time.time()
        message_id = frame.headers["message-id"]
        subscription = frame.headers["subscription"]

        try:
            order = json.loads(frame.body)
            print(f"[CONSUMIDOR] Recebido pedido {order['id']}: {order['produto']} "
                  f"x{order['quantidade']} (enviado {order['enviado_em']})")
        except (ValueError, KeyError, TypeError) as error:
            # Mensagem inválida: o NACK faz o ActiveMQ movê-la para a fila ActiveMQ.DLQ,
            # em vez de reentregar a mesma mensagem para sempre
            print(f"[CONSUMIDOR] Mensagem inválida, enviada para a DLQ: {error}")
            self.conn.nack(message_id, subscription)
            return

        # Confirma o processamento; sem o ACK a mensagem volta para a fila
        self.conn.ack(message_id, subscription)

    def on_error(self, frame) -> None:
        print(f"[CONSUMIDOR] Erro: {frame.body}")


def main() -> None:
    parser = create_parser("Consumidor de pedidos do ActiveMQ")
    parser.add_argument("--timeout", type=float, default=0,
                        help="Encerra após N segundos sem mensagens (0 = roda até Ctrl+C)")
    args = parser.parse_args()

    conn = connect(args)
    listener = OrderListener(conn)
    conn.set_listener("", listener)
    conn.subscribe(destination=args.queue, id=1, ack="client-individual")
    print(f"[CONSUMIDOR] Escutando {args.queue} em {args.host}:{args.port} (Ctrl+C para sair)")

    try:
        while conn.is_connected():
            if args.timeout and time.time() - listener.last_message_at > args.timeout:
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

    if not conn.is_connected():
        sys.exit("[CONSUMIDOR] A conexão com o broker caiu.")
    conn.disconnect()
    print("[CONSUMIDOR] Desconectado.")


if __name__ == "__main__":
    main()
