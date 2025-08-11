# E2B API Key Setup Instructions

To use the sandbox functionality in this application, you need to set up an E2B API key. Follow these steps:

## Step 1: Get Your E2B API Key

1. Go to [https://e2b.dev/dashboard](https://e2b.dev/dashboard)
2. Sign up for an account or log in if you already have one
3. Navigate to the "Team" tab
4. Copy your API key

## Step 2: Set Your API Key

You can set your API key in two ways:

### Option 1: Update the .env file (Recommended)

Open the `.env` file in the project root and replace `your-e2b-api-key-here` with your actual API key:

```
E2B_API_KEY="your-actual-api-key-here"
```

### Option 2: Set as Environment Variable

Set the API key as an environment variable in your system:

**On Windows (Command Prompt):**
```cmd
set E2B_API_KEY=your-actual-api-key-here
```

**On Windows (PowerShell):**
```powershell
$env:E2B_API_KEY="your-actual-api-key-here"
```

**On macOS/Linux:**
```bash
export E2B_API_KEY=your-actual-api-key-here
```

## Step 3: Verify Setup

After setting your API key, you can test the application:

```bash
uv run run_app.py
```

The application should now be able to use the E2B sandbox for code execution and testing.

## Troubleshooting

If you encounter any issues:

1. Make sure your API key is correct and active
2. Check that you have internet connectivity
3. Verify that the E2B service is working by checking their status page
4. Ensure you haven't exceeded your API usage limits

For more information, visit the [E2B documentation](https://docs.e2b.dev/).