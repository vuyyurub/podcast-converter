from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import boto3
from newspaper import Article
from nltk.tokenize import sent_tokenize
import nltk
import uuid
import os
from pydub import AudioSegment 

nltk.download("punkt")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

s3_bucket = "bvuyyuru-polly-bucket"

class ArticleRequest(BaseModel):
    url: str

def split_text(text, max_chars=3000):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

@app.post("/api/generate")
def generate_podcast(data: ArticleRequest):
    url = data.url

    try:
        article = Article(url)
        article.download()
        article.parse()
    except Exception as e:
        return {"error": f"Failed to download or parse article: {e}"}

    text = article.text
    title = article.title or f"article-{uuid.uuid4()}"
    base_filename = f"{title[:50].replace(' ', '_')}"
    chunks = split_text(text)

    s3 = boto3.client("s3")
    polly = boto3.client("polly")

    audio_segments = []
    temp_filenames = []
    for i, chunk in enumerate(chunks):
        filename = f"{base_filename}_part{i + 1}.mp3"

        try:
            response = polly.synthesize_speech(
                Text=chunk,
                OutputFormat="mp3",
                VoiceId="Joanna",
            )

            with open(filename, "wb") as f:
                f.write(response["AudioStream"].read())

            temp_filenames.append(filename)
            audio_segments.append(AudioSegment.from_mp3(filename))

        except Exception as e:
            for f in temp_filenames:
                if os.path.exists(f):
                    os.remove(f)
            return {"error": f"Error in chunk {i + 1}: {e}"}
    full_audio = audio_segments[0]
    for seg in audio_segments[1:]:
        full_audio += seg

    merged_filename = f"{base_filename}_full.mp3"
    full_audio.export(merged_filename, format="mp3")

    try:
        s3.upload_file(merged_filename, s3_bucket, merged_filename)
    except Exception as e:
        for f in temp_filenames:
            if os.path.exists(f):
                os.remove(f)
        if os.path.exists(merged_filename):
            os.remove(merged_filename)
        return {"error": f"Failed to upload merged file to S3: {e}"}

    for f in temp_filenames:
        if os.path.exists(f):
            os.remove(f)
    if os.path.exists(merged_filename):
        os.remove(merged_filename)

    merged_url = f"https://{s3_bucket}.s3.amazonaws.com/{merged_filename}"

    return {"audio_url": merged_url}
