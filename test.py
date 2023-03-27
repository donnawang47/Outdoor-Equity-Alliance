
import os

def main():
    DATABASE_URL = os.getenv('DATABASE_URL')
    print(DATABASE_URL)

if __name__ == '__main__':
    main()
