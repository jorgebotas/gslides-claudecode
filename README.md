# gslides-claudecode

A Python library and CLI for programmatically creating Google Slides presentations from Claude Code projects. Uses service account authentication to append slides to user-owned presentations — no OAuth flows, browser authentication, or user interaction required.

## Why gslides-claudecode?

This package solves the automation gap for Google Slides:
- **Service account only**: No OAuth, no browser flows, works in headless environments
- **Append workflow**: Works with existing presentations you create and share
- **Claude Code integration**: Built-in skills and agents for seamless AI-assisted slide generation
- **Multiple content types**: Text, bullets, images (local files or URLs), tables from CSV data
- **Speaker notes**: Add context and talking points to every slide

Perfect for automated reporting, progress dashboards, and transforming analysis outputs into stakeholder-ready presentations.

## Prerequisites

- **Python 3.8+**
- **Google Cloud Project** with Slides and Drive APIs enabled
- **uv** (recommended) or **pip** for installation

## Setup Guide

### 1. Create Google Cloud Project and Enable APIs

1. **Create a project** (or use existing):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "Select a project" → "New Project" 
   - Enter project name and click "Create"
   - Note your `PROJECT_ID` for the next steps

2. **Enable Google Slides API**:
   - Navigate to: `https://console.cloud.google.com/apis/library/slides.googleapis.com?project=<YOUR_PROJECT_ID>`
   - Click "Enable"

3. **Enable Google Drive API**:
   - Navigate to: `https://console.cloud.google.com/apis/library/drive.googleapis.com?project=<YOUR_PROJECT_ID>`
   - Click "Enable"

### 2. Create Service Account

1. **Go to Service Accounts**:
   - Navigate to: `https://console.cloud.google.com/iam-admin/serviceaccounts?project=<YOUR_PROJECT_ID>`
   - Click "Create Service Account"

2. **Configure the account**:
   - Service account name: `slides-automation` (or your preferred name)
   - Description: `Service account for Google Slides API access`
   - Click "Create and Continue"
   - Skip role assignment (not needed) and click "Done"

3. **Generate and download JSON key**:
   - Click on your new service account
   - Go to "Keys" tab → "Add Key" → "Create new key"
   - Select "JSON" format and click "Create"
   - **Save the downloaded file as `service_account.json` in your project directory**

### 3. Install Package

```bash
# Recommended: using uv
uv pip install -e .

# Alternative: using pip
pip install -e .
```

### 4. Create and Share Presentation

**⚠️ Important**: Service accounts have **zero Google Drive storage quota** and cannot create or own files. You must create presentations in your personal Google Drive first, then share them.

1. **Create a presentation**:
   - Go to [Google Slides](https://slides.google.com)
   - Create a new presentation
   - Copy the presentation ID from the URL: `https://docs.google.com/presentation/d/{PRESENTATION_ID}/edit`

2. **Share with service account**:
   - Click "Share" in the top-right
   - Enter the service account email (found in your `service_account.json` file, looks like `slides-automation@your-project-id.iam.gserviceaccount.com`)
   - Set permission to **"Editor"**
   - Click "Send"

### 5. Verify Setup

```bash
# Test the connection
gslides test {PRESENTATION_ID}
```

Expected success output:
```
✓ Connected successfully!
Title: My Presentation
Slides: 1
Presentation ID: 1AbCdEfGhIjKlMnOpQrStUvWxYz
```

## Usage

### Command Line Interface

The `gslides` CLI provides five commands for different slide types:

```bash
# Test API connection
gslides test {presentation_id}

# Add text slide
gslides text {presentation_id} \
  --title "Project Results" \
  --body "Our analysis shows a 15% improvement in accuracy over the baseline model." \
  --notes "Emphasize the business impact of this improvement"

# Add bulleted list
gslides bullets {presentation_id} \
  --title "Key Achievements" \
  --bullets "Completed model training,Achieved 94% accuracy,Reduced inference time by 30%" \
  --notes "These milestones unlock the next phase of development"

# Add image slide (from public URL)
gslides image {presentation_id} \
  --title "Performance Trends" \
  --url "https://example.com/chart.png" \
  --notes "Chart shows consistent improvement over 6-month period"

# Add image slide (from local file - uploads to Drive automatically)
gslides image {presentation_id} \
  --title "Architecture Diagram" \
  --path "diagrams/model_architecture.png" \
  --notes "New architecture reduces complexity while improving performance"

# Add table from CSV file
gslides table {presentation_id} \
  --title "Model Comparison" \
  --csv "results/benchmark.csv" \
  --notes "Highlighted model shows best balance of accuracy and speed"
```

### Python Library

```python
from gslides_claudecode import Deck

# Initialize with service account
deck = Deck.from_service_account(
    key_file="service_account.json",  # or None to use env var
    presentation_id="your_presentation_id"
)

# Add different slide types
slide_id = deck.append_text(
    title="Executive Summary",
    body="Q3 results exceed targets with 15% revenue growth and 94% customer satisfaction.",
    speaker_notes="Focus on the growth trajectory and customer feedback themes"
)

slide_id = deck.append_bullets(
    title="Technical Achievements",
    bullets=[
        "Model accuracy improved to 94.2%",
        "Inference latency reduced by 30%", 
        "Memory usage optimized (-25%)"
    ],
    speaker_notes="These improvements enable real-time applications"
)

slide_id = deck.append_image(
    title="Training Progress",
    image_path="outputs/training_curve.png",  # Local file - auto-uploads to Drive
    speaker_notes="Convergence achieved at epoch 15 with stable validation loss"
)

slide_id = deck.append_table(
    title="Benchmark Results", 
    rows=[
        ["Model", "Accuracy", "Latency", "Memory"],
        ["Baseline", "87.1%", "120ms", "2.1GB"],
        ["Optimized", "94.2%", "85ms", "1.6GB"]
    ],
    speaker_notes="Optimized model wins across all key metrics"
)

# Get presentation info
info = deck.info()
print(f"'{info['title']}' now has {info['slide_count']} slides")
```

### Authentication Options

Credentials are loaded in this priority order:

1. **Explicit file path**: `--key-file path/to/service_account.json`
2. **Environment variable**: `GOOGLE_APPLICATION_CREDENTIALS=path/to/service_account.json`  
3. **Default location**: `./service_account.json` in current directory

```bash
# Method 1: Command-line argument
gslides --key-file /secure/path/service_account.json test {presentation_id}

# Method 2: Environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/secure/path/service_account.json"
gslides test {presentation_id}

# Method 3: Default location
cp /secure/path/service_account.json ./service_account.json
gslides test {presentation_id}
```

## Troubleshooting

### 403 Permission Errors

**Error**: `HttpError 403 "The caller does not have permission"`

**Causes and solutions**:
- **APIs not enabled**: Verify both Google Slides API and Google Drive API are enabled in your GCP project
- **Presentation not shared**: Ensure the presentation is shared with your service account email as "Editor"
- **Wrong project**: Check that your service account belongs to the project where APIs are enabled

### Storage Quota Errors  

**Error**: `storageQuota.limit = '0'` or similar quota-related failures

**Explanation**: Service accounts have zero Google Drive storage quota by design. They cannot create, own, or store files.

**Solution**: Always create presentations in your personal Google Drive first, then share them with the service account. Never attempt to create presentations programmatically with service accounts.

### Image Upload Issues

**Local files**: Images uploaded via `image_path` parameter are automatically uploaded to Google Drive and made publicly readable. This requires:
- Google Drive API enabled on your project
- Service account has Drive API access (included in required scopes)

**Public URLs**: Images via `image_url` parameter must be publicly accessible. Google Slides cannot access:
- Local file paths (like `file:///Users/...`)
- URLs requiring authentication
- Private cloud storage URLs

**Supported formats**: PNG, JPEG, GIF. Other formats may not render correctly.

### File Not Found

**Error**: `FileNotFoundError: Service account key file not found`

**Solutions**:
- Verify the path to `service_account.json` is correct
- Check file permissions (must be readable by your user)
- Ensure the file wasn't accidentally moved or deleted
- Try specifying the full absolute path

### Invalid Presentation ID

**Error**: `HttpError 404 "Requested entity was not found"`

**Solutions**:
- Double-check the presentation ID from the Google Slides URL
- Verify the presentation exists and wasn't deleted
- Confirm the presentation is shared with your service account
- Ensure you're using the presentation ID, not the sharing URL

## Claude Code Integration

This repo doubles as a **Claude Code plugin** that bundles two skills and one agent:

- **gslides-setup** (skill) — walks you through GCP project creation, API enablement, service account + key download, sharing a deck, and verifying the connection. Asks which installer you use (`uv`, `pip`, `conda`, `poetry`, `pipx`) and tailors the commands accordingly.
- **gslides-report** (skill) — generates progress/result slide decks from figures and project context.
- **gslides-builder** (agent) — dedicated agent for all slide operations in a project.

### Install as a plugin

From any Claude Code session:

```
/plugin marketplace add jorgebotas/gslides-claudecode
/plugin install gslides-claudecode@gslides-claudecode
```

This makes the skills and agent discoverable. The Python package (`gslides-claudecode`) is **not** installed automatically — the `gslides-setup` skill will prompt for your preferred installer and give you the right command when you trigger it.

### Trigger the setup skill

After installing the plugin, in Claude Code:

```
> help me set up google slides
```

The `gslides-setup` skill activates and walks you through everything, including the `pip`/`uv`/`conda`/`poetry`/`pipx` install step.

### Manual install (without the plugin system)

If you'd rather drop the assets into `~/.claude/` by hand:

```bash
git clone https://github.com/jorgebotas/gslides-claudecode
cp -r gslides-claudecode/skills/* ~/.claude/skills/
cp gslides-claudecode/agents/gslides-builder.md ~/.claude/agents/
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

This is an open-source project. Contributions welcome via GitHub issues and pull requests.