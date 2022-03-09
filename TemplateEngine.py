BEGIN_FOR_LOOP = b'{% for'
END_FOR_LOOP = b'{% end for %}'
DELIMITER_OPEN = b'{% '
DELIMITER_CLOSE = b' %}'


class TemplateEngine:
    def __init__(self, file_name, context_obj: dict):
        self.__file_name = file_name
        self.__context_obj = context_obj
        self.__processed_lines = list()
        self.__process_template()

    def __bytes__(self) -> bytes:
        return b''.join(self.__processed_lines)

    def __process_template(self):
        with open(self.__file_name, 'rb') as file:
            current_context = None
            section_to_loop = b''
            for_loop_started = False
            for line in file:
                if for_loop_started:
                    found_end_for = line.find(END_FOR_LOOP)
                    if found_end_for != -1:
                        for_loop_started = False
                        self.__processed_lines.extend(self.__handle_for_loop(section_to_loop, current_context))
                    else:
                        section_to_loop += line
                else:
                    found = line.find(BEGIN_FOR_LOOP)
                    if found != -1:
                        for_loop_started = True
                        found_end = line.find(DELIMITER_CLOSE)
                        for_statement_parts = line[found+3:found_end].split()
                        current_context = for_statement_parts[3]
                    else:
                        found_include = line.find(b'{% include')
                        if found_include != -1:
                            self.__processed_lines.extend(self.__handle_include(line))
                        else:
                            self.__processed_lines.append(line)

    def __handle_for_loop(self, section: bytes, context) -> list:
        lines_to_add = list()
        ctx = context.decode('utf-8')
        for c in self.__context_obj.get(ctx):
            current_section = section
            begin = current_section.find(b'{{')
            while begin != -1:
                end = current_section[begin+2:].find(b' }}')
                attribute_name = current_section[begin+3:begin+2+end]
                attribute_name = attribute_name.decode('ascii')
                replace_what = current_section[begin:begin+2+end+3]
                replace_with = c[attribute_name]
                replace_with = str(replace_with) if not isinstance(replace_what, str) else replace_what
                replace_with = replace_with.encode('ascii')
                current_section = current_section.replace(replace_what, replace_with)
                begin = current_section.find(b'{{')
            lines_to_add.append(current_section)
        return lines_to_add

    def __handle_include(self, include_statement: bytes) -> list:
        lines_to_add = list()
        file_name_begin = include_statement.find(b'include ')+8
        file_name_end = include_statement.find(b' %}')
        file_name = b'templates/' + include_statement[file_name_begin:file_name_end]
        with open(file_name, 'rb') as file:
            for line in file:
                lines_to_add.append(line)
        return lines_to_add
