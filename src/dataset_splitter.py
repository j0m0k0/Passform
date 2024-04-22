def extract_first_lines(input_filepath, output_filepath, num_lines=16000):
    """
    Extracts the first 'num_lines' lines from a file specified by 'input_filepath'
    and writes them to a new file specified by 'output_filepath'.
    
    :param input_filepath: Path to the input text file (string).
    :param output_filepath: Path to the output text file (string).
    :param num_lines: Number of lines to extract (int).
    """
    try:
        with open(input_filepath, 'r', encoding='utf-8') as file_in:
            with open(output_filepath, 'w', encoding='utf-8') as file_out:
                for i, line in enumerate(file_in):
                    if i < num_lines:
                        file_out.write(line)
                    else:
                        break
        print(f"Successfully wrote the first {num_lines} lines from {input_filepath} to {output_filepath}")
    except FileNotFoundError:
        print(f"Error: The file {input_filepath} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
# Assuming 'rockyou.txt' is in the same directory as this script
input_file = '../dataset/rockyou.txt'
output_file = '../dataset/rockyou16k.txt'
extract_first_lines(input_file, output_file)
