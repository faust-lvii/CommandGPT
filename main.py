import os
import sys
import subprocess
import json
from dotenv import load_dotenv
import requests
import argparse

load_dotenv()
will_be_executed, debug_mode = False, False


class LocalLLM:
    def __init__(self, base_url, api_key, model, temperature, max_tokens=500):
        self.base_url = base_url
        self.api_key = api_key if api_key else "dummy_api_key_for_local"
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def send(self, system_message, user_message):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        try:
            if debug_mode:
                print(f"Sending request to: {url}")
                print(f"Request data: {json.dumps(data, indent=2)}")
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()  # Raise an error for non-200 status codes
            response_json = json.loads(response.text)
            
            if debug_mode:
                print(f"Response: {json.dumps(response_json, indent=2)}")
                
            if "choices" in response_json and len(response_json["choices"]) > 0:
                return response_json["choices"][0]["message"]["content"].strip()
            else:
                return "Error: Unexpected API response format"
        except requests.exceptions.RequestException as e:
            error_msg = f"API Request Error: {str(e)}"
            if debug_mode:
                print(error_msg)
                print(f"Response: {response.text if 'response' in locals() else 'No response'}")
            return error_msg
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            if debug_mode:
                print(error_msg)
            return error_msg


def parse_args(input):
    parser = argparse.ArgumentParser(description="CommandGPT - Convert between command languages and natural language")
    parser.add_argument("-i", "--input", help="Input language (nat, bash, ps)", required=True)
    parser.add_argument("-o", "--output", help="Output language (nat, bash, ps)", required=True)
    parser.add_argument("-c", "--command", help="Command to be converted", required=True)
    parser.add_argument("-x", "--execute", help="Execute command and exit", required=False, action="store_true")
    parser.add_argument("-d", "--debug", help="Debug mode", required=False, action="store_true")
    parser.add_argument("--url", help="Local LLM server URL", default=os.getenv("LLM_BASE_URL", "http://localhost:1234/v1"))
    parser.add_argument("--model", help="Model name", default=os.getenv("LLM_MODEL_NAME", "local-model"))
    parser.add_argument("--temp", help="Temperature (0.0-1.0)", type=float, default=float(os.getenv("LLM_TEMPERATURE", "0.2")))
    parser.add_argument("--max-tokens", help="Maximum tokens in response", type=int, default=int(os.getenv("LLM_MAX_TOKENS", "500")))
    args = parser.parse_args(input)
    return args.input, args.output, args.command, args.execute, args.debug, args.url, args.model, args.temp, args.max_tokens


def convert(input_type, output_type, command_to_convert, base_url=None, model_name=None, temperature=0.2, max_tokens=500):
    # Set default values if not provided
    base_url = base_url or os.getenv("LLM_BASE_URL") or "http://localhost:1234/v1"
    model_name = model_name or os.getenv("LLM_MODEL_NAME") or "local-model"
    api_key = os.getenv("OPENAI_API_KEY")  # Optional for many local LLMs
    
    llm = LocalLLM(
        base_url=base_url, 
        api_key=api_key, 
        model=model_name, 
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    longs = {"bash": "Bash", "ps": "PowerShell", "nat": "Natural Language"}
    short_longs = {"bash": "Bash", "ps": "PS", "nat": "NL"}
    
    # Craft more effective system and user prompts
    system_message = f"""You are CommandGPT, an expert in command line interfaces and scripting languages.
Your only purpose is to translate between {longs[input_type]} and {longs[output_type]}.
- Provide ONLY the converted command or explanation with no additional text
- Do not include explanations, notes, or markdown formatting
- Ensure your translation is accurate and follows best practices
"""
    
    user_message = f"""Convert this {longs[input_type]} to {longs[output_type]}:
{command_to_convert}"""
    
    try:
        result = llm.send(system_message, user_message)
        
        # Clean up the response
        result = result.strip()
        # Remove markdown code blocks if present
        if result.startswith("```") and result.endswith("```"):
            result = result[result.find("\n")+1:result.rfind("```")].strip()
        elif result.startswith("`") and result.endswith("`"):
            result = result[1:-1].strip()
            
        # Remove phrases like "Here is the equivalent..." or "In PowerShell, ..."
        common_prefixes = [
            f"Here is the {longs[output_type]} equivalent:", 
            f"The {longs[output_type]} equivalent is:", 
            f"In {longs[output_type]},", 
            f"The {longs[output_type]} version would be:",
            f"{longs[output_type]} equivalent:",
            f"{short_longs[output_type]} equivalent:"
        ]
        
        for prefix in common_prefixes:
            if result.lower().startswith(prefix.lower()):
                result = result[len(prefix):].strip()
        
        return result
    except Exception as converting_error:
        return f"An error occurred while converting. Is your LLM server running? (Error: {converting_error})"


def ascii_art():
    return """
█▀▀ █▀█ █▀▄▀█ █▀▄▀█ ▄▀█ █▄░█ █▀▄ █▀▀ █▀█ ▀█▀
█▄▄ █▄█ █░▀░█ █░▀░█ █▀█ █░▀█ █▄▀ █▄█ █▀▀ ░█░
    """


def run_powershell(powershell_script):
    try:
        result = subprocess.run(["powershell", "-Command", powershell_script], 
                             capture_output=True, text=True)
        print(result.stdout)
        if result.stderr and debug_mode:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        if debug_mode:
            print(f"Error executing PowerShell: {str(e)}")
        return False


def run_bash(bash_script):
    try:
        result = subprocess.run(["bash", "-c", bash_script], 
                             capture_output=True, text=True)
        print(result.stdout)
        if result.stderr and debug_mode:
            print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        if debug_mode:
            print(f"Error executing Bash: {str(e)}")
        return False


def interactive_mode():
    print(ascii_art())
    
    # Get environment variables or use defaults
    base_url = os.getenv("LLM_BASE_URL") or "http://localhost:1234/v1"
    model_name = os.getenv("LLM_MODEL_NAME") or "local-model"
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "500"))
    
    if debug_mode:
        print(f"Using LLM at: {base_url}")
        print(f"Model: {model_name}")
        print(f"Temperature: {temperature}")
        print(f"Max tokens: {max_tokens}")
    
    options = [
        "Natural Language to Bash",
        "Natural Language to PowerShell",
        "Bash to Natural Language",
        "Bash to PowerShell",
        "PowerShell to Natural Language",
        "PowerShell to Bash",
        "Exit"
    ]
    
    while True:
        print("\nCommandGPT Options:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        try:
            choice = int(input("\nEnter your choice: "))
            if choice < 1 or choice > len(options):
                print("Invalid choice. Please try again.")
                continue
                
            if choice == 7:  # Exit
                print("Exiting CommandGPT. Goodbye!")
                break
                
            # Map choices to input and output types
            map_of_choices = {
                1: ["nat", "bash"],
                2: ["nat", "ps"],
                3: ["bash", "nat"],
                4: ["bash", "ps"],
                5: ["ps", "nat"],
                6: ["ps", "bash"]
            }
            
            input_type, output_type = map_of_choices[choice]
            
            # Get the command to convert
            command = input(f"Enter the {options[choice-1].split(' to ')[0]} to convert: ")
            if not command.strip():
                print("Command cannot be empty. Please try again.")
                continue
                
            # Perform the conversion
            print("\nConverting...")
            result = convert(input_type, output_type, command, base_url, model_name, temperature, max_tokens)
            
            # Pretty output based on the conversion type
            print(f"\n{options[choice-1].split(' to ')[1]} equivalent:")
            print(f"{result}")
            
            # Offer to execute if the output is a command
            if output_type in ["bash", "ps"]:
                execute = input("\nDo you want to execute this command? (y/n): ").lower().strip() == 'y'
                if execute:
                    print("\nExecuting command...")
                    if output_type == "ps" and os.name == "nt":
                        run_powershell(result)
                    elif output_type == "bash" and os.name != "nt":
                        run_bash(result)
                    else:
                        print(f"Cannot execute {output_type} command on this system.")
            
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            continue
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            if debug_mode:
                import traceback
                traceback.print_exc()
    

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        input_type, output_type, command, will_be_executed, debug_mode, base_url, model_name, temperature, max_tokens = parse_args(args)
        cmd = convert(input_type, output_type, command, base_url, model_name, temperature, max_tokens)
        print(cmd)
        
        if will_be_executed:
            if output_type == "ps" and os.name == "nt":
                run_powershell(cmd)
            elif output_type == "bash" and os.name != "nt":
                run_bash(cmd)
            else:
                print(f"Cannot execute {output_type} command on this system.")
    else:
        try:
            interactive_mode()
        except KeyboardInterrupt:
            print("\nExiting CommandGPT. Goodbye!")
            