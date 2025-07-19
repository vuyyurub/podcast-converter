import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import boto3
from newspaper import Article
from nltk.tokenize import sent_tokenize
import nltk
import uuid
from pydub import AudioSegment
from urllib.request import urlopen
import json

nltk.download("punkt")
s3_bucket = "bvuyyuru-polly-bucket"
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
ALGORITHMS = ["RS256"]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class ArticleRequest(BaseModel):
    url: str


class Auth0Bearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(Auth0Bearer, self).__init__(auto_error=auto_error)

    async def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        if credentials:
            token = credentials.credentials
            try:
                jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
                jwks = json.loads(urlopen(jwks_url).read())
                unverified_header = jwt.get_unverified_header(token)
                rsa_key = {}
                for key in jwks["keys"]:
                    if key["kid"] == unverified_header["kid"]:
                        rsa_key = {
                            "kty": key["kty"],
                            "kid": key["kid"],
                            "use": key["use"],
                            "n": key["n"],
                            "e": key["e"],
                        }
                if rsa_key:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=ALGORITHMS,
                        audience=API_AUDIENCE,
                        issuer=f"https://{AUTH0_DOMAIN}/",
                    )
                    return payload
            except JWTError as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token validation error: {str(e)}",
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Authentication error: {str(e)}",
                )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization credentials",
        )

auth_scheme = Auth0Bearer()

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
def generate_podcast(data: ArticleRequest, token: dict = Depends(auth_scheme)): 
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
