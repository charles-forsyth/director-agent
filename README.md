# Director Agent

An autonomous movie studio agent that orchestrates Gemini, Veo, TTS, and Music generation tools to create short documentaries from a single topic.

## Features

*   **Autonomous Planning**: Uses Gemini Pro to research a topic and create a shot-by-shot production manifest.
*   **Multi-Modal Generation**: Orchestrates video (Veo), images (Imagen 3), audio (Gemini TTS), and music (Lyria).
*   **Automatic Editing**: Assembles all assets into a final MP4 movie using FFmpeg.
*   **Secure**: Built with strict security practices, using Pydantic for validation and secret management.

## Installation

Install globally using `uv`:

```bash
uv tool install git+https://github.com/charles-forsyth/director-agent.git
```

## Configuration

The agent requires a Google Gemini API key. You can set this via an environment variable or a configuration file.

1.  **Environment Variable:**
    ```bash
    export GEMINI_API_KEY="your_api_key"
    ```

2.  **Config File:**
    Create a file at `~/.config/director-agent/.env`:
    ```env
    GEMINI_API_KEY=your_api_key_here
    # Optional overrides
    # OUTPUT_DIR=~/Movies
    ```

## Usage

```bash
director "The History of Quantum Computing"
```

## Development

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    uv sync
    ```
3.  Run the CLI:
    ```bash
    uv run director "Test Topic"
    ```
