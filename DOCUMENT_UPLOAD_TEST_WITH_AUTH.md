# Document Upload Testing Guide

This guide provides step-by-step instructions to test the document upload functionality with proper authentication.

## Step 1: Get Authentication Token

First, you need to get an authentication token by logging in:

```powershell
# PowerShell
$loginData = @{
    email = "your-email@example.com"
    password = "your-password"
} | ConvertTo-Json

$loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" `
    -Method POST `
    -Body $loginData `
    -ContentType "application/json"

$token = ($loginResponse.Content | ConvertFrom-Json).access_token
```

## Step 2: Test Document Upload

Now use the token to upload a document:

```powershell
# PowerShell - More reliable approach with detailed debugging
$token = "YOUR_TOKEN_HERE"  # Replace with your actual token

# Create a temporary test file if you don't have one
$testFilePath = "$env:TEMP\test_document.txt"
Set-Content -Path $testFilePath -Value "This is a test document content."

# Define the upload URL
$uploadUrl = "http://localhost:8000/api/documents/project/1/upload"

# Define boundary for multipart form
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

# Build the multipart form data manually
$bodyLines = @()
$bodyLines += "--$boundary$LF"
$bodyLines += "Content-Disposition: form-data; name=`"file`"; filename=`"test_document.txt`"$LF"
$bodyLines += "Content-Type: text/plain$LF$LF"
$bodyLines += [System.IO.File]::ReadAllText($testFilePath)
$bodyLines += "$LF--$boundary$LF"
$bodyLines += "Content-Disposition: form-data; name=`"name`"$LF$LF"
$bodyLines += "Test Document$LF"
$bodyLines += "--$boundary$LF"
$bodyLines += "Content-Disposition: form-data; name=`"description`"$LF$LF"
$bodyLines += "This is a test document$LF"
$bodyLines += "--$boundary--$LF"

$body = [System.String]::Join("", $bodyLines)

# Set up headers
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "multipart/form-data; boundary=$boundary"
}

# Make the request with verbose output
try {
    Write-Host "Sending request to: $uploadUrl"
    Write-Host "Headers: $($headers | ConvertTo-Json)"

    $response = Invoke-WebRequest -Uri $uploadUrl -Method POST -Headers $headers -Body $body -ErrorAction Stop
    Write-Host "Success! Status code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
}
catch {
    Write-Host "Error occurred: $_"
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"

    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response body: $responseBody"
        $reader.Close()
    }
}

# Clean up
Remove-Item -Path $testFilePath -Force
```

**Alternative using curl in PowerShell:**

```powershell
# Using curl.exe (if available through Git for Windows)
$token = "YOUR_TOKEN_HERE"  # Replace with actual token
$testFilePath = "$env:TEMP\test_document.txt"
Set-Content -Path $testFilePath -Value "This is a test document content."

# Execute curl command (assumes curl.exe is in PATH)
$curlCommand = @"
curl.exe -v -X POST "http://localhost:8000/api/documents/project/1/upload" -H "Authorization: Bearer $token" -F "file=@$testFilePath" -F "name=Test Document" -F "description=Test upload"
"@

Write-Host "Executing: $curlCommand"
Invoke-Expression $curlCommand

# Clean up
Remove-Item -Path $testFilePath -Force
```

## Alternative Using curl (if available)

If you have curl installed (for example via Git Bash), you can use this command:

```bash
curl -X POST "http://localhost:8000/api/documents/project/1/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "name=Sample Document" \
  -F "description=Test document upload"
```

## Debugging Tips

If you're still getting 404 errors:

1. **Check that your backend is running**: Make sure the FastAPI server is running on port 8000.

2. **Verify correct URL path**: Ensure you're using the exact path `/api/documents/project/1/upload`.

3. **Check authentication**: Ensure your token is valid and properly formatted in the Authorization header.

4. **Examine logs**: Look at the backend server logs for more detailed error information.

5. **URL encoding**: Ensure there are no encoding issues with the URL.

6. **Project existence**: Confirm that a project with ID 1 actually exists in your database.

7. **Router registration**: Make sure the documents router is properly registered in main.py:

   ```python
   from app.api.documents_supabase import router as documents_supabase_router
   app.include_router(documents_supabase_router, prefix="/api/documents", tags=["documents"])
   ```

8. **Verify API routes**: We've already confirmed that the endpoint `/api/documents/project/{project_id}/upload` exists in the API.

9. **Check project ID**: Make sure you have at least one project in your database. Try listing all projects:

   ```powershell
   $token = "YOUR_TOKEN_HERE"  # Replace with your actual token
   Invoke-WebRequest -Uri "http://localhost:8000/api/projects" -Method GET -Headers @{"Authorization" = "Bearer $token"}
   ```

10. **Inspect server logs**: Look at the debug logs from the server while making the request to see exactly what's happening:
    ```powershell
    # Run the server with debug logs
    cd backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
    ```
