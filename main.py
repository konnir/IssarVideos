from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from typing import List
from fastapi.encoders import jsonable_encoder

from data.video_info import VideoInfo



app = FastAPI()

@app.get("/options")
async def get_options():
    return JSONResponse(content={"options": ["option1", "option2", "option3"]})

@app.get("/topics")
async def get_topics():
    return JSONResponse(content={"topics": ["topic1", "topic2", "topic3"]})

@app.get("/narratives")
async def get_narratives(topic: str):
    narratives_by_topic = {
        "topic1": ["narrative1a", "narrative1b"],
        "topic2": ["narrative2a", "narrative2b"],
        "topic3": ["narrative3a", "narrative3b"],
    }
    return JSONResponse(content={"narratives": narratives_by_topic.get(topic, [])})

# Example video_info_list; replace with your actual data source
video_info_list: List[VideoInfo] = []
@app.get("/videos")
async def get_videos(narrative: str):
    filtered_videos = [v for v in video_info_list if v.narrative == narrative]
    return JSONResponse(content=jsonable_encoder(filtered_videos))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)