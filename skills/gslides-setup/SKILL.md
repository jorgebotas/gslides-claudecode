---
name: gslides-setup
description: Guide users through setting up Google Slides API access with service accounts for Claude Code projects. Use when users want to connect to Google Slides, set up slide automation, create service accounts, or troubleshoot Google API authentication issues.
---

# Google Slides Setup Guide

Walks users through the complete setup process for integrating Google Slides API with Claude Code projects using service accounts.

## When to use this skill

Trigger this skill when users mention:
- Setting up Google Slides integration
- Creating service accounts for Slides
- Authentication errors with Google APIs
- "Connect to Google Slides"
- "Set up slide automation"
- Troubleshooting 403 errors or quota issues

## Setup Process

**Before starting step 3**, ask the user which Python installer they use (options: `uv`, `pip`, `conda`/`mamba`, `poetry`, `pipx`). Remember the answer and use it for every install/venv command throughout the walkthrough. If they don't know, default to `pip`.

### 1. Create GCP Project and Enable APIs

Guide the user to:

1. **Create a Google Cloud Project** (if they don't have one):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click "Select a project" → "New Project"
   - Enter a project name and click "Create"

2. **Enable required APIs**:
   - Navigate to `https://console.cloud.google.com/apis/library/slides.googleapis.com?project=PROJECT_ID` (replace PROJECT_ID)
   - Click "Enable" for Google Slides API
   - Navigate to `https://console.cloud.google.com/apis/library/drive.googleapis.com?project=PROJECT_ID`
   - Click "Enable" for Google Drive API

### 2. Create Service Account

1. **Go to Service Accounts**:
   - Navigate to `https://console.cloud.google.com/iam-admin/serviceaccounts?project=PROJECT_ID`
   - Click "Create Service Account"

2. **Configure the account**:
   - Enter a name (e.g., "slides-automation")
   - Add description: "Service account for Google Slides API access"
   - Click "Create and Continue"
   - Skip role assignment (not needed for this use case)
   - Click "Done"

3. **Generate JSON key**:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Select "JSON" and click "Create"
   - The key file downloads automatically - **save it securely**

### 3. Install gslides-claudecode

Use the command that matches the user's chosen installer:

| Installer | Command |
|-----------|---------|
| `uv` | `uv pip install gslides-claudecode` (or `uv add gslides-claudecode` inside a uv-managed project) |
| `pip` | `pip install gslides-claudecode` |
| `conda` / `mamba` | `pip install gslides-claudecode` (inside the active conda env — the package isn't on conda-forge yet) |
| `poetry` | `poetry add gslides-claudecode` |
| `pipx` | `pipx install gslides-claudecode` (isolates the `gslides` CLI globally) |

If the user hasn't created an environment yet, suggest one using their chosen tool before installing:

| Installer | Env command |
|-----------|-------------|
| `uv` | `uv venv && source .venv/bin/activate` |
| `pip` | `python -m venv .venv && source .venv/bin/activate` |
| `conda` | `conda create -n gslides python=3.11 && conda activate gslides` |
| `poetry` | `poetry init` (if not already in a project) |

### 4. Set up credentials

1. **Place the key file**:
   - Save the downloaded JSON as `service_account.json` in your project directory
   - Or set `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the file path

2. **Verify installation**:
   ```bash
   gslides --help
   ```

### 5. Create and share a presentation

**IMPORTANT**: Service accounts cannot create files in Google Drive due to quota limitations. You must:

1. **Create a presentation** in your personal Google Drive
2. **Share it with the service account**:
   - Open the presentation in Google Slides
   - Click "Share" button
   - Enter the service account email (found in the JSON key file, looks like `name@project-id.iam.gserviceaccount.com`)
   - Set permission to "Editor"
   - Click "Send"

### 6. Test the connection

```bash
gslides test <presentation_id>
```

The presentation ID is found in the URL: `https://docs.google.com/presentation/d/PRESENTATION_ID/edit`

## Expected output on success

```
✓ Connected successfully!
Title: My Presentation
Slides: 1
Presentation ID: 1AbCdEfGhIjKlMnOpQrStUvWxYz
```

## Troubleshooting

### 403 Forbidden errors

**Cause**: APIs not enabled or insufficient permissions

**Solutions**:
1. Verify both Slides and Drive APIs are enabled in the GCP Console
2. Check that the presentation is shared with the service account email as Editor
3. Ensure the service account JSON file is valid and accessible

### "storageQuota.limit=0" errors

**Cause**: Attempting to create files with a service account

**Solution**: Service accounts have no Drive storage quota. Always create presentations in your personal Drive first, then share with the service account.

### File not found errors

**Solutions**:
1. Check the `service_account.json` file exists in the expected location
2. Verify `GOOGLE_APPLICATION_CREDENTIALS` environment variable points to the correct file
3. Ensure the JSON file has correct permissions (readable by your user)

### Invalid presentation ID

**Symptoms**: "Requested entity was not found" errors

**Solutions**:
1. Double-check the presentation ID from the URL
2. Verify the presentation is shared with the service account
3. Ensure the presentation wasn't deleted or moved

## Known limitations to mention during setup

Before the user tries `gslides image`, flag these so they aren't surprised:

1. **Service accounts cannot upload local images.** The Drive quota is zero; `image_path=` uploads fail with a clear error. Tell the user to either host images publicly (GitHub raw with a commit-pinned URL works well — use `/<sha>/image.png`, not `/main/image.png`, to defeat Google's image CDN caching) and use `image_url=`, or use a Google Workspace Shared Drive, or switch to OAuth auth.
2. **Images must be ≤ ~2 MB.** The library auto-downscales local images to 1600 px longest edge via Pillow. For `image_url=` sources the user must pre-size.

## Next steps

Once setup is complete, users can:

- Add slides programmatically: `gslides text <id> --title "Title" --body "Content"`
- Generate reports with the `gslides-report` skill
- Use the Python library in their projects: `from gslides_claudecode import Deck`

## Security notes

- Keep service account JSON files secure and never commit them to version control
- Use environment variables (`GOOGLE_APPLICATION_CREDENTIALS`) in production
- Regularly rotate service account keys (recommended: every 90 days)
- Grant minimal necessary permissions (Editor on specific presentations only)