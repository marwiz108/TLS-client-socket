TLS Client Socket

This program creates a client program that connects to a server using a TLS socket connection. The program is run from the command line and passes arguments for hostname and NUID, and an optional argument port.
The client program evaluates the EVAL expression and returns the result back to the server. This continues until a BYE message is received with a secret_flag.