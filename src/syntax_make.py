import os

def delete_file_if_exists(filename):
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"ファイル {filename} を削除しました。")
        except Exception as e:
            print(f"ファイル {filename} の削除中にエラーが発生しました: {e}")
    else:
        print(f"ファイル {filename} は存在しません。")

def combine_files(input_files, output_filename):
    combined_content = ""

    for file in input_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_content += content + "\n\n"
        except Exception as e:
            print(f"Error reading {file}: {e}")

    delete_file_if_exists(output_filename)
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(combined_content)

        print(f"Syntaxes combined and saved to {output_filename}")
    except Exception as e:
        print(f"Error writing to {output_filename}: {e}")