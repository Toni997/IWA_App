import re

CRLF = b'\r\n'
TEMPLATES_DIR = b'templates/'

INCLUDE_PATTERN = rb"{%\sinclude\s([A-Za-z0-9._\-]+)\s%}"
FOR_BEGIN_PATTERN = rb"{%\sfor\s([a-zA-Z0-9]+)\sin\s([a-zA-Z0-9]+)\s%}"
END_FOR_PATTERN = rb"{%\send\sfor\s%}"
IF_PATTERN = rb"{%\sif\s([0-9a-zA-Z_]+)\s%}"
ELSE_PATTERN = rb"{%\selse\s%}"
END_IF_PATTERN = rb"{%\send\sif\s%}"
VARIABLE_PATTERN = rb"{{\s([A-Za-z0-9_.]+)\s}}"


class TemplateEngine:
    def __init__(self, file_name, context: dict) -> None:
        self.__file_name = file_name
        self.__content: bytes = b''
        self.__context = context

        self.__process(self.__file_name)

    def __bytes__(self):
        return self.__content

    def __process(self, file_name) -> None:
        with open(file_name, 'rb') as file:
            self.__content = file.read()
        self.__handle_includes()
        self.__handle_for_loops()
        self.__handle_all_vars()
        self.__handle_if_statements()

    def __handle_includes(self):
        match = re.search(INCLUDE_PATTERN, self.__content)
        while match:
            replace_what_begin = match.regs[0][0]
            replace_what_end = match.regs[0][1]
            replace_what = self.__content[replace_what_begin:replace_what_end]
            file_name_begin = match.regs[1][0]
            file_name_end = match.regs[1][1]
            file_name = self.__content[file_name_begin:file_name_end]
            with open(TEMPLATES_DIR + file_name, 'rb') as file:
                replace_with = file.read()
            self.__content = self.__content.replace(replace_what, replace_with)
            match = re.search(INCLUDE_PATTERN, self.__content)

    def __handle_for_loops(self) -> None:
        match = re.search(FOR_BEGIN_PATTERN, self.__content)
        while match:
            replace_with_total = b''
            replace_what_begin = match.regs[0][0]
            match_end_loop = re.search(END_FOR_PATTERN, self.__content)
            replace_what_end = match_end_loop.regs[0][1]
            replace_what = self.__content[replace_what_begin:replace_what_end]
            replace_with_begin = match.regs[0][1]
            replace_with_end = match_end_loop.regs[0][0]
            replace_with = self.__content[replace_with_begin:replace_with_end]
            var_name = self.__content[match.regs[1][0]:match.regs[1][1]]
            loop_over_what = self.__content[match.regs[2][0]:match.regs[2][1]].decode('ascii')
            for each in self.__context[loop_over_what]:
                replace_with_total += self.__handle_loop_vars(replace_with, var_name, each)
            self.__content = self.__content.replace(replace_what, replace_with_total)
            match = re.search(INCLUDE_PATTERN, self.__content)

    def __handle_loop_vars(self, content: bytes, var_name: str, each: dict) -> bytes:
        match = re.search(VARIABLE_PATTERN, content)
        while match:
            replace_what_begin = match.regs[0][0]
            replace_what_end = match.regs[0][1]
            replace_what = content[replace_what_begin:replace_what_end]
            var_path_begin = match.regs[1][0]
            var_path_end = match.regs[1][1]
            var_path = content[var_path_begin:var_path_end]
            var_paths = var_path.split(b'.')
            if var_paths.pop(0) != var_name:
                print("Syntax error: Could not process for loop")
                return var_path
            replace_with = var_path
            for path in var_paths:
                replace_with = str(each[path.decode('ascii')]).encode('utf-8')
            content = content.replace(replace_what, replace_with)
            match = re.search(VARIABLE_PATTERN, content)
        return content

    def __handle_all_vars(self) -> None:
        match = re.search(VARIABLE_PATTERN, self.__content)
        while match:
            replace_what_begin = match.regs[0][0]
            replace_what_end = match.regs[0][1]
            replace_what = self.__content[replace_what_begin:replace_what_end]
            var_name_begin = match.regs[1][0]
            var_name_end = match.regs[1][1]
            var_name = self.__content[var_name_begin:var_name_end]
            replace_with = str(self.__context[var_name.decode('ascii')]).encode('utf-8')
            self.__content = self.__content.replace(replace_what, replace_with)
            match = re.search(VARIABLE_PATTERN, self.__content)

    def __handle_if_statements(self) -> None:
        if_found = re.search(IF_PATTERN, self.__content)
        while if_found:
            if_begin = if_found.regs[0][0]
            if_end = if_found.regs[0][1]
            var_begin = if_found.regs[1][0]
            var_end = if_found.regs[1][1]
            var_name = self.__content[var_begin:var_end]
            var_name = var_name.decode()
            else_found = re.search(ELSE_PATTERN, self.__content)
            if else_found:
                else_begin = else_found.regs[0][0]
                else_end = else_found.regs[0][1]
                replace_what = self.__content[if_begin:else_begin]
                replace_with = self.__content[if_end:else_begin] if self.__context[var_name] else b''
                self.__content = self.__content.replace(replace_what, replace_with)
                else_found = re.search(ELSE_PATTERN, self.__content)
                else_begin = else_found.regs[0][0]
                else_end = else_found.regs[0][1]
                end_if = re.search(END_IF_PATTERN, self.__content)
                end_if_begin = end_if.regs[0][0]
                end_if_end = end_if.regs[0][1]
                replace_what = self.__content[else_begin:end_if_end]
                replace_with = self.__content[else_end:end_if_begin] if not self.__context[var_name] else b''
                self.__content = self.__content.replace(replace_what, replace_with)
            else:
                end_if = re.search(END_IF_PATTERN, self.__content)
                end_if_begin = end_if.regs[0][0]
                end_if_end = end_if.regs[0][1]
                replace_what = self.__content[if_begin:end_if_end]
                replace_with = self.__content[if_end:end_if_begin] if self.__context[var_name] else b''
                self.__content = self.__content.replace(replace_what, replace_with)
            if_found = re.search(IF_PATTERN, self.__content)
