**Face Recognition Based Attendance System**



**About the Project**



The Face Recognition Based Attendance System is a Python-based application that uses face recognition technology to automatically record student attendance.



The system captures student face images, trains a face recognition model, recognizes registered students through a webcam, and records attendance with date and time.



**Technologies Used**



\- Python

\- OpenCV

\- Tkinter

\- NumPy

\- Pandas

\- Pillow

\- CSV



**Features**



\- Student registration

\- Face image capture

\- Face recognition

\- Automatic attendance marking

\- Date and time recording

\- Student details management

\- Password-protected model training

\- Attendance records stored in CSV format



**How It Works**



1\. Enter the student's ID and name.

2\. Capture face images using the webcam.

3\. Train the face recognition model.

4\. Start attendance using the webcam.

5\. The system recognizes registered students.

6\. Attendance is recorded with ID, name, date, and time.



**Project Structure**



Face-Recognition-Attendance-System/

│

├── main.py

├── haarcascade\_frontalface\_default.xml

├── requirements.txt

├── .gitignore

│

├── StudentDetails/

├── TrainingImage/

├── TrainingImageLabel/

└── Attendance/



**Installation and Run**

From PowerShell, run these commands in the project folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```



**Requirements**



\- Python

\- Webcam

\- Required Python packages



**Project Purpose**



This project demonstrates how computer vision and face recognition can be used to automate attendance management and reduce manual attendance work.



Author



Nithiyapriya

