from flask import Flask, request, jsonify, render_template
from datetime import datetime, timezone
import requests
import os
from dotenv import load_dotenv
from supabase import create_client

# 🔐 Load environment variables from .env
load_dotenv()

# ✅ Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# 🔗 Supabase setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🤖 Hugging Face setup
HF_API_URL = os.getenv("HF_API_URL")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# 🏠 Home route
@app.route("/")
def index(): 
    return render_template("index.html")

# 🧠 Analyze mood route
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json(force=True)
        entry = data.get("entry", "").strip()

        if not entry:
            return jsonify({"error": "No journal entry provided"}), 400

        # 🔍 Call Hugging Face API
        hf_response = requests.post(HF_API_URL, headers=HF_HEADERS, json={"inputs": entry})
        hf_result = hf_response.json()

        label = hf_result[0][0]["label"]
        score = round(hf_result[0][0]["score"] * 100, 2)

        # 💾 Save to Supabase
        supabase.table("moods").insert({
            "entry": entry,
            "mood": label,
            "score": score,
            "timestamp": datetime.now(timezone.utc).isoformat()

        }).execute()

        return jsonify({"mood": label, "score": score})

    except Exception as e:
        print("Error in /analyze:", e)
        return jsonify({"error": str(e)}), 500

# 📊 History route
@app.route("/history", methods=["GET"])
def history():
    try:
        res = supabase.table("moods").select("*").order("timestamp", desc=False).execute()
        return jsonify(res.data)
    except Exception as e:
        print("Error in /history:", e)
        return jsonify({"error": str(e)}), 500

# 🚀 Run the app
if __name__ == "__main__":
    app.run(debug=True)