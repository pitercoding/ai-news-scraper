import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY is not configured."
    )


client = OpenAI(
    api_key=api_key
)


class ArticleAnalysis(BaseModel):
    summary: str
    key_points: list[str]
    category: str


def ask_openai(prompt: str) -> str:
    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt,
    )

    return response.output_text


def analyze_article(prompt: str) -> ArticleAnalysis:
    response = client.responses.parse(
        model="gpt-5-mini",
        input=prompt,
        text_format=ArticleAnalysis,
    )

    return response.output_parsed