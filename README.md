# Calibration Test

This project is a web application designed to help users improve their calibration skills by guessing numerical ranges for various trivia questions. The correct answers are provided after submission to allow users to assess their performance.

## Features

- Presents users with 10 random trivia questions from a pool of 200 questions.
- Users input their estimated lower and upper bounds for each question.
- Displays the correct answers after submission and calculates a calibration score.

## Installation

### Prerequisites

- Python 3.6 or higher
- Git
- Node.js (optional, for front-end dependencies)

### Steps

1. **Clone the repository:**
```bash
   git clone https://github.com/yourusername/calibration-test.git
   cd calibration-test
```

2. **Set up a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Run the application:**

```bash
python app.py
```

5. **Open your browser and navigate to:**
```
    http://localhost:5000
```

### Usage

Open the application in your web browser.
Enter your estimated lower and upper bounds for each of the 10 trivia questions.
Submit your answers to see the correct answers and your calibration score.

## Next Steps for Improvement

Here are some ideas for future improvements:

1. **Enhanced User Interface:**
    *   Improve the design and responsiveness of the UI using a front-end framework like React or Vue.js.
    *   Add animations and transitions for a smoother user experience.
2. **Question Pool Expansion:**
    *   Increase the pool of trivia questions to provide more variety and reduce repetition for frequent users.
3. **User Authentication and Profiles:**
    *   Implement user authentication to allow users to create accounts and save their calibration progress.
    *   Provide a dashboard for users to track their performance over time.
4. **Statistics and Insights:**
    *   Display detailed statistics and insights about user performance, such as average score, trends, and areas for improvement.
5. **Admin Interface:**
    *   Create an admin interface for managing the pool of trivia questions, including adding, editing, and deleting questions.
6. **Internationalization:**
    *   Add support for multiple languages to make the application accessible to a wider audience.
7. **Mobile App:**
    *   Develop a mobile version of the application using a framework like React Native or Flutter.
