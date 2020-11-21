import sys
import scanner
import parser

if __name__ == '__main__':

    try:
        # filename = sys.argv[1] if len(sys.argv) > 1 else "examples/scanner_example_error.txt"
        filename = sys.argv[1] if len(sys.argv) > 1 else "examples/parser_example_3.txt"
        # filename = sys.argv[1] if len(sys.argv) > 1 else "examples/work_example.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    parser = parser.parser
    text = file.read()

    program = parser.parse(text, lexer=scanner.lexer)
    program.print_tree()
