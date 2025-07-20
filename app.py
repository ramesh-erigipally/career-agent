# Career Agent - AI-powered resume chatbot
# This application creates a conversational AI that can answer questions about a person's background
# using their resume and LinkedIn summary, with capabilities to record user interactions
# Author: Ramesh Erigipally
__version__ = "1.0.0"
"""
Career Agent - AI-powered resume chatbot

Author: Ramesh Erigipally
Version: 1.0.0

Description:
This application creates a conversational AI that can answer questions about a person's background
using their resume and LinkedIn summary, with capabilities to record user interactions.

Repository: https://github.com/ramesh-erigipally/career-agent
License: MIT
"""




import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
import gradio as gr

# Load environment variables from .env file
load_dotenv(override=True)

# Initialize OpenAI client with API key
api_key = os.getenv("OPENAI_API_KEY")
openai = OpenAI(api_key=api_key)

# Validate that required API key is present
if api_key is None: 
    raise ValueError("OPENAI_API_KEY is not set")

# File paths for resume data
pdf_path = "data/resume.pdf"
summary_path = "data/summary.txt"

def get_pdf_text(pdf_path):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from all pages of the PDF
    """
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def get_text_from_file(file_path):
    """
    Read text content from a text file.
    
    Args:
        file_path (str): Path to the text file
        
    Returns:
        str: Content of the text file
    """
    with open(file_path, "r") as file:
        return file.read()

# Load resume data from files
resume_data = get_pdf_text(pdf_path) 
resume_summary = get_text_from_file(summary_path)

# Pushover notification configuration
# Used to send notifications when users interact with the chatbot
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

def send_pushover(message):
    """
    Send a notification message via Pushover service.
    
    Args:
        message (str): Message to send
        
    Returns:
        dict: Response from Pushover API or error status
    """
    # Check if Pushover credentials are configured
    if not pushover_user or not pushover_token:
        print("Pushover credentials not configured")
        return {"status": "error", "message": "Pushover not configured"}
    
    try:
        data = {
            "token": pushover_token,
            "user": pushover_user,
            "message": message
        }
        response = requests.post(pushover_url, data=data)
        return response.json()
    except Exception as e:
        print(f"Error sending pushover notification: {e}")
        return {"status": "error", "message": str(e)}

def record_user_details(email, name="Not provided", notes="not provided"):
    """
    Record user contact details and send notification.
    Called when users provide their email for follow-up.
    
    Args:
        email (str): User's email address
        name (str): User's name (optional)
        notes (str): Additional notes about the user (optional)
        
    Returns:
        dict: Success status
    """
    send_pushover(f"User details recorded: email: {email}, Name: {name}, note:{notes}")
    return {"status": "success"}

def record_unknown_question(question):
    """
    Record questions that the AI cannot answer.
    Used for tracking and improving the chatbot's knowledge base.
    
    Args:
        question (str): The question that couldn't be answered
        
    Returns:
        dict: Success status
    """
    send_pushover(f"Unknown question: {question}")
    return {"status": "success"}

# Tool definitions for OpenAI function calling
# These define the functions that the AI can call during conversations

record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The name of this user"
            },
            "notes": {
                "type": "string",
                "description": "Any additional notes about this user"
            }
        },
        "required": ["email"]
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Use this tool to record that a user has asked a question that is not related to the resume",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that the user has asked"
            }
        },
        "required": ["question"]
    }
}

# List of available tools for the AI
tools = [{"type": "function", "function": record_user_details_json}, {"type": "function", "function": record_unknown_question_json}]

print("tools")
print(tools)

# Person whose background the AI represents
name = "Ramesh Erigipally"

# System prompt that defines the AI's role and behavior
system_prompt = f"""
Your character is {name}. You are responsible for answering questions related to {name}, his background, skills and experience.
You are given a summary of a person's background and LinkedIn profile which you can use to answer questions.
You are also given a resume of the person.
You are given with {name}'s resume data and summary of his background and LinkedIn profile.
"""

# Add context data to the system prompt
system_prompt += f"Summary:\n{resume_summary}\n\nResume:\n{resume_data}"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."
system_prompt += f"If you don't know the answer use the tool record_unknown_question to record the question that you couldn't answer, even if it's about something trivial or unrelated to career."
system_prompt += f"If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool."

def handle_tool_calls(tool_calls):
    """
    Process tool calls from the AI and execute the corresponding functions.
    
    Args:
        tool_calls: List of tool call objects from OpenAI API
        
    Returns:
        list: List of tool result messages to add to conversation
    """
    print("tool_calls")
    print(tool_calls)
    results = []
    for tool_call in tool_calls:
        if tool_call.function.name == "record_user_details":
            args = json.loads(tool_call.function.arguments)
            result = record_user_details(**args)
            results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
        elif tool_call.function.name == "record_unknown_question":
            args = json.loads(tool_call.function.arguments)
            result = record_unknown_question(**args)
            results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return results
    

def chat(message, history):
    """
    Main chat function that handles conversations with users.
    Processes messages through OpenAI API and handles tool calls.
    
    Args:
        message (str): User's input message
        history (list): Previous conversation messages
        
    Returns:
        str: AI's response to the user
    """
    # Build message history including system prompt
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    done = False
    max_iterations = 10  # Prevent infinite loops from repeated tool calls
    iteration = 0
    
    # Loop to handle multiple tool calls in sequence
    while not done and iteration < max_iterations:
        try:
            # Call OpenAI API with tools enabled
            response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)
            finish_reason = response.choices[0].finish_reason

            if finish_reason == "tool_calls":
                # AI wants to call a tool - process the tool calls
                assistant_message = response.choices[0].message
                tool_calls = assistant_message.tool_calls
                results = handle_tool_calls(tool_calls)
                messages.append(assistant_message)
                messages.extend(results)
                iteration += 1
            else:
                # AI has finished responding.
                done = True
                
        except Exception as e:
            print(f'Erro Details {e}');
            error_message = getattr(e, "response", {}).json().get("error", {}).get("message")
           
            return f"I apologize, but I encountered an error processing your request. \n {error_message}"
        
    # Return the final response or error message
    return response.choices[0].message.content if response.choices[0].message.content else "I apologize, but I encountered an error processing your request."

# Launch the Gradio chat interface
# This creates a web-based chat UI for users to interact with the AI

description = f'''Hi, I’m Ramesh’s AI Career Agent – here to help you explore his professional journey.
Ask me anything about his skills, experience, or background – I’ve got the answers!'''

gr.ChatInterface(
    chat,
    type="messages",
    description=description
).launch()