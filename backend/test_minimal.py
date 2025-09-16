from fastapi import FastAPI

# Minimal test app to check if core FastAPI works
app = FastAPI(
    title="Test API",
    version="1.0.0",
    description="Test FastAPI app"
)

@app.get("/")
async def root():
    return {"message": "Test API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
