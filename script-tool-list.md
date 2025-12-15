deepresearch v0.13.1
- deep-research
gen-music v0.2.4
- gen-music
gen-tts v0.1.12
- gen-tts
generate-gemini-image v0.1.12
- generate-gemini-image
generate-gemini-voice v0.1.12
- generate-voice
generate-veo-video v0.2.5
- generate-veo
tax-commander v1.1.0
- tax-commander
usage: deep-research [-h] [-v]
                     {research,start,followup,list,show,delete,cleanup,tree,auth,estimate}
                     ...

Gemini Deep Research Agent CLI
==============================
A powerful tool to conduct autonomous, multi-step research using Gemini 3 Pro.
Support web search, local file ingestion, streaming thoughts, and follow-ups.
    

positional arguments:
  {research,start,followup,list,show,delete,cleanup,tree,auth,estimate}
                        Command to run
    research            Start a new research task
    start               Start a research task in the background (Headless)
    followup            Ask a follow-up question to a previous session
    list                List recent research sessions
    show                Show details of a previous session
    delete              Delete a session from history
    cleanup             Delete stale cloud resources (GC)
    tree                Visualize session hierarchy
    auth                Manage authentication
    estimate            Estimate cost of a research task

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

Examples:
---------
1. Basic Web Research (Streaming):
   deep-research research "History of the internet" --stream

2. Research with Local Files (Smart Context):
   deep-research research "Summarize this contract" --upload ./contract.pdf --stream

3. Formatted Output & Export:
   deep-research research "Compare GPU prices" --format "Markdown table" --output prices.md
   deep-research research "List top 5 cloud providers" --output market_data.json

4. Headless Research (Fire & Forget):
   deep-research start "Detailed analysis of quantum computing"
   # ... process detaches ...
   deep-research list
   deep-research show 1

5. Follow-up Question:
   deep-research followup 1 "Can you explain the error correction?"

6. Manage History:
   deep-research list
   deep-research show 1

Configuration:
--------------
Set GEMINI_API_KEY in a local .env file or at ~/.config/deepresearch/.env
    
usage: gen-music [-h] [-o OUTPUT] [-d DURATION] [--bpm BPM] [-p] [--history]
                 [--rerun RERUN] [--init] [-f {wav,mp3}] [-b] [--optimize]
                 [--temp] [--live]
                 [prompt]

Generate music using Google's Vertex AI Lyria model.

positional arguments:
  prompt                The text prompt for the music.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output filename.
  -d DURATION, --duration DURATION
                        Duration in seconds.
  --bpm BPM             Beats per minute.
  -p, --play            Play immediately after generation.
  --history             Show command history.
  --rerun RERUN         Rerun a history item by ID.
  --init                Initialize configuration in ~/.config/gen-music/
  -f {wav,mp3}, --format {wav,mp3}
                        Output format.
  -b, --background      Run in background.
  --optimize            Use Gemini to optimize the prompt.
  --temp                Generate a temporary file, play it, and delete it.
  --live                Start an interactive live DJ session.
usage: gen-tts [-h] [--input-file FILE] [--detailed-prompt-file FILE]
               [--generate-transcript TOPIC] [--podcast] [--summary]
               [--transcript-model TRANSCRIPT_MODEL] [--output-file FILE]
               [--audio-format {WAV,MP3}] [--temp] [--no-play] [--model MODEL]
               [--list-voices] [--voice-name NAME] [--multi-speaker]
               [--speaker-voices SPEAKER=VOICE_NAME [SPEAKER=VOICE_NAME ...]]
               [--project-id ID]
               [text]

Generate high-quality speech from text using Google Gemini's native Text-to-Speech (TTS) capabilities, including single and multi-speaker options.

options:
  -h, --help            show this help message and exit

Input Options (provide one of text, --input-file, --generate-transcript or piped data):
  text                  The text to synthesize. Optional if using --input-
                        file, --generate-transcript, or piping text via stdin.
  --input-file FILE     Read the text to synthesize from a specific file path.
  --detailed-prompt-file FILE
                        Path to a Markdown file containing a detailed prompt
                        (Audio Profile, Scene, Director's Notes) for advanced
                        TTS control.

Content Generation Options:
  --generate-transcript TOPIC
                        Generate a script for the TTS based on a topic using
                        Gemini.
  --podcast             Convert input into a multi-speaker podcast script.
                        Defaults to Host/Guest speakers and MP3 format.
  --summary             Convert input into a concise, info-packed summary
                        script. Defaults to 'Sulafat' (Warm) voice and MP3
                        format.
  --transcript-model TRANSCRIPT_MODEL
                        The model to use for generating the
                        transcript/podcast/summary. Default: 'gemini-2.5-pro'.

Output Options:
  --output-file FILE    Save the generated audio to this file. If omitted, a
                        filename is automatically generated based on the text
                        and timestamp. Ignored if --temp is used.
  --audio-format {WAV,MP3}
                        The audio file format. 'WAV' (default) is uncompressed
                        linear PCM. 'MP3' is widely compatible.
  --temp                Generate the audio to a temporary file, play it
                        immediately, and then delete it. Useful for quick
                        previews.
  --no-play             Disable automatic playback of the generated audio
                        file. Default behavior is to play after generation.

Voice Configuration:
  --model MODEL         The Gemini TTS model to use. Default:
                        'gemini-2.5-flash-preview-tts'. Other options include
                        'gemini-2.5-pro-preview-tts'.
  --list-voices         List all available Gemini TTS voices and exit.
  --voice-name NAME     The specific Gemini TTS voice name to use for single-
                        speaker mode. Default: 'Charon'. Use --list-voices to
                        see all available options.
  --multi-speaker       Enable multi-speaker mode. Requires --speaker-voices.
  --speaker-voices SPEAKER=VOICE_NAME [SPEAKER=VOICE_NAME ...]
                        Define speaker names and their corresponding voice
                        names for multi-speaker mode. Example: 'Joe=Charon
                        Jane=Puck'. Requires --multi-speaker.

Project Configuration:
  --project-id ID       The Google Cloud Project ID to bill for usage.
                        Defaults to the 'GCLOUD_PROJECT' environment variable
                        or 'ucr-research-computing'. (Note: API key is also
                        used for auth)

EXAMPLES:

  1. Generate and play a simple sentence (Preview mode - single speaker):
     gen-tts "Hello, world! This is a test." --temp --voice-name Kore

  2. Create a podcast from a text file (Deep Dive style):
     gen-tts --input-file article.txt --podcast

  3. Create a concise summary of a text file (Warm voice, info-packed):
     gen-tts --input-file report.txt --summary

  4. Pipe text to create a summary:
     cat emails.txt | gen-tts --summary

  5. Save multi-speaker speech to a specific MP3 file:
     gen-tts "Joe: How's it going today Jane?
Jane: Not too bad, how about you?"              --multi-speaker --speaker-voices Joe=Kore Jane=Puck              --output-file conversation.mp3
             
  6. Generate a script and audio from a topic:
     gen-tts --generate-transcript "A funny debate about pineapple on pizza"              --multi-speaker --speaker-voices Mario=Kore Luigi=Puck              --output-file pizza_debate.wav
                                                                                                                                                                                                                   
 Usage: generate-gemini-image [OPTIONS] COMMAND [ARGS]...                                                                                                                                                          
                                                                                                                                                                                                                   
 Modernized Gemini Image Generation CLI                                                                                                                                                                            
                                                                                                                                                                                                                   
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --prompt              -p      TEXT                  The text prompt to generate an image from. Required unless piping stdin.                                                                                    │
│ --image               -i      PATH                  Reference image(s) for editing/composition. Can be specified multiple times.                                                                                │
│ --count               -n      INTEGER RANGE [x>=1]  Number of images to generate (Nano Banana strict). [default: 1]                                                                                             │
│ --style                       TEXT                  Artistic styles to apply. Examples: 'Cyberpunk', 'Watercolor', 'Oil Painting', 'Photorealistic', 'Anime', 'Sketch', 'Vintage'.                              │
│ --variation                   TEXT                  Visual variations to apply. Examples: 'Cinematic Lighting', 'Moody', 'Golden Hour', 'Minimalist', 'High Contrast', 'Pastel Colors'.                         │
│ --output-dir          -o      PATH                  Directory to save output. Defaults to ~/Pictures/Gemini_Generated.                                                                                          │
│ --filename            -f      TEXT                  Specific filename for output image (e.g., 'result.png').                                                                                                    │
│ --api-key                     TEXT                  Google AI Studio API Key (overrides env).                                                                                                                   │
│ --project-id                  TEXT                  GCP Project ID (overrides env).                                                                                                                             │
│ --location                    TEXT                  GCP Location (default: us-central1).                                                                                                                        │
│ --model-name                  TEXT                  Vertex AI Model (default: gemini-3-pro-image-preview).                                                                                                      │
│ --aspect-ratio                TEXT                  Aspect ratio. Options: '1:1', '16:9', '9:16', '4:3', '3:4'.                                                                                                 │
│ --image-size                  TEXT                  Image resolution. Options: '1K', '2K', '4K'.                                                                                                                │
│ --negative-prompt             TEXT                  Items to exclude from the image (e.g., 'blur, distortion, people').                                                                                         │
│ --seed                        INTEGER               Random seed for reproducible results (if supported by model).                                                                                               │
│ --verbose             -v                            Enable verbose logging.                                                                                                                                     │
│ --install-completion                                Install completion for the current shell.                                                                                                                   │
│ --show-completion                                   Show completion for the current shell, to copy it or customize the installation.                                                                            │
│ --help                -h                            Show this message and exit.                                                                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ init   Initialize the application configuration. Creates a secure .env file in ~/.config/generate-gemini-image/                                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

usage: generate-veo [-h] [--output-file OUTPUT_FILE] [--duration {4,6,8}]
                    [--aspect-ratio {16:9,9:16}]
                    [--negative-prompt NEGATIVE_PROMPT] [--image IMAGE]
                    [--last-frame LAST_FRAME]
                    [--ref-images REF_IMAGES [REF_IMAGES ...]] [--video VIDEO]
                    [--no-audio] [--seed SEED] [--history] [--rerun RERUN]
                    [prompt]

Generate a video using the Vertex AI VEO 3.1 model.

positional arguments:
  prompt                The text prompt for the video.

options:
  -h, --help            show this help message and exit
  --output-file OUTPUT_FILE, -o OUTPUT_FILE
                        Output filename.
  --duration {4,6,8}    Duration (4, 6, 8). Default 8.
  --aspect-ratio {16:9,9:16}
                        Aspect ratio.
  --negative-prompt NEGATIVE_PROMPT
                        Negative prompt.
  --image IMAGE         Initial image path for Image-to-Video.
  --last-frame LAST_FRAME
                        Last frame image path (requires --image).
  --ref-images REF_IMAGES [REF_IMAGES ...]
                        Path(s) to reference images (max 3).
  --video VIDEO         Path to input video for extension (must be Veo-
                        generated).
  --no-audio            Ignored (Veo 3.1 always generates audio).
  --seed SEED           Seed for random number generation (optional).
  --history             Display prompt history.
  --rerun RERUN         Rerun a prompt from history by number.

Examples:
---------
1. Text-to-Video:
   generate-veo "A cinematic drone shot of a futuristic city at night, neon lights, rain."
   generate-veo "A cute robot gardening in a sunlit greenhouse." --duration 4

2. Image-to-Video (Animation):
   generate-veo "Make the waves move and the clouds drift." --image ./ocean.png
   generate-veo "The character turns their head and smiles." --image ./portrait.jpg

3. Style Transfer (Reference Images):
   generate-veo "A fashion model walking on a runway." --ref-images ./style_dress.png ./style_glasses.png
   generate-veo "A cyberpunk street scene." --ref-images ./blade_runner_ref.jpg

4. Morphing (First & Last Frame):
   generate-veo "Morph this sketch into a photorealistic drawing." --image ./sketch.png --last-frame ./final.png
   generate-veo "A car transforming into a robot." --image ./car.png --last-frame ./robot.png

5. Video Extension:
   generate-veo "The drone continues flying over the mountains." --video ./previous_veo_clip.mp4
   generate-veo "The character walks out of the frame." --video ./generated_clip.mp4
    
