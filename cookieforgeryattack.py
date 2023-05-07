import sys
import socket

def main():
    if len(sys.argv) != 3:
        print('Usage: python %s host port' % sys.argv[0])
        sys.exit(1)

    try:
        host = sys.argv[1]
        port =  int(sys.argv[2])

        with socket.socket() as sock:
            sock.connect((host, port))

            out_flo = sock.makefile(mode='w', encoding='iso-8859-1')
            out_flo.write('GET ', + '/show' + ' HTTP/1.1\r\n')
            out_flo.write('Host: ' + host + '\r\n')
            out_flo.write('Cookie: username=attacker\r\n')
            out_flo.write('\r\n')
            out_flo.flush()

            in_flo = sock.makefile(mode='r', encoding='iso-8859-1')
            for line in in_flo:
                print(line, end='')

    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    if __name__ == '__main__':
        main()

