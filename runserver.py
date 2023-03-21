#----------------------------------------------------------------------- 
#-----------------------------------------------------------------------

import sys


def main():
  
  if len(sys.argv) != 2:
    print('Usage: ' + sys.argv[0] + ' port', file=sys.stderr)
    sys.exit(1)
    
   try:
    port = int(sys.argv[1])
   except Exception:
    print('Port must be an integer.', file=sys.stderr)
    sys.exit(1)
    
   try:
    penny.app.run(host='0.0.0.0', port=port, debug=True) # debug=True for now
   except Exception as ex:
    print(ex, file=sys.stderr)
    sys.exit(1)
    
if __name__ == '__main__':
  main()
