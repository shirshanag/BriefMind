from fastapi import FastAPI, HTTPException,Form
from fastapi.staticfiles import StaticFiles #handles all the static files
from fastapi.responses import FileResponse 
import requests # send requests to backend
import os # Interact with the operation system
import json # Handles json file 
#FastAPI creates backend application
#HTTpException catch any exception
#Form is to create any form that can send request to backend
app= FastAPI()
#Serve static files (HTML,css,js)
app.mount("/static",StaticFiles(directory="static"),name="static")
OLLAMA_URL="http://localhost:11434/api/generate"
MODEL_NAME="mistral"

@app.get("/")
def serve_homepage():
    """ Serves the index.html when accessing the root url """
    return FileResponse(os.path.join("static","index.html"))
@app.post("/summarize")
def summarize_text(text: str=Form(...)):
    headers={"Content-Type":'application/json'}
    try:
        response=requests.post (
            OLLAMA_URL,
            json={"model":MODEL_NAME,"prompt":f"Summarize this:{text}","stream":False},
            headers=headers
        )
        #Log the response for debugging

        print("Ollama Response:",response.text)

        #Ensure valid json response

        response_data=response.text.strip()
        try:
            json_response=json.loads(response_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500,detail=f"Invalid json response from ollama {response_data}")
        #Extract summarised text
        summarized_text=json_response.get("response","No valid summary recieved")
        return {"summary":summarized_text}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Requests to ollama failed:{str(e)}")
if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="0.0.0.0",port=8000 ,reload=True)