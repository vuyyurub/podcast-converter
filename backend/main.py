import boto3
from newspaper import Article
import uuid

s3_bucket = "bvuyyuru-polly-bucket" 
url = input("Enter article URL: ")
article = Article(url)
article.download()
article.parse()
text = article.text
title = article.title or f"article-{uuid.uuid4()}"
filename = f"{title[:50].replace(' ', '_')}.mp3"

polly = boto3.client('polly')
response = polly.synthesize_speech(
    Text=text[:3000],
    OutputFormat='mp3',
    VoiceId='Joanna'
)
with open(filename, 'wb') as f:
    f.write(response['AudioStream'].read())
print(f"MP3 saved locally as {filename}")
s3 = boto3.client('s3')
s3.upload_file(filename, s3_bucket, filename)
url = f"https://{s3_bucket}.s3.amazonaws.com/{filename}"
print(f"Uploaded to S3: {url}")
