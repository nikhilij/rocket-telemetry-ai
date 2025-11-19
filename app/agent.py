"""
LangChain agent and tools for AI-powered analysis.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Any
import json
import numpy as np
from datetime import datetime, timedelta, timezone

from . import crud, schemas, config, prompts
from .db import SessionLocal

# Initialize the LLM based on provider configuration
# Defaults to Google Generative AI (Gemini)
if config.LLM_PROVIDER == "google_genai":
    llm = ChatGoogleGenerativeAI(
        model=config.LLM_MODEL_NAME,
        google_api_key=config.GOOGLE_API_KEY,
        temperature=0.0,  # We want deterministic, factual answers
    )
else:
    # Fallback or raise error if provider not supported
    raise ValueError(f"Unsupported LLM provider: {config.LLM_PROVIDER}")


def get_summary_agent(asset_id: str, window_minutes: int) -> schemas.SummaryResponse:
    """
    Agent that generates a health summary for an asset.
    """
    db = SessionLocal()
    try:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=window_minutes)

        # 1. Retrieve data using CRUD functions
        anomalies = crud.get_anomalies_by_asset(db, asset_id, start_time, end_time)
        telemetry = crud.get_telemetry_for_agent(db, asset_id, start_time, end_time)

        if not telemetry and not anomalies:
            return schemas.SummaryResponse(
                asset_id=asset_id,
                summary="No telemetry data or anomalies found for the given time window.",
            )

        # 2. Aggregate and format the context for the LLM
        context = _build_summary_context(anomalies, telemetry)

        # 3. Create and run the LangChain chain
        prompt = ChatPromptTemplate.from_messages(
            [("system", prompts.SUMMARIZATION_SYSTEM_PROMPT), ("human", "{context}")]
        )
        chain = prompt | llm

        raw_response = chain.invoke({"context": context})

        # 4. Extract the content from AIMessage
        summary_text = raw_response.content

        return schemas.SummaryResponse(asset_id=asset_id, summary=summary_text)

    finally:
        db.close()


def get_qa_agent(request: schemas.AskRequest) -> schemas.AskResponse:
    """
    Agent that answers a natural language question about telemetry data.
    """
    db = SessionLocal()
    try:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=request.window_minutes)

        # 1. Retrieve data
        telemetry = crud.get_telemetry_for_agent(
            db, request.asset_id, start_time, end_time
        )

        if not telemetry:
            return schemas.AskResponse(
                answer="I don't have enough data to answer that question.", sources=[]
            )

        # 2. Format context
        context = _build_qa_context(telemetry)

        # 3. Create and run chain
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", prompts.QA_SYSTEM_PROMPT),
                ("human", "Question: {question}\n\nContext: {context}"),
            ]
        )
        chain = prompt | llm

        response = chain.invoke({"question": request.question, "context": context})
        answer = response.content

        # 4. Format response
        sources = [
            {"type": "telemetry", "id": str(t.id), "timestamp": t.timestamp.isoformat()}
            for t in telemetry[:5]  # Cite the 5 most recent sources
        ]

        return schemas.AskResponse(answer=answer, sources=sources)

    finally:
        db.close()


def _build_summary_context(
    anomalies: List[schemas.AnomalyRecordInDB],
    telemetry: List[schemas.TelemetryEventInDB],
) -> str:
    """Helper to format data into a string for the summary prompt."""
    context_str = "Context for Asset Health Summary:\n\n"

    if anomalies:
        context_str += "1. Recent Anomalies:\n"
        for anom in anomalies[:5]:  # Limit to 5 most recent anomalies
            context_str += (
                f"- At {anom.timestamp.strftime('%H:%M:%S')}: {anom.explanation}\n"
            )
    else:
        context_str += "1. No anomalies detected in this window.\n"

    context_str += "\n2. Telemetry Overview:\n"

    # Aggregate telemetry by metric
    metrics_agg = {}
    for event in telemetry:
        if event.metric not in metrics_agg:
            metrics_agg[event.metric] = []
        metrics_agg[event.metric].append(event.value)

    if not metrics_agg:
        context_str += "No telemetry data available.\n"
    else:
        for metric, values in metrics_agg.items():
            context_str += (
                f"- Metric '{metric}': "
                f"{len(values)} data points, "
                f"Avg: {np.mean(values):.2f}, "
                f"Min: {min(values):.2f}, "
                f"Max: {max(values):.2f}\n"
            )

    return context_str


def _build_qa_context(telemetry: List[schemas.TelemetryEventInDB]) -> str:
    """Helper to format data into a string for the Q&A prompt."""
    context_str = "Context Telemetry Data:\n"
    for event in telemetry:
        context_str += (
            f"- telemetry(metric='{event.metric}', value={event.value}, unit='{event.unit}', "
            f"timestamp='{event.timestamp.isoformat()}', asset_id='{event.asset_id}')\n"
        )
    return context_str
