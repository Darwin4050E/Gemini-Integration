from fastapi import FastAPI, BackgroundTasks
import uvicorn
from main import main

app = FastAPI()

def task():
    main()

@app.post("/notion-trigger")
async def webhook_receiver(background_tasks: BackgroundTasks):
    
    background_tasks.add_task(task)
    
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)