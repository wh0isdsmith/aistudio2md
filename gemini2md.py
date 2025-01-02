import json
import os
import glob
import re  # Import the 're' module for regular expression operations
import zipfile


def format_markdown(json_data):
    markdown_output = ""

    # --- Header ---
    markdown_output += "# Gemini Pro Conversation\n\n"
    if 'runSettings' in json_data:
        markdown_output += f"**Model:** {json_data['runSettings']['model']}\n"
        markdown_output += f"**Temperature:** {json_data['runSettings']['temperature']}\n\n"

    # --- Citations ---
    if 'citations' in json_data and json_data['citations']:
        markdown_output += "## Citations\n\n"
        for citation in json_data['citations']:
            if 'uri' in citation:
                markdown_output += f"*   [{citation['uri']
                                           }]({citation['uri']})\n"
        markdown_output += "\n"

    # --- System Instructions (Optional) ---
    if 'systemInstruction' in json_data and json_data['systemInstruction']:
        markdown_output += "## System Instructions\n\n"
        markdown_output += json_data['systemInstruction'].get(
            'text', '') + "\n\n"

    # --- Conversation ---
    markdown_output += "## Conversation\n\n"
    if 'chunkedPrompt' in json_data and 'chunks' in json_data['chunkedPrompt']:
        for chunk in json_data['chunkedPrompt']['chunks']:
            if chunk['role'] == 'user':
                markdown_output += "### User\n\n"
            elif chunk['role'] == 'model':
                markdown_output += "### Model\n\n"

            # Handle "thoughts" differently
            if chunk.get('isThought', False):
                markdown_output += "> " + \
                    chunk.get('text', '').replace("\n", "\n> ") + "\n\n"
            else:
                if 'text' in chunk:
                    # Improved code block detection using regular expressions
                    code_block_pattern = r"```(?:\w+\n)?(.*?)```"
                    matches = re.findall(code_block_pattern,
                                         chunk['text'], re.DOTALL)

                    if matches:
                        for code_snippet in matches:
                            markdown_output += "```\n" + code_snippet.strip() + "\n```\n\n"
                    else:
                        markdown_output += chunk['text'] + "\n\n"
    else:
        markdown_output += "No conversation data available.\n\n"

    return markdown_output


def convert_json_to_markdown(input_path, output_path):  # Added output_path argument
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        markdown_content = format_markdown(json_data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"Successfully converted '{input_path}' to '{output_path}'")

    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error processing '{input_path}': {e}")


def unzip_files(directory):
    # Create the AI_Studio_Chats directory if it doesn't exist
    output_dir = os.path.join(directory, 'AI_Studio_Chats')
    os.makedirs(output_dir, exist_ok=True)

    # Find all zip files in the directory
    zip_files = [f for f in os.listdir(directory) if f.endswith('.zip')]

    for zip_file in zip_files:
        zip_path = os.path.join(directory, zip_file)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

    # Rename all files in the output directory to add .json extension
    for filename in os.listdir(output_dir):
        file_path = os.path.join(output_dir, filename)
        if os.path.isfile(file_path) and not filename.endswith('.json'):
            new_file_path = file_path + '.json'
            os.rename(file_path, new_file_path)


if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    unzip_files(script_dir)
    print("Unzipping complete and .json extension added to files.")

    # Construct the path to the AI_Studio_Chats directory
    ai_studio_chats_dir = os.path.join(script_dir, "AI_Studio_Chats")
    # Get all .json files in the AI_Studio_Chats directory
    json_files = glob.glob(os.path.join(ai_studio_chats_dir, "*.json"))

    # Create the Markdown Chats directory in the root
    markdown_chats_dir = os.path.join(script_dir, "Markdown Chats")
    os.makedirs(markdown_chats_dir, exist_ok=True)

    for json_file in json_files:
        # Create output file name with .md extension in the Markdown Chats directory
        base_name = os.path.splitext(os.path.basename(json_file))[0]
        output_file = os.path.join(markdown_chats_dir, f"{base_name}.md")
        convert_json_to_markdown(json_file, output_file)
