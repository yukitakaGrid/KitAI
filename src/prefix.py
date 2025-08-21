def indent_text(text, num_spaces=4):
    """
    テキストの各行を指定されたスペース数でインデントする
    GPT-4生成コードを適切にフォーマットするために使用
    
    Args:
        text (str): インデントするテキスト
        num_spaces (int): インデントするスペース数（デフォルト: 4）
        
    Returns:
        str: インデントされたテキスト
    """
    lines = text.split('\n')
    indented_lines = [(' ' * num_spaces) + line for line in lines]
    indented_text = '\n'.join(indented_lines)
    return indented_text

def green_lines_with_prefix(text, prefix):
    """
    テキストをDiscordの差分表示形式（diff）でフォーマット
    機能実装完了メッセージなどで使用
    
    Args:
        text (str): フォーマットするテキスト
        prefix (str): 各行の先頭に付けるプレフィックス（通常"+"）
        
    Returns:
        str: Discord用差分表示形式のテキスト
    """
    lines = text.strip().split('\n')
    formatted_lines = [f"{prefix}{line}" for line in lines]
    formatted_text = '\n'.join(formatted_lines)
    formatted_text_color = '''```diff
''' + formatted_text + '''
```
'''
    return formatted_text_color