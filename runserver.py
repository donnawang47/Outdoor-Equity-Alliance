import sys
import argparse
import oea

#google expects app to run on port 5000
PORT = 5000

#NOte: probably uneccessary to have arg parser

def main():
    parser = argparse.ArgumentParser(description= \
        'The registrar application', allow_abbrev=False)
    parser.add_argument('port', type = int,
        help='the port at which the server should listen')
    args = parser.parse_args()

    port = args.port

    # if len(sys.argv) != 1:
    #     print('Usage: ' + sys.argv[0], file=sys.stderr)
    #     sys.exit(1)

    try:
        oea.app.run(host='0.0.0.0', port=port, debug=True)#,
                    #ssl_context = ('cert.pem','key.pem'))
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()