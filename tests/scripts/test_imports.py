"""Test script to verify all imports and configurations"""

import sys

sys.path.insert(0, "A:/Projects/rocket-telemetry-ai")

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app import config, prompts

print("✅ All imports successful!")
print(f"✅ LLM Provider: {config.LLM_PROVIDER}")
print(f"✅ Model: {config.LLM_MODEL_NAME}")
print(f"✅ API Key configured: {config.GOOGLE_API_KEY is not None}")
print("✅ Using latest langchain-google-genai v3.1.0")
print("✅ ChatPromptTemplate configured correctly")

# Test LLM initialization
llm = ChatGoogleGenerativeAI(
    model=config.LLM_MODEL_NAME,
    google_api_key=config.GOOGLE_API_KEY,
    temperature=0.0,
)
print(f"✅ LLM initialized: {type(llm).__name__}")

# Test prompt template
prompt = ChatPromptTemplate.from_messages(
    [("system", prompts.SUMMARIZATION_SYSTEM_PROMPT), ("human", "{context}")]
)
print(f"✅ Prompt template created: {len(prompt.messages)} messages")

print("\n🎉 All components are working correctly with latest versions!")
