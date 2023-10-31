def indent_text(text, num_spaces=4):
    lines = text.split('\n')
    indented_lines = [(' ' * num_spaces) + line for line in lines]
    indented_text = '\n'.join(indented_lines)
    return indented_text

def green_lines_with_prefix(text, prefix):
    lines = text.strip().split('\n')
    formatted_lines = [f"{prefix}{line}" for line in lines]
    formatted_text = '\n'.join(formatted_lines)
    formatted_text_color = '''```diff
''' + formatted_text + '''
```
'''
    return formatted_text_color