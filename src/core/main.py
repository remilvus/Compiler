import sys
from src.scanner import scanner
from src.parser import parser
from src.type_checker.node_visitor import TypeChecker
from src.interpreter.interpreter import Interpreter

if __name__ == '__main__':

    try:
        # filename = sys.argv[1] if len(sys.argv) > 1 else "examples/types_example_3.txt"
        # filename = sys.argv[1] if len(sys.argv) > 1 else "examples/type_errors.txt"
        filename = sys.argv[1] if len(sys.argv) > 1 else "examples/interpreter_example_6.txt"
        # filename = sys.argv[1] if len(sys.argv) > 1 else "examples/work_example_2.txt"
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    parser = parser.parser
    text = file.read()

    try:
        ast = parser.parse(text, lexer=scanner.lexer)
        ast.print_tree()

        typeChecker = TypeChecker()
        typeChecker.visit(ast)

        if typeChecker.correct:
            interpreter = Interpreter()
            interpreter.visit(ast)

    except SyntaxError as error:
        print(error.msg)
