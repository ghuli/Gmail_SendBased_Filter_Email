# Gmail Sender-Based Filter

This project automatically filters and labels Gmail messages based on sender email addresses using the Gmail API.

## Features
- Authenticate with Gmail using OAuth2
- Create or get labels automatically
- Search and filter emails by sender
- Apply labels and remove from INBOX in batches
- Progress bars for bulk operations

## Requirements
- Python 3.7+
- Gmail API credentials (`token.json`)

## Setup
1. Clone the repository.
2. Create a virtual environment and activate it:
   ```sh
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up Gmail API credentials and place your `token.json` in the project root.

## Usage
Run the main script:
```sh
python src/Gmail_SenderBased_Filter.py
```

## Testing
Run all unit tests:
```sh
python -m unittest discover -s tests
```

## Project Structure
- `src/` — Main source code
- `tests/` — Unit tests

## License
MIT
