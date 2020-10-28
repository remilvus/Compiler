import os
import pytest


def check_parser(parser, scanner, text, capfd, filename):
    parser.parse(text, lexer=scanner.lexer)
    out, err = capfd.readouterr()

    assert out == "", f"Failed on {filename}"

def test_parser(capfd):
    import parser as parser_module
    import scanner

    parser = parser_module.parser
    example_dir = "examples"

    for filename in os.listdir(example_dir):
        filename = os.path.join(example_dir, filename)

        file = open(filename, "r")
        text = file.read()

        if "error" in filename:
            with pytest.raises(AssertionError):
                check_parser(parser, scanner, text, capfd, filename)
        else:
            check_parser(parser, scanner, text, capfd, filename)
