from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
app = Flask(__name__)
import re
from openai import OpenAI
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OpenAI_api_key"),
)

def query_model(user_query, content):

    
   
    """Passes user query and email list to the model for classification."""
    messages = [
        {"role": "system", "content": "System Prompt"},
        {"role": "user", "content": f"User Query: {user_query}\n\nContent:\n{content}"}
    ]

    completion = client.chat.completions.create(
        model="google/gemma-3-27b-it:free",
        messages=messages
    )
    print(completion.choices[0].message.content)
    return completion.choices[0].message.content
