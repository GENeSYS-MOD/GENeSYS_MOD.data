import os

def search_non_utf8_characters(file_dir):
    data_folder = file_dir
    error_messages = []

    for root, dirs, files in os.walk(data_folder):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                non_utf8_lines = []

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_number, line in enumerate(f, start=1):
                            #1+1 # Something needs to be done in python in try-part. Hence, placeholder to minimize computing power.  See below for code that iterates search of non-utf-8-characters over lines of utf-8-openable files.
                            try: 
                                line.encode('utf-8')
                            except UnicodeEncodeError as e:
                                # Log the line number and file that causes the error
                                print(f"UTF-8 encoding error in file '{file_path}' at line {line_number}: {e}")
                                non_utf8_lines.append(line_number)
                except UnicodeDecodeError:
                    with open(file_path, 'rb') as f:
                        line_number = 0
                        for line in f:
                            line_number += 1
                            try:
                                line.decode('utf-8')
                            except UnicodeDecodeError as e:
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

