# Krushi Sakha 
-Smarter eyes for healthier crops. 
🌿 Krushi Sakha

Seeing crop stress the way a field expert would.

A yellow leaf could mean disease, pests, hunger, or thirst, and a photo alone can't tell you which. KisanLens reads the crop photo together with field conditions (rainfall, humidity, farmer's observations) before giving an answer. When it isn't sure, it says so and shows an expert's contact number instead of guessing.

Features
Combines photo + field context, so the same leaf can lead to different results (e.g. yellowing with a dry spell points to water stress, not nutrient deficiency)
Explains its reasoning in plain language
Flags uncertain cases and shows an expert's tap-to-call contact
Covers healthy, fungal disease, nutrient deficiency, water stress, pest damage, and ambiguous cases
7 crops: tomato, potato, chili, brinjal, onion, mango, banana
English, Hindi and Marathi
No yield-loss claims, only a diagnosis and a next step
Files
kisanlens.html: browser version, just open it
kisanlens_html_python.py: Python (Flask) version
Run

Browser: double-click kisanlens.html

Python:

bash
pip install flask pillow
python kisanlens_html_python.py

Then open http://localhost:5000

Tech stack

HTML5, CSS3, JavaScript (Canvas API), Python (Flask, Pillow)

Limitations
Uses a rule-based scoring engine, not a trained deep-learning model
Sample leaves are illustrative; not yet validated on large real field datasets
Expert contact is a placeholder
Guidance only, confirm with a local expert for costly decisions
TEAM :
MEMBER 1:SHUBHA KULKARNI
MEMBER 2:ISHWARI SHETE
MEMBER 3:DURVA SHINDE
MEMBER 4:SHRADHA PHULARI

