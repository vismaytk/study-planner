import os,markdown
from flask import Flask, render_template, request, send_from_directory, jsonify
import PIL.Image
import google.generativeai as genai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    return render_template('schedulePlanner.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    return render_template('chatbotPage.html')

@app.route('/qpa', methods=['POST'])
def qpa():
    return render_template('qpAnalyzer.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    response = model.generate_content(user_input)
    response_text = response.text.strip() 

    return jsonify({"response": response_text})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'response': 'No file part'})
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'response': 'No selected file'})
    
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'response': f'File {filename} uploaded successfully.'})

@app.route('/generate_content', methods=['POST'])
def generate_content():
    if 'image' not in request.files or request.files['image'].filename == '':
        return "No image uploaded!", 400
    image_file = request.files['image']
    prompt = request.form['prompt']
    days = request.form['days']
    instruct = 'i have '+ days +' days to complete this, give me a whole study plan for same.'

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
    image_file.save(image_path)
    img = PIL.Image.open(image_path)
    
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    response = model.generate_content([instruct+prompt, img])
    
    response_html = markdown.markdown(response.text)

    return render_template('resultSchedulePlanner.html', prompt=prompt, image_url=image_file.filename, response_html=response_html)

@app.route('/qp_Analyzer', methods=['POST'])
def qp_analyzer():
    if 'image' not in request.files or request.files['image'].filename == '':
        return "No image uploaded!", 400
    image_file = request.files['image']

    instruct="Analyze the provided file to classify questions, extract keywords, assess difficulty, recognize patterns, perform comparative analysis, provide personalized study recommendations, summarize text, generate questions, and create a knowledge graph of key concepts and relationships for the text given ahead: "
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
    image_file.save(image_path)
    img = PIL.Image.open(image_path)
    
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
    response = model.generate_content([instruct, img])
    response_html = markdown.markdown(response.text)

    return render_template('qpResult.html', image_url=image_file.filename, response_html=response_html)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
