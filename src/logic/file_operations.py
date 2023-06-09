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
        unicode_exception_occured = False
        while True:
            if not path.exists(file_path) or rewrite_file:
                with open(file_path, "w", encoding="utf-8") as f:
                    for letter in text:
                        try:
                            f.write(letter)
                        except UnicodeEncodeError:
                            unicode_exception_occured = True
                            f.write("?")
                print("File was successfully written.")
                if unicode_exception_occured:
                    print(
                        "But due to UnicodeEncodeException symbols wich "
                        "Python can't encode were replaced by '?', "
                        "so it might not be properly decoded."
                    )
                break
            else:
                rewrite_file = input(
                    f"Sorry, but file '{file_path}' already exists.\n"
                    f"Do you want to rewrite it [Y/N]? "
                )
                if not rewrite_file.lower() in ["y", "yes", "yeah"]:
                    print("Aborted =/")
                    exit(0)

    return write_text_to_file
