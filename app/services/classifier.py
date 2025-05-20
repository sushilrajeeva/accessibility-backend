# app/services/classifier.py

import asyncio
from typing import List, Dict

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import settings

# 1) Build a chat prompt template
#    We're wrapping the content in a single-user message template.
_CHAT_PROMPT = ChatPromptTemplate.from_template(
    """You are an accessibility-tagging assistant.
Assign exactly one tag from: title, h1, paragraph, image_caption, image, footer.

Region content:
\"\"\"{content}\"\"\"

Respond with just the tag label."""
)

# 2) Initialize the ChatOpenAI LLM
_llm = ChatOpenAI(
    model=settings.LLM_MODEL_NAME,
    temperature=settings.LLM_TEMPERATURE,
    openai_api_key=settings.OPENAI_API_KEY,
)

# 3) Build the pipeline: prompt → LLM → string parser
_chain = _CHAT_PROMPT | _llm | StrOutputParser()

async def classify_region(region: Dict) -> str:
    """
    Given a region dict with keys 'type' and 'content',
    returns a tag label string.
    - For images, returns 'image' immediately.
    - Otherwise, invokes the prompt→LLM pipeline asynchronously.
    """
    if region.get("type") == "image":
        return "image"

    # 4) Invoke the chain with the content variable
    result: str = await _chain.ainvoke({"content": region["content"]})
    return result.strip()

async def classify_regions(regions: List[Dict]) -> List[Dict]:
    """
    Classify a list of regions in parallel via asyncio.gather.
    Adds a 'tag' field to each region dict and returns the list.
    """
    tasks = [classify_region(r) for r in regions]
    tags = await asyncio.gather(*tasks)
    for region, tag in zip(regions, tags):
        region["tag"] = tag
    return regions
