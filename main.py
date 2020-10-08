import sys
import scanner

if __name__ == '__main__':

    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()
    lexer = scanner.lexer  
    lexer.input(text)

    # Tokenize
    while True:
        tok = lexer.token()
        if not tok: 
            break    # No more input

        print("({}): |{:15.15} |{}|".format(tok.lineno, tok.type + '|', tok.value))
