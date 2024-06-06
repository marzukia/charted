def indent_line(line: str, level: int, indent: int) -> str:
    """Indent a line based on the current nesting level.

    Args:
        line (str): The HTML line to indent.
        level (int): The current level of nesting.
        indent (int): The number of spaces to use for each level of indentation.

    Returns:
        str: The indented line.
    """
    return " " * (level * indent) + line


def format_html(html: str, indent: int = 2) -> str:
    """Pretty format the given HTML string.

    Args:
        html (str): The HTML string to format.
        indent (int): The number of spaces to use for indentation.

    Returns:
        str: The pretty-formatted HTML string.
    """
    lines = html.replace(">", ">\n").replace("<", "\n<").split("\n")
    pretty_lines, level = [], 0

    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        if stripped_line.startswith("</"):
            level -= 1
            pretty_lines.append(indent_line(line, level, indent))
        elif stripped_line.startswith("<") and not (
            stripped_line.startswith("<!") or stripped_line.endswith("/>")
        ):
            pretty_lines.append(indent_line(line, level, indent))
            level += 1
        else:
            pretty_lines.append(indent_line(line, level, indent))

    return "\n".join(pretty_lines)
