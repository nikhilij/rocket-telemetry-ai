"""
LangChain agent and tools for AI-powered analysis.
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
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


# Define tools for the agent
@tool
def get_anomalies_for_asset(asset_id: str, minutes: int = 60) -> str:
    """Get all anomalies detected for a specific asset in the last X minutes."""
    db = SessionLocal()
    try:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=minutes)
        anomalies = crud.get_anomalies_by_asset(db, asset_id, start_time, end_time)
        if not anomalies:
            return f"No anomalies detected for {asset_id} in the last {minutes} minutes."
        result = f"Anomalies for {asset_id} in the last {minutes} minutes:\n"
        for a in anomalies:
            result += f"- Metric: {a.metric}, Score: {a.score:.2f}, Time: {a.timestamp}, Explanation: {a.explanation}\n"
        return result
    finally:
        db.close()


@tool
def get_anomalies_last_minutes(minutes: int) -> str:
    """Get all anomalies detected in the last X minutes across all assets."""
    db = SessionLocal()
    try:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=minutes)
        anomalies = crud.get_anomalies_by_asset(db, None, start_time, end_time)
        if not anomalies:
            return "No anomalies detected in the last {} minutes.".format(minutes)
        result = "Anomalies in the last {} minutes:\n".format(minutes)
        for a in anomalies:
            result += f"- Asset: {a.asset_id}, Metric: {a.metric}, Score: {a.score:.2f}, Time: {a.timestamp}, Explanation: {a.explanation}\n"
        return result
    finally:
        db.close()


@tool
def get_telemetry_at_timestamp(asset_id: str, metric: str, timestamp: str) -> str:
    """Get telemetry value for a specific asset, metric, and timestamp."""
    db = SessionLocal()
    try:
        # Parse timestamp
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        # Find closest event
        events = crud.get_telemetry_events_by_metric(
            db, asset_id, metric, ts - timedelta(minutes=1), ts + timedelta(minutes=1)
        )
        if not events:
            return f"No telemetry found for {asset_id}/{metric} near {timestamp}."
        # Find closest
        closest = min(events, key=lambda e: abs((e.timestamp - ts).total_seconds()))
        return f"At {closest.timestamp}: {metric} = {closest.value} {closest.unit}"
    finally:
        db.close()


@tool
def get_recent_telemetry(asset_id: str, minutes: int) -> str:
    """Get recent telemetry data for an asset in the last X minutes."""
    db = SessionLocal()
    try:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(minutes=minutes)
        telemetry = crud.get_telemetry_for_agent(db, asset_id, start_time, end_time)
        if not telemetry:
            return f"No telemetry data for {asset_id} in the last {minutes} minutes."
        result = f"Recent telemetry for {asset_id} (last {minutes} minutes):\n"
        for t in telemetry[-10:]:  # Last 10 for brevity
            result += f"- {t.timestamp}: {t.metric} = {t.value} {t.unit}\n"
        return result
    finally:
        db.close()


tools = [get_anomalies_for_asset, get_anomalies_last_minutes, get_telemetry_at_timestamp, get_recent_telemetry]


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
    Agent that answers a natural language question using tools.
    """
    llm_with_tools = llm.bind_tools(tools)

    try:
        # System prompt for conversational responses
        system_prompt = (
            "You are a helpful AI assistant for rocket telemetry analysis. "
            "Answer questions naturally and conversationally, using the results from tools. "
            "If no anomalies are found, confirm that clearly and offer to check further if needed. "
            "Keep responses informative and friendly. "
            "When asked about anomalies without a specific time range, check the last 60 minutes by default."
        )

        # Initial messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.question),
        ]

        # Initial call
        ai_msg = llm_with_tools.invoke(messages)
        sources = []

        if ai_msg.tool_calls:
            tool_results = []
            for tool_call in ai_msg.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                sources.append({"tool": tool_name, "input": tool_args})
                if tool_name == "get_anomalies_for_asset":
                    result = get_anomalies_for_asset.run(tool_args)
                elif tool_name == "get_anomalies_last_minutes":
                    result = get_anomalies_last_minutes.run(tool_args)
                elif tool_name == "get_telemetry_at_timestamp":
                    result = get_telemetry_at_timestamp.run(tool_args)
                elif tool_name == "get_recent_telemetry":
                    result = get_recent_telemetry.run(tool_args)
                else:
                    result = "Unknown tool"
                tool_results.append(
                    ToolMessage(content=result, tool_call_id=tool_call["id"])
                )

            # Call again with tool results
            messages = messages + [ai_msg] + tool_results
            final_response = llm_with_tools.invoke(messages)
            answer = final_response.content
        else:
            answer = ai_msg.content

        return schemas.AskResponse(answer=answer, sources=sources)
    except Exception as e:
        return schemas.AskResponse(
            answer=f"Error processing question: {str(e)}", sources=[]
        )


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
