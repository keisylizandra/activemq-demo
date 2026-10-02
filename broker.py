"""Opções de linha de comando e conexão com o ActiveMQ, usadas pelo produtor e pelo consumidor."""
import argparse
import sys

import stomp
from stomp.exception import ConnectFailedException


def create_parser(description: str) -> argparse.ArgumentParser:
    """Cria o parser já com as opções de conexão, comuns aos dois scripts."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--host", default="localhost", help="Host do ActiveMQ (ex.: IP público da EC2)")
    parser.add_argument("--port", type=int, default=61613, help="Porta STOMP do ActiveMQ")
    parser.add_argument("--queue", default="/queue/pedidos")
    parser.add_argument("--user", default="admin")
    parser.add_argument("--password", default="admin")
    return parser


def connect(args: argparse.Namespace) -> stomp.Connection:
    """Conecta no ActiveMQ. Se o broker não responder, encerra o programa com uma mensagem clara."""
    conn = stomp.Connection([(args.host, args.port)])
    try:
        conn.connect(args.user, args.password, wait=True)
    except ConnectFailedException:
        sys.exit(f"Erro: não foi possível conectar no ActiveMQ em {args.host}:{args.port}")
    return conn
