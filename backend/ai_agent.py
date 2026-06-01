from langchain.agents import tool
from backend.tools import query_medgemma, call_emergency,fetch_nearby_therapists

@tool
async def ask_mental_health_specialist(query: str) -> str:
    """
    Generate a therapeutic response using the groq model.
    Use this for all general user queries, mental health questions, emotional concerns,
    or to offer empathetic, evidence-based guidance in a conversational tone.
    """
    return await query_medgemma(query)


# @tool
# def emergency_call_tool() -> None:
#     """
#     Place an emergency call to the safety helpline's phone number via Twilio.
#     Use this only if the user expresses suicidal ideation, intent to self-harm,
#     or describes a mental health emergency requiring immediate help.
#     """
#     call_emergency()
@tool
async def emergency_call_tool() -> str:
    """
    Place an emergency call to the safety helpline's phone number via Twilio.
    Use this only if the user expresses suicidal ideation, intent to self-harm,
    or describes a mental health emergency requiring immediate help.
    """
    # Even though call_emergency() is sync in tools.py, we wrap it in this async tool
    call_emergency()
    return "Emergency call successfully placed."


@tool
async def find_nearby_therapists_by_location(location: str) -> str:
    """
    Finds and returns a list of licensed therapists near the specified location.
    ALWAYS use this tool immediately when a user asks to find, locate, or search for 
    a therapist, doctor, counselor, clinic, or hospital in a specific area or city.
    Do not give general advice; use this tool instead.

    Args:
        location (str): The name of the city or area in which the user is seeking therapy support.

    Returns:
        str: A newline-separated string containing therapist names and contact info.
    """
    # Fix: Added the 'await' keyword here so it actually runs your Geoapify code!
    return await fetch_nearby_therapists(location)

# Step1: Create an AI Agent & Link to backend
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from backend.config import GROQ_API_KEY


tools = [ask_mental_health_specialist, emergency_call_tool, find_nearby_therapists_by_location]
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.2, api_key=GROQ_API_KEY)
graph = create_react_agent(llm, tools=tools)

SYSTEM_PROMPT = """
You are an AI engine supporting mental health conversations with warmth and vigilance.
You have access to three tools:

1. `ask_mental_health_specialist`: Use this tool to answer general emotional or psychological queries with therapeutic guidance.
2. `find_nearby_therapists_by_location`: You MUST use this tool whenever a user explicitly asks to find a therapist, clinic, doctor, or professional help near a location. Do not hallucinate directories or tables. Use the data from this tool to provide a short, direct list of real names and addresses.
3. `emergency_call_tool`: Use this immediately if the user expresses suicidal thoughts, self-harm intentions, or is in crisis.

Keep your responses clean, comforting, and direct. When providing local options, list the doctor/clinic names directly from the tool response.
"""

# def parse_response(stream):
#     tool_called_name = "None"
#     final_response = None

#     for s in stream:
#         # Check if a tool was called
#         tool_data = s.get('tools')
#         if tool_data:
#             tool_messages = tool_data.get('messages')
#             if tool_messages and isinstance(tool_messages, list):
#                 for msg in tool_messages:
#                     tool_called_name = getattr(msg, 'name', 'None')

#         # Check if agent returned a message
#         agent_data = s.get('agent')
#         if agent_data:
#             messages = agent_data.get('messages')
#             if messages and isinstance(messages, list):
#                 for msg in messages:
#                     if msg.content:
#                         final_response = msg.content

#     return tool_called_name, final_response


# Added 'async' here
async def parse_response(stream):
    tool_called_name = "None"
    final_response = None

    # Added 'async for' here because the stream will now be asynchronous
    async for s in stream:
        # Check if a tool was called
        tool_data = s.get('tools')
        if tool_data:
            tool_messages = tool_data.get('messages')
            if tool_messages and isinstance(tool_messages, list):
                for msg in tool_messages:
                    tool_called_name = getattr(msg, 'name', 'None')

        # Check if agent returned a message
        agent_data = s.get('agent')
        if agent_data:
            messages = agent_data.get('messages')
            if messages and isinstance(messages, list):
                for msg in messages:
                    if msg.content:
                        final_response = msg.content

    return tool_called_name, final_response

"""if __name__ == "__main__":
    while True:
        user_input = input("User: ")
        print(f"Received user input: {user_input[:200]}...")
        inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", user_input)]}
        stream = graph.stream(inputs, stream_mode="updates")
        tool_called_name, final_response = parse_response(stream)
        print("TOOL CALLED: ", tool_called_name)
        print("ANSWER: ", final_response)"""
        