import os
from langchain.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv


def load_environment_variable():
    """ 
    Load the environment variable containing the GROQ API key
    """
    try:
        load_dotenv()
        # Fetch the API key from the environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set or is empty")
        print("API key loaded successfully")
        return api_key
    
    except Exception as e:
        print(f"Error loading environment variable: {e}")
        return None


def get_llm_response(prompt_user):
    """ 
    Get response from llama3-8b- model using the given prompt
    """
    api = load_environment_variable()
    llm = ChatGroq(model="llama3-8b-8192", groq_api_key=api)

    system = "You are a software engineer"
    human="{text}"
    prompt=ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", human)
    ]
    )

    chain=prompt | llm

    prompt = prompt_user
    response = chain.invoke({"text": prompt}) 
    return response.content


    