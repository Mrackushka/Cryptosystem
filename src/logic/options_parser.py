from .file_operations import load_text_from_file, file_writer_factory


class OptionsParser:
    def __init__(self, cli_options, cipher_method_names):
        self.cli_options = cli_options
        self.cipher_method_names = cipher_method_names

    def parse_options(self):
        input_text = self.get_input()
        file_writer = self.get_output()
        cipher_method_name = self.get_chosen_cipher_method_name()
        return self.cli_options, input_text, cipher_method_name, file_writer

    def get_input(self):
        if input_text := self.cli_options["text"]:
            pass
        else:
            input_text = load_text_from_file(self.cli_options["file"])
        del self.cli_options["text"]
        del self.cli_options["file"]
        return input_text

    def get_output(self):
        if out_file_path := self.cli_options["out"]:
            file_writer = file_writer_factory(out_file_path)
        else:

            def file_writer(text):
                print(text)

        del self.cli_options["out"]
        return file_writer

    def get_chosen_cipher_method_name(self):
        cipher_method_name = ""
        for name in self.cipher_method_names:
            option_value = self.cli_options[name]
            if option_value:
                cipher_method_name = name
            del self.cli_options[name]
        return cipher_method_name
