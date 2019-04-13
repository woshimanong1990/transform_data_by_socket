# coding: utf-8
import select
import socket

from queue import Queue, Empty

from transform_data_by_socket.utils import setup_logging_and_return_logger

logger = setup_logging_and_return_logger("record.log")


def create_server(port):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', port))
        server.listen()
        server.setblocking(0)
        return server
    except:
        logger.error("create server error", exc_info=True)


def create_remote_connect(remote_host, remote_port):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((remote_host, remote_port))
        server.setblocking(0)
        return server
    except:
        logger.error("create remote connect error", exc_info=True)


def clear_connect(inputs, outputs, couple_connects, discard_socket, message_queues):
    try:
        pair_socket = couple_connects[discard_socket]
        if discard_socket in outputs:
            outputs.remove(discard_socket)
        if pair_socket in outputs:
            outputs.remove(pair_socket)
        if discard_socket in inputs:
            inputs.remove(discard_socket)
        if pair_socket in inputs:
            inputs.remove(pair_socket)
        discard_socket.close()
        pair_socket.close()

        couple_connects.pop(pair_socket, None)
        couple_connects.pop(discard_socket, None)
        if discard_socket in message_queues:
            del message_queues[discard_socket]
        if pair_socket in message_queues:
            del message_queues[pair_socket]
    except:
        logger.error("clear connect error", exc_info=True)


def start(local_listen_port, remote_host, remote_port):
    local_server = create_server(local_listen_port)

    if not local_server:
        return
    inputs = [local_server]
    outputs = []
    message_queues = {}
    couple_connects = {}

    while inputs:
        readable, writable, exceptional = select.select(
            inputs, outputs, inputs)
        for s in readable:
            if s is local_server:
                connection, client_address = s.accept()
                connection.setblocking(0)
                remote_connect = create_remote_connect(remote_host, remote_port)
                if remote_connect is None:
                    logger.error("create remote connect error for %s", client_address)
                    connection.close()
                    continue
                message_queues[connection] = Queue()
                message_queues[remote_connect] = Queue()

                couple_connects[connection] = remote_connect
                couple_connects[remote_connect] = connection

                inputs.append(connection)
                inputs.append(remote_connect)
                outputs.append(remote_connect)
                continue

            try:
                data = s.recv(1024)
            except BlockingIOError as e:
                continue
            except ConnectionResetError as e:
                clear_connect(inputs, outputs, couple_connects, s, message_queues)
                continue
            except:
                logger.error("unknown error , type s:%s :id:%s len:%s", type(s), id(s), len(inputs), exc_info=True)
                continue
            # logger.info("get data:%s", data)
            if data:
                message_queues[couple_connects[s]].put(data)
                if s not in outputs:
                    outputs.append(s)
            else:
                clear_connect(inputs, outputs, couple_connects, s, message_queues)

        for s in writable:
            if s not in message_queues:
                continue
            try:
                next_msg = message_queues[s].get_nowait()
            except Empty:
                continue
            else:
                s.send(next_msg)

        for s in exceptional:
            logger.error("get error:%s", s)
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()
            del message_queues[s]


def main():
    local_listen_port = 1234
    remote_host = '192.168.1.209'
    remote_port = 12345
    try:
        start(local_listen_port, remote_host, remote_port)
    except:
        logger.error("start main error", exc_info=True)


if __name__ == "__main__":
    main()