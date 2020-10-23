import sys
import scanner
import parser

if __name__ == '__main__':

    try:
        # filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
        filename = sys.argv[1] if len(sys.argv) > 1 else "example_2.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    parser = parser.parser
    text = file.read()
    parser.parse(text, lexer=scanner.lexer)

    # Tokenize
    while True:
        tok = scanner.lexer.token()
        if not tok: 
            break    # No more input

        print("({}): |{:15.15} |{}|".format(tok.lineno, tok.type + '|', tok.value))
