import os

def delete_file_if_exists(filename):
    """
    ファイルが存在する場合に安全に削除する
    
    Args:
        filename (str): 削除するファイル名
    """
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"ファイル {filename} を削除しました。")
        except Exception as e:
            print(f"ファイル {filename} の削除中にエラーが発生しました: {e}")
    else:
        print(f"ファイル {filename} は存在しません。")

def combine_files(input_files, output_filename):
    """
    複数のテキストファイルを1つのファイルに結合する
    KitAIでは init.txt + register_bot_func.txt + finish.txt を結合して
    完全なDiscord botスクリプト（execute_combined.py）を生成する
    
    Args:
        input_files (list): 結合するファイルのリスト
        output_filename (str): 出力ファイル名
    """
    combined_content = ""

    # 各ファイルの内容を読み込んで結合
    for file in input_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_content += content + "\n\n"
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # 既存ファイルを削除してから新しいファイルを作成
    delete_file_if_exists(output_filename)
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(combined_content)

        print(f"Syntaxes combined and saved to {output_filename}")
    except Exception as e:
        print(f"Error writing to {output_filename}: {e}")