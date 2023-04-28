import sys
import oea

def main():

    if len(sys.argv) != 1:
        print('Usage: ' + sys.argv[0], file=sys.stderr)
        sys.exit(1)

    #google auth expects app to run on port 5000
    try:
        oea.app.run(host='0.0.0.0', port=5000, debug=True,
            ssl_context = ('cert.pem','key.pem'))
    except Exception as ex:
        print(sys.argv[0] + str(ex), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()