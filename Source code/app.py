from flask import Flask, render_template, request, make_response
from flask_socketio import SocketIO, emit
import spacy
import pdfkit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

nlp = spacy.load('en_core_web_sm')

products = {
    'milk': 3,
    'egg': 5,
    'bread': 2,
    'butter': 7,
    'cheese': 4,
    'apple': 6,
    'banana': 19,
    'orange': 8,
    'pumpkin': 12,
    'potato': 23,
    'onion': 9,
    'carrot': 15,
    'lettuce': 1,
    'cucumber': 14,
    'icecream': 10,
    'broccoli': 18,
    'toffee': 11,
    'spinach': 20,
    'chicken': 25,
    'beef': 17,
    'pork': 13,
    'salmon': 22,
    'tuna': 16,
    'shrimp': 21,
    'rice': 48,
    'pasta': 30,
    'flour': 28,
    'sugar': 24,
    'salt': 26,
    'pepper': 29,
    'oil': 31,
    'sausage': 27,
    'vinegar': 32,
    'sauce': 33,
    'coffee': 45,
    'tea': 37,
    'cereal': 50,
    'oats': 36,
    'biscuit': 38,
    'jam': 35,
    'honey': 34,
    'soap': 39,
    'shampoo': 42,
    'conditioner': 40,
    'facewash': 41,
    'tissue': 44,
    'perfume': 43,
    'toothpaste': 46,
    'toothbrush': 47
}

# Cumulative summary
cumulative_summary = []

def find_product_location(product):
    product = product.strip().lower()
    return products.get(product, None)

@socketio.on('connect')
def greet_user():
    global cumulative_summary
    cumulative_summary = []  # Reset cumulative summary
    emit('response', {'response': 'Hello, How can I help you?', 'summary': ''})

@socketio.on('new_chat')
def handle_new_chat():
    global cumulative_summary
    cumulative_summary = []  # Reset cumulative summary
    emit('response', {'response': 'Hello, How can I help you?', 'summary': ''})

@socketio.on('message')
def handle_message(data):
    global cumulative_summary
    user_input = data['message']
    doc = nlp(user_input)
    product_list = [token.text.lower() for token in doc if token.pos_ == 'NOUN']
    response_messages = []

    for product in product_list:
        shelf = find_product_location(product)
        if shelf:
            response_messages.append(f"{product.capitalize()} is on shelf {shelf}.")
            cumulative_summary.append(f"{product.capitalize()}: Shelf {shelf}")
        else:
            response_messages.append(f"Sorry, {product} is not found.")
            cumulative_summary.append(f"{product.capitalize()}: Not Found")

    response = " ".join(response_messages)
    summary_response = "\n".join(cumulative_summary)

    emit('response', {'response': response, 'summary': summary_response})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    html = render_template('index.html', summary=request.form['summary'])
    options = {
        'page-size': 'A4',
        'encoding': 'UTF-8',
        'no-outline': None,
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'zoom': '1.5',  # Increase font size
    }
    pdf = pdfkit.from_string(html, False, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=shelf_numbers.pdf'
    return response

if __name__ == '__main__':
    socketio.run(app, debug=True)
