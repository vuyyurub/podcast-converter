from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from newspaper import Article
import uuid
from pydub import AudioSegment
from typing import Optional
from urllib.request import urlopen
import json
import boto3
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from boto3.dynamodb.conditions import Key
import nltk
import os

nltk.download("punkt")
from nltk.tokenize import sent_tokenize
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "bvuyyuru-polly-bucket")


AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
API_AUDIENCE = os.getenv("AUTH0_API_AUDIENCE")
ALGORITHMS = ["RS256"]


s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

polly = boto3.client(
    "polly",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

podcast_table = dynamodb.Table(os.getenv("DYNAMODB_PODCAST_TABLE", "Podcasts"))
user_table = dynamodb.Table(os.getenv("DYNAMODB_USER_TABLE", "Users"))


class Auth0Bearer(HTTPBearer):
    async def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
        token = credentials.credentials
        try:
            jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
            jwks = json.loads(urlopen(jwks_url).read())
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = next(
                (key for key in jwks["keys"] if key["kid"] == unverified_header["kid"]),
                None
            )
            if rsa_key:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer=f"https://{AUTH0_DOMAIN}/"
                )
                return payload
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Token error: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

auth_scheme = Auth0Bearer()


class UrlRequest(BaseModel):
    url: str

class TextRequest(BaseModel):
    text: str

class GenerateRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None

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


def synthesize_text_to_audio(text: str, base_filename: str):
    chunks = split_text(text)
    audio_segments = []
    temp_files = []

    for i, chunk in enumerate(chunks):
        filename = f"{base_filename}_part{i + 1}.mp3"
        try:
            response = polly.synthesize_speech(
                Text=chunk,
                OutputFormat="mp3",
                VoiceId=os.getenv("POLLY_VOICE_ID", "Joanna")
            )
            with open(filename, "wb") as f:
                f.write(response["AudioStream"].read())
            temp_files.append(filename)
            audio_segments.append(AudioSegment.from_mp3(filename))
        except Exception as e:
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)
            raise RuntimeError(f"Polly error: {e}")

    if not audio_segments:
        raise RuntimeError("No audio segments were generated")

    merged_audio = audio_segments[0]
    for seg in audio_segments[1:]:
        merged_audio += seg

    merged_filename = f"{base_filename}_full.mp3"
    merged_audio.export(merged_filename, format="mp3")

    try:
        s3.upload_file(
            merged_filename, 
            S3_BUCKET, 
            merged_filename,
            ExtraArgs={'ACL': 'public-read'}
        )
    except Exception as e:
        raise RuntimeError(f"S3 upload failed: {e}")
    finally:
        for f in temp_files + [merged_filename]:
            if os.path.exists(f):
                os.remove(f)

    return f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{merged_filename}"

@app.post("/api/generate")
def generate(request: GenerateRequest, token: dict = Depends(auth_scheme)):
    if request.text:
        return generate_from_text(TextRequest(text=request.text), token)
    elif request.url:
        return generate_from_url(UrlRequest(url=request.url), token)
    else:
        raise HTTPException(status_code=400, detail="Either text or URL must be provided.")


@app.post("/api/generate-from-url")
def generate_from_url(data: UrlRequest, token: dict = Depends(auth_scheme)):
    try:
        article = Article(data.url)
        article.download()
        article.parse()
        text = article.text
        title = article.title or f"article-{uuid.uuid4()}"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Article download/parse error: {e}")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Article has no text content.")

    audio_url = synthesize_text_to_audio(text, title[:50].replace(" ", "_"))

    user_id = token.get("sub")
    user_email = token.get("email")
    user_name = token.get("name")
    try:
        user_table.put_item(
            Item={
                "user_id": user_id,
                "email": user_email,
                "name": user_name
            },
            ConditionExpression="attribute_not_exists(user_id)"
        )
    except:
        pass
    podcast_id = str(uuid.uuid4())
    podcast_table.put_item(
        Item={
            "podcast_id": podcast_id,
            "user_id": user_id,
            "title": title,
            "source": "url",
            "source_url": data.url,
            "audio_url": audio_url,
            "created_at": datetime.utcnow().isoformat()
        }
    )

    return {"audio_url": audio_url}

@app.post("/api/generate-from-text")
def generate_from_text(data: TextRequest, token: dict = Depends(auth_scheme)):
    text = data.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Input text is empty.")
    title = f"text-{uuid.uuid4()}"
    audio_url = synthesize_text_to_audio(text, title)

    user_id = token.get("sub")
    user_email = token.get("email")
    user_name = token.get("name")
    try:
        user_table.put_item(
            Item={
                "user_id": user_id,
                "email": user_email,
                "name": user_name
            },
            ConditionExpression="attribute_not_exists(user_id)"
        )
    except:
        pass  
    podcast_id = str(uuid.uuid4())
    podcast_table.put_item(
        Item={
            "podcast_id": podcast_id,
            "user_id": user_id,
            "title": title,
            "source": "text",
            "audio_url": audio_url,
            "created_at": datetime.utcnow().isoformat()
        }
    )

    return {"audio_url": audio_url}

@app.get("/api/podcasts")
def get_user_podcasts(token: dict = Depends(auth_scheme)):
    user_id = token.get("sub")
    try:
        response = podcast_table.query(
            IndexName="user_id-index",
            KeyConditionExpression=Key("user_id").eq(user_id)
        return {"podcasts": response.get("Items", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching podcasts: {e}")

@app.post("/api/podcasts/{podcast_id}/favorite")
def toggle_favorite(podcast_id: str, token: dict = Depends(auth_scheme)):
    user_id = token.get("sub")
    try:
        response = podcast_table.get_item(Key={"podcast_id": podcast_id})
        item = response.get("Item")
        if not item or item.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access to podcast")
        
        is_favorite = item.get("is_favorite", False)
        podcast_table.update_item(
            Key={"podcast_id": podcast_id},
            UpdateExpression="SET is_favorite = :val",
            ExpressionAttributeValues={":val": not is_favorite}
        )
        return {"message": "Favorite updated", "is_favorite": not is_favorite}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle favorite: {e}")