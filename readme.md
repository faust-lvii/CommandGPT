### CommandGPT

CommandGPT is a command line tool for converting between natural language and shell commands. This version supports both OpenAI API and local LLMs through services like LM Studio, Ollama, and others.

Features:
- Natural Language to PowerShell command
- Natural Language to Bash command
- Bash to PowerShell command
- PowerShell to Natural Language
- Bash to Natural Language
- PowerShell to Bash command

#### Requirements

- Python 3.6+
- Local LLM server (LM Studio, Ollama, etc.) or OpenAI API key

#### Installation

```bash
pip install -r requirements.txt
```

#### Configuration

Copy the example environment file and configure it for your needs:

```bash
cp .env.example .env
```

Edit the `.env` file to configure your LLM settings:

```
# LLM API Settings
LLM_BASE_URL=http://localhost:1234/v1  # URL of your local LLM server
LLM_MODEL_NAME=local-model             # Name of the model to use
LLM_TEMPERATURE=0.2                    # Lower for more precise results
LLM_MAX_TOKENS=500                     # Max tokens in the response

# Only needed if using OpenAI API instead of a local LLM
# OPENAI_API_KEY=your_api_key_here
```

#### Using with LM Studio

1. Download and install [LM Studio](https://lmstudio.ai/)
2. Load your desired model in LM Studio
3. Start the local inference server (usually on port 1234)
4. Make sure your `.env` file has the correct URL (typically `http://localhost:1234/v1`)
5. Run CommandGPT as shown below

##### Recommended Models for LM Studio

For best performance with command conversions, we recommend these models:

| Model | Size | Good for |
|-------|------|----------|
| CodeLlama | 7B, 13B, 34B | General code and command translations |
| DeepSeek Coder | 6.7B, 33B | Precise code generation and bash/PowerShell |
| WizardCoder | 7B, 13B, 34B | Command explanations and translations |
| Mixtral | 8x7B | Well-rounded performance for all conversion types |
| Mistral | 7B | Good balance of size and performance |

To use with LM Studio:
1. Download your preferred model in LM Studio's Models tab
2. Select the model and start the local server
3. Configure `.env` with the correct model name if needed

#### Usage

**Interactive Mode:**

https://user-images.githubusercontent.com/47084109/231006889-ceb8d60c-dea3-4c8f-88d6-a50be29ee615.mp4

```bash
python main.py
```

**Command Line Mode:**

https://user-images.githubusercontent.com/47084109/231006746-ccd82554-0ec7-431e-a612-bbb3f29f0dd4.mp4

```bash
python main.py [-h] -i INPUT -o OUTPUT -c COMMAND [-x] [-d] [--url URL] [--model MODEL] [--temp TEMP] [--max-tokens MAX_TOKENS]
```

### Options:

```
-h, --help              Show this help message and exit
-i INPUT, --input INPUT
                        Input language (nat, bash, ps)
-o OUTPUT, --output OUTPUT
                        Output language (nat, bash, ps)
-c COMMAND, --command COMMAND
                        Command to be converted
-x, --execute           Execute command and exit
-d, --debug             Debug mode
--url URL               Local LLM server URL
--model MODEL           Model name
--temp TEMP             Temperature (0.0-1.0)
--max-tokens MAX_TOKENS Maximum tokens in response
```

#### Examples

**Command Line Examples:**

Convert a natural language request to a PowerShell command:
```bash
python main.py -i nat -o ps -c "Create a file named test.txt"
```

Convert a Bash command to PowerShell:
```bash
python main.py -i bash -o ps -c "ls -la | grep '.txt'"
```

Run with debug info and custom temperature:
```bash
python main.py -i nat -o bash -c "Find all PDF files modified in the last week" -d --temp 0.1
```

**Interactive Mode Examples:**

- Convert Natural Language to PowerShell command:
```
CommandGPT Options:
1. Natural Language to Bash
2. Natural Language to PowerShell
3. Bash to Natural Language
4. Bash to PowerShell
5. PowerShell to Natural Language
6. PowerShell to Bash
7. Exit

Enter your choice: 2
Enter the Natural Language to convert: Create a file named test.txt

Converting...

PowerShell equivalent:
New-Item -ItemType File -Path "test.txt"
```

#### Using with Different Local LLMs

This version of CommandGPT is compatible with any OpenAI API-compatible inference server, including:

- **LM Studio**: Great for testing different models locally. Supports a wide range of models.
- **Ollama**: Easy to use for various open-source models like Llama, Mistral, and CodeLlama.
- **LocalAI**: Another good option for running models locally.

For best results with command conversions, we recommend:
- Code-specialized models like CodeLlama, Deepseek Coder, or WizardCoder
- Using a temperature of 0.1-0.3
- Models with at least 7B parameters for more accurate conversions

You can specify your LLM settings via environment variables or command-line parameters.

#### Tips for Better Results

1. For natural language to command conversions, be as specific as possible
2. Try different temperature values - lower (0.1) for exact command conversions, slightly higher (0.3-0.5) for descriptive conversions
3. Adjust the max_tokens parameter if you need longer explanations
4. Code-specialized LLMs tend to perform better for this task
