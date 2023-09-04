from flask import Flask, render_template, request, jsonify
import psycopg2
from dbInfo import db_host, db_name, db_user, db_password

app = Flask(__name__)

# Initialize the database connection and cursor
db_conn = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password
)
cursor = db_conn.cursor()

# Create a route to serve the game page
@app.route('/')
def index():
    return render_template('game.html')

# Create a route to receive and store game scores
@app.route('/submit_score', methods=['POST'])
def submit_score():
    username = request.form.get('username')
    score = int(request.form.get('score'))

    # Insert the score into the database
    cursor.execute("INSERT INTO high_scores (username, score) VALUES (%s, %s)", (username, score))
    db_conn.commit()

    # return jsonify(success=True)

# Create a route to retrieve the latest 10 games
@app.route('/latest_scores')
def latest_scores():
    # Retrieve the latest 10 scores from the database
    cursor.execute("SELECT username, score FROM high_scores ORDER BY score DESC LIMIT 10")
    scores = cursor.fetchall()

    # Convert the result into a list of dictionaries
    score_data = [{'username': row[0], 'score': row[1]} for row in scores]

    return jsonify(score_data)

if __name__ == '__main__':
    app.run(debug=True)
