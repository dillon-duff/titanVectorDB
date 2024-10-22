from flask import Flask, render_template, request, jsonify
from qa_system import qa_system
import pdb

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = request.json.get('question')
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    
    try:
        response = qa_system(question)
        print(f"Response: {response}")
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
