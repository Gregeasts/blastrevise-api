from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
past_questions = []  # Stores all generated questions in memory


# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ ERROR: Missing Google Gemini API Key")
    exit(1)

# Configure the Gemini API
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/reset-memory", methods=["POST"])
def reset_memory():
    global past_questions
    past_questions = []  # Clear memory
    return jsonify({"message": "Question memory has been reset."})

# Endpoint to generate quiz questions (only questions, no answers)
@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    global past_questions  
    try:
        data = request.get_json()
        topic = data.get("topic")
        num_questions = data.get("num_questions")
        format_type = data.get("question_format")
        question_level = data.get("question_level")
        avoid_questions = "\n".join(past_questions)
        print(avoid_questions)
        

        # Ensure parameters are received
        if not topic or not num_questions or not format_type:
            raise ValueError("Missing parameters")

        # Create a Gemini prompt to generate questions only
        prompt = f"""
        Generate {num_questions} {format_type} quiz questions on the topic "{topic}" at a teaching level of {question_level}. Do NOT repeat any of these past questions {avoid_questions}. All questions must be of exactly the question type {format_type} (for short answer there should be no multiple choice or long answer questions.)
        Provide only the questions as a JSON list. Do not provide the answers and for multiple choice have questions and options in same index eg) do not have them split into seperate lists etc have them all in the same long string as shown below.
        For example:
        ["What is AI?", "How does machine learning work?"]
        If multiple choice: ["What is AI?" (a) a car, (b) a dog, (c) Artificial intelligence",]
        If the questions are of type long answer, add a larger mark relevant to the question for each eg) out of 30.
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        response_string = response.text
        print("Current Memory:", past_questions)  # Debugging output
        
        
        
        



        # Check if the response is empty or malformed
       
        
        # Attempt to parse the questions
        
        past_questions.append(response_string)

        return jsonify({"questions": response_string})
        


    except Exception as e:
        print(f"Error generating quiz: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint to check each answer
@app.route("/check-answer", methods=["POST"])
def check_answer():
    try:
        data = request.get_json()
        
        question = data.get("question")
        user_answer = data.get("user_answer")
        questiontype =data.get("questiontype")
        questionlevel=data.get("questionlevel")

        print("hi",user_answer)
        
        # Create a Gemini prompt to evaluate the student's answer
        prompt = f"""
        Evaluate the following:
        Question: {question}
        Student's Answer: {user_answer}
        Question format: {questiontype}
        Question level:{questionlevel}
        Reply with "Correct" if the answer is correct, or "Wrong" if the answer is wrong. For the format types of multiple choice and short answer, then add a comment on why the answer is wrong if it is, with the correct answer given (not in loads of detail. Do not ever use the word "correct" in this explanation! For the long answer questions, there will be a max mark given in the question, after deciding whether the answer is roughly right or wrong, give it a mark out of this max mark, critically analysing all of the factual reasoning, grammar and layout of the argument, structure etc and however else the question would be analysed at the given level. Be harsh!)
        """
        
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        

        # Check if the response is empty or malformed
        if not response.text.strip():
            raise ValueError("Received empty response from Gemini AI.")
        
        result = response.text.strip()
       
        
        return jsonify({"result": result})
    except Exception as e:
        print(f"Error checking answer: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)


