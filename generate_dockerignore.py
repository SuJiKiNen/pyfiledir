def transform_line(line):
    if line.strip() == '':
        return line
    if line.startswith('#'):
        return line
    if line.startswith('!/'):
        return '!' + line[2:]
    if line.startswith('!'):
        return '!**/' + line[1:]
    if line.startswith('/'):
        return line[1:]
    return '**/' + line


def transform():
    try:
        with open(".gitignore", "r") as gitigonre:
            gitigonre_lines = gitigonre.readlines()
            with open(".dockerignore", "w") as dockerignore:
                for line in gitigonre_lines:
                    dockerignore.write(transform_line(line))
    except FileNotFoundError:
        pass


if __name__ == '__main__':
    import sys
    sys.exit(transform())
