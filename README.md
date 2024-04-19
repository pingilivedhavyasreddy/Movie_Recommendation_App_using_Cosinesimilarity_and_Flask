# Movie_Recommendation_App_using_Cosinesimilarity_and_Flask
This is a Flask web application that provides movie recommendations based on user input. It utilizes a content-based recommendation algorithm to suggest movies similar to the ones entered by the user. Additionally, the application allows users to register, log in, and contact the administrators.

Features
User Authentication: Users can register, log in, and log out securely.
Movie Recommendations: Enter a movie name, and the system suggests similar movies.
Recently Released Movies: View a list of recently released movies with their details.
Top Rated Movies: Explore a collection of top-rated movies.
Trending Movies: See what movies are currently trending.
Contact Form: Users can submit messages through the contact form.
Admin Panel: Administrators can view user details and contact messages.

Setup

1. Clone the repository:
git clone https://github.com/pingilivedhavyasreddy/Movie_recommendation_app_with_cosine_similarity_and_flask.git

2. Install dependencies:
pip install -r requirements.txt

3. Set up the database:
python
>>> from app import db
>>> db.create_all()
>>> exit()

4. Run the application:
python app.py

5. Access the application in your web browser at http://localhost:5000.


Technologies Used
Flask
SQLAlchemy
WTForms
scikit-learn (for recommendation algorithm)
pandas
Bootstrap (for frontend)
The Movie Database (TMDb) API

Screenshots:
![Screenshot 2024-04-17 202741](https://github.com/pingilivedhavyasreddy/Movie_recommendation_app_with_cosine_similarity_and_flask/assets/109604239/0b8416f3-f42f-4d29-89bf-13e2d2fe7120)
![Screenshot 2024-04-17 203227](https://github.com/pingilivedhavyasreddy/Movie_recommendation_app_with_cosine_similarity_and_flask/assets/109604239/3ed5c55f-7b6f-4b77-a571-3493e5c8be28)
![Screenshot 2024-04-17 202448](https://github.com/pingilivedhavyasreddy/Movie_recommendation_app_with_cosine_similarity_and_flask/assets/109604239/0d2c47ea-92c8-47c6-96a3-583f3ff1121f)
![Screenshot 2024-04-17 202523](https://github.com/pingilivedhavyasreddy/Movie_recommendation_app_with_cosine_similarity_and_flask/assets/109604239/c5450635-1bac-4104-b4da-13abcc95ff75)
![Screenshot 2024-04-17 202553](https://github.com/pingilivedhavyasreddy/Movie_recommendation_app_with_cosine_similarity_and_flask/assets/109604239/e780044f-d13a-4749-b1f7-e101bf02e89d)
![Screenshot 2024-04-17 202724](https://github.com/pingilivedhavyasreddy/Movie_recommendation_app_with_cosine_similarity_and_flask/assets/109604239/f798a1bd-275a-42b9-bc0c-822b1b6b6e9e)

