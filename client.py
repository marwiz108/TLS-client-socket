#!/usr/bin/env python
import argparse
import socket
import ssl
import sys

PORT = int(sys.argv[2]) if sys.argv[1] == "-p" else 27995
HOST = sys.argv[-2]
NUID = sys.argv[-1]

BUFFER_LEN = 16384

HELLO = "cs5700spring2022 HELLO"
EVAL = "cs5700spring2022 EVAL"
STATUS = "cs5700spring2022 STATUS"
ERROR = "cs5700spring2022 ERR #DIV/0"
BYE = "cs5700spring2022 BYE"

def isOperator(value):
    '''
    Function: isOperator - checks if given value is an operator
    Parameters: value - the given value to check
    Return: true if value is an operator, false otherwise
    '''
    return value == "+" or value == "-" or value == "*" or value == "//" or value == "<<^"

def calculate(val1, val2, op):
    '''
    Function: calculate - calculates given values using the given operator
    Parameters: val1 - lefthand operand value
                val2 - righthand operand value
                op - operator to apply to values
    Return: an integer result of the calculation (floors any float values)
            a boolean indicating whether a ZeroDivisionError occurred
    '''
    has_error = False
    result = 0
    try:
        if op == "+": result = val1 + val2
        if op == "-": result = val1 - val2
        if op == "*": result = val1 * val2
        if op == "//": result = val1 // val2
        if op == "<<^": result = (val1 << 13)^val2
    except ZeroDivisionError:
        has_error = True
    return result, has_error

def evaluate(expression):
    '''
    Function: evaluate - evaluates the expression given
    Parameters: expression - the expression that needs to be evaluated
    Return: an integer result from the evaluation
            a boolean indicating whether a ZeroDivisionError occurred
    '''
    has_error = False
    expr = expression.split(" ")
    values = []
    operators = []

    for element in expr:
        if isOperator(element) or element == "(":
            operators.append(element)

        if element.lstrip("-").isnumeric():
            values.append(int(element))

        if element == ")":
            while len(operators) > 0 and operators[-1] != "(":
                op = operators.pop()
                val2 = values.pop()
                val1 = values.pop()
                res, has_error = calculate(val1, val2, op)
                if has_error:
                    return res, has_error
                values.append(res)
            operators.pop()
    
    while len(operators) > 0 and operators[-1] != "(":
        op = operators.pop()
        val2 = values.pop()
        val1 = values.pop()
        res, has_error = calculate(val1, val2, op)
        if has_error:
            return res, has_error
        values.append(res)
    operators.pop()

    return values.pop(), has_error

def readFromServer(client):
    '''
    Function: readFromServer - receives the full message sent by the server
    Paramters: client - the secure TLS client that is connected to the server
    Return: a byte string of an EVAL message or BYE message from the server
    '''
    msg = ""
    while not msg.endswith("\n"):
        incoming_msg = client.recv(BUFFER_LEN).decode("utf-8")
        msg += incoming_msg

    return msg

def main():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        secure_client = ssl.wrap_socket(client_socket, ssl_version=ssl.PROTOCOL_TLSv1_2)
        secure_client.connect((HOST, PORT))
    except:
        client_socket.close()
        sys.exit("Connection failed.\n")

    hello_msg = HELLO + " " + NUID + "\n"
    secure_client.sendall(hello_msg.encode("utf-8"))

    server_msg = readFromServer(secure_client)

    while EVAL in server_msg:
        eval_res, has_error = evaluate(server_msg[server_msg.index("("):])
        if has_error:
            error_msg = ERROR + "\n"
            secure_client.sendall(error_msg.encode("utf-8"))
            has_error = False
        else:
            status_msg = STATUS + " " + str(eval_res) + "\n"
            secure_client.sendall(status_msg.encode("utf-8"))

        server_msg = readFromServer(secure_client)
    
    if BYE in server_msg:
        print(server_msg)
        
    secure_client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=int, default=27995)
    parser.add_argument("-s", action="store_true", required=True)
    parser.add_argument("HOST", type=str)
    parser.add_argument("NUID", type=str)
    args = parser.parse_args()
    main()
