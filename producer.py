"""Produtor: envia pedidos para uma fila do ActiveMQ."""
import json
import sys
import time
from datetime import datetime

from stomp.exception import NotConnectedException

from broker import connect, create_parser


def build_order(order_id: int) -> dict:
    """Monta um pedido de exemplo."""
    return {
        "id": order_id,
        "produto": f"Produto-{order_id}",
        "quantidade": order_id * 2,
        "enviado_em": datetime.now().isoformat(timespec="seconds"),
    }


def main() -> None:
    parser = create_parser("Produtor de pedidos para o ActiveMQ")
    parser.add_argument("--count", type=int, default=10, help="Quantidade de pedidos")
    parser.add_argument("--interval", type=float, default=0.5, help="Segundos entre pedidos")
    args = parser.parse_args()

    conn = connect(args)
    print(f"[PRODUTOR] Conectado em {args.host}:{args.port}, enviando para {args.queue}")

    try:
        for order_id in range(1, args.count + 1):
            order = build_order(order_id)
            conn.send(
                destination=args.queue,
                body=json.dumps(order),
                # persistent: o broker grava a mensagem em disco, então ela sobrevive a um restart
                headers={"persistent": "true", "content-type": "application/json"},
            )
            print(f"[PRODUTOR] Enviado pedido {order_id}: {order}")
            time.sleep(args.interval)
    except NotConnectedException:
        sys.exit("[PRODUTOR] A conexão com o broker caiu.")

    conn.disconnect()
    print("[PRODUTOR] Fim.")


if __name__ == "__main__":
    main()
