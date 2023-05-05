from os import path


def load_text_from_file(file_path):
    if path.exists(file_path):
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    else:
        print(f"Sorry, but no '{file_path}' file was found :c")
        exit(0)


def file_writer_factory(file_path):
    def write_text_to_file(text):
        rewrite_file = False
        while True:
            if not path.exists(file_path) or rewrite_file:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print('File was successfully written.')
                break
            else:
                rewrite_file = input(
                    f"Sorry, but file '{file_path}' already exists.\n"
                    f"Do you want to rewrite it [Y/N]? "
                )
                if not rewrite_file.lower() in ['y', 'yes', 'yeah']:
                    print('Aborted =/')
                    exit(0)

    return write_text_to_file
