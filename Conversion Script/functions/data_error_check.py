import os

def search_non_utf8_characters(file_dir):
    data_folder = file_dir
    error_messages = []

    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                non_utf8_lines = []

                # Fast path: one whole-file decode (C speed). Only when that
                # fails do we fall back to per-line decoding to report the
                # offending line numbers. The old per-line loop re-encoded
                # every line of every valid file, which dominated startup.
                with open(file_path, 'rb') as f:
                    raw = f.read()
                try:
                    raw.decode('utf-8')
                except UnicodeDecodeError:
                    for line_number, line in enumerate(raw.splitlines(), start=1):
                        try:
                            line.decode('utf-8')
                        except UnicodeDecodeError:
                            non_utf8_lines.append(line_number)

                if non_utf8_lines:
                    # Find index of 'Data' in absolute file path
                    data_index = file_path.find('Data')
                    if data_index != -1:
                        # Construct relative path with 'GENeSYS-MOD' prefix
                        relative_path = f"GENeSYS-MOD\{file_path[data_index:].lstrip(os.path.sep)}"
                    else:
                        relative_path = file_path

                    # Build error message for this file
                    if len(non_utf8_lines) == 1:
                        error_message = f"Non UTF-8 characters found in file '{relative_path}' in line {non_utf8_lines[0]}. Try saving the file in UTF-8 or use UTF-8-characters.\n"
                    else:
                        error_message = f"Non UTF-8 characters found in file '{relative_path}' in lines {', '.join(map(str, non_utf8_lines))}. Try saving the file in UTF-8 or use UTF-8-characters.\n"
                    error_messages.append(error_message)

    if error_messages:
        # Raise all collected error messages
        raise ValueError("\n".join(error_messages))

