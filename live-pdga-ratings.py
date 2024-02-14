from flask import Flask, request, render_template
import src.models.Round
from src.Rating import main
# Create a Flask app object
app = Flask(__name__)

# Define a route for the home page
@app.route('/')
def home():
    # Render a template with a form for user input
    return render_template('home.html')

@app.route('/result', methods=['POST'])
def result():
    # Get the user input from the form
    pdga_number = request.form['pdga_number']
    # Do something with the user input, such as validating it or querying a database
    # For simplicity, we'll just print it to the console
    resultArray = main(pdga_number)
    
    # Render a template with the user input and some message
    return render_template('result.html', pdga_number=pdga_number, current_rating = resultArray[0], calculated_rating = resultArray[1])


# Run the app in debug mode
if __name__ == '__main__':
    app.run(debug=True)