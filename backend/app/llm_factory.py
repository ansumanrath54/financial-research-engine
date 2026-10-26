import os
import boto3
from typing import Tuple
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import AzureChatOpenAI
from langchain_aws import ChatBedrockConverse

DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "claude").lower()
LLM_REQUEST_TIMEOUT_SECONDS = 45

def get_llm(provider: str = DEFAULT_PROVIDER) -> BaseChatModel:
    prov = provider.lower()

    if prov == "claude":
        return ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0,
            api_key=os.getenv("ANTHROPIC_API_KEY", "mock-key"),
            timeout=LLM_REQUEST_TIMEOUT_SECONDS,
            max_retries=0
        )
    elif prov == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY", "mock-key"),
            timeout=LLM_REQUEST_TIMEOUT_SECONDS,
            max_retries=1
        )
    elif prov == "azure":
        return AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY", "mock-key"),
            temperature=0,
            timeout=LLM_REQUEST_TIMEOUT_SECONDS,
            max_retries=0
        )
    elif prov == "aws":
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=os.getenv("AWS_SESSION_TOKEN", None)
        )
        return ChatBedrockConverse(
            model=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
            temperature=0,
            client=client,
            timeout=LLM_REQUEST_TIMEOUT_SECONDS,
            max_retries=1
        )
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}. Options: 'claude', 'gemini', 'azure', 'aws'")

def get_provider_rate_card(provider: str = DEFAULT_PROVIDER) -> Tuple[float, float]:
    prov = provider.lower()
    if prov in ["claude", "aws"]:
        return (3.0, 15.0)
    elif prov == "gemini":
        return (1.25, 5.0)
    elif prov == "azure":
        return (2.5, 10.0)
    return (3.0, 15.0)

def extract_text_content(content) -> str:
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                text_parts.append(block["text"])

        if text_parts:
            return "\n".join(text_parts)

    raise ValueError(f"Expected text response content, received {type(content).__name__}")

def extract_token_counts(res) -> Tuple[int, int]:
    if hasattr(res, "usage_metadata") and res.usage_metadata:
        in_tok = res.usage_metadata.get("input_tokens", 0)
        out_tok = res.usage_metadata.get("output_tokens", 0)
        return in_tok, out_tok

    meta = getattr(res, "response_metadata", {})
    usage = meta.get("usage", {}) or meta.get("token_usage", {})
    in_tok = usage.get("input_tokens") or usage.get("prompt_tokens") or 150
    out_tok = usage.get("output_tokens") or usage.get("completion_tokens") or 50
    return in_tok, out_tok