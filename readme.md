## Gesture Volume Control System
This project is a Django-based web application that allows users to control system volume using hand gestures detected through a webcam.

## Features

* Real-time hand gesture detection
* Control system volume using fingers
* Visual feedback using camera
* User-friendly interface

##  Technologies Used

* Python
* Django
* OpenCV
* MediaPipe
* NumPy

##  How It Works

* The webcam captures hand movements
* MediaPipe detects hand landmarks
* Distance between fingers is calculated
* Based on the distance, system volume is increased or decreased

##  How to Run the Project

1. Clone the repository
2. Create a virtual environment
3. Activate the environment
4. Install dependencies:
   pip install -r requirements.txt
5. Run the server:
   python manage.py runserver
6. Open browser and run the project

##  Project Structure

* gestureproject/ → main Django project
* volumeapp/ → core application logic
* manage.py → Django entry point
* requirements.txt → dependencies

## Future Improvements

* Add GUI enhancements
* Improve gesture accuracy
* Add more gesture controls

## Author
Pallavi Patidar
