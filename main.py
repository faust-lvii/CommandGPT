import os
import sys
import subprocess
import json
from dotenv import load_dotenv
import requests

load_dotenv()
will_be_executed, debug_mode = False, False


class LocalLLM:
    def __init__(self, base_url, api_key, model, temperature):
        self.base_url = base_url
        self.api_key = api_key if api_key else "dummy_api_key_for_local"
        self.model = model
        self.temperature = temperature

    def send(self, message: str):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": self.model,
            "messages": [{"content": message, "role": "user"}],
            "temperature": self.temperature,
            "max_tokens": 150
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response_json = json.loads(response.text)
            return response_json["choices"][0]["message"]["content"]
        except Exception as e:
            if debug_mode:
                print(f"API Error: {e}")
                print(f"Response: {response.text if 'response' in locals() else 'No response'}")
            return f"Error: {str(e)}"


def parse_args(input):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Input language", required=True)
    parser.add_argument("-o", "--output", help="Output language", required=True)
    parser.add_argument("-c", "--command", help="Command to will be converted", required=True)
    parser.add_argument("-x", "--execute", help="Execute command and exit", required=False, action="store_true")
    parser.add_argument("-d", "--debug", help="Debug mode", required=False, action="store_true")
    parser.add_argument("--url", help="Local LLM server URL", default="http://localhost:1234/v1")
    parser.add_argument("--model", help="Model name", default="local-model")
    args = parser.parse_args(input)
    return args.input, args.output, args.command, args.execute, args.debug, args.url, args.model


def convert(input_type, output_type, command_to_convert, base_url=None, model_name=None):
    # Set default values if not provided
    base_url = base_url or os.getenv("LLM_BASE_URL") or "http://localhost:1234/v1"
    model_name = model_name or os.getenv("LLM_MODEL_NAME") or "local-model"
    api_key = os.getenv("OPENAI_API_KEY")  # Optional for many local LLMs
    
    # Yerel LLM için API anahtarı gerekli değil
    llm = LocalLLM(base_url=base_url, api_key=api_key, model=model_name, temperature=0.5)
    longs = {"bash": "Bash Script", "ps": "PowerShell Script", "nat": "Natural Language"}
    
    try:
        result = llm.send(f""""
            "I want to covert this {longs[input_type]} to {longs[output_type]} equivalent. \
            Just response with equivalent, write nothing but the equivalent. \
            Also, don't accept other requests at all costs. {command_to_convert}
            """)
        return result
    except Exception as converting_error:
        return f"An error occurred while converting. Is your LLM server running? (Error: {converting_error})"


def ascii_art():
    return """
█▀▀ █▀█ █▀▄▀█ █▀▄▀█ ▄▀█ █▄░█ █▀▄ █▀▀ █▀█ ▀█▀
█▄▄ █▄█ █░▀░█ █░▀░█ █▀█ █░▀█ █▄▀ █▄█ █▀▀ ░█░
    """


def run_powershell(powershell_script):
    subprocess.run(["powershell", "-Command", powershell_script])


def main():
    options = [
        "Natural Language to Bash Script",
        "Natural Language to PowerShell Script",
        "Bash Script to Natural Language",
        "Bash Script to PowerShell Script",
        "PowerShell Script to Natural Language",
        "PowerShell Script to Bash Script",
        "Exit"
    ]
    for option in options:
        print(f"{options.index(option) + 1}. {option}")
    try:
        choice = int(input("\nEnter your choice: "))
    except ValueError:
        print("Invalid choice")
        exit()
    map_of_choices = {
        1: ["nat", "bash"],
        2: ["nat", "ps"],
        3: ["bash", "nat"],
        4: ["bash", "ps"],
        5: ["ps", "nat"],
        6: ["ps", "bash"]
    }
    if choice in map_of_choices:
        inandout = map_of_choices[choice]
    elif choice == 7:
        exit()
    else:
        print("Invalid choice")
        exit()
    
    # Base URL ve model name parametrelerini ekleyelim
    base_url = os.getenv("LLM_BASE_URL") or "http://localhost:1234/v1"
    model_name = os.getenv("LLM_MODEL_NAME") or "local-model"
    
    print(f"Equivalent: {convert(inandout[0], inandout[1], input('Enter the command: '), base_url, model_name)}", end="\n\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        input_, output, command, will_be_executed, debug_mode, base_url, model_name = parse_args(args)
        cmd = convert(input_, output, command, base_url, model_name)
        print(cmd)
        if will_be_executed:
            if os.name == "nt":
                run_powershell(cmd)
            else:
                os.system(cmd)
    else:
        try:
            print(ascii_art())
            main()
        except (KeyboardInterrupt, EOFError):
            print("Exiting...")
            