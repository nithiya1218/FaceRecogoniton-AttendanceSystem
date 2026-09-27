############################################# IMPORTING ################################################
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mess
import tkinter.simpledialog as tsd
import cv2
import os
import csv
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

############################################# CONFIGURATION ################################################

BASE_DIR = Path(__file__).resolve().parent

CONFIG = {
    "CASCADE_PATH": str(BASE_DIR / "haarcascade_frontalface_default.xml"),
    "STUDENT_DIR": str(BASE_DIR / "StudentDetails"),
    "TRAINING_DIR": str(BASE_DIR / "TrainingImage"),
    "MODEL_DIR": str(BASE_DIR / "TrainingImageLabel"),
    "ATTENDANCE_DIR": str(BASE_DIR / "Attendance"),
    "MODEL_FILE": str(BASE_DIR / "TrainingImageLabel" / "Trainer.yml"),
    "STUDENT_CSV": str(BASE_DIR / "StudentDetails" / "StudentDetails.csv"),
    "PASSWORD_FILE": str(BASE_DIR / "TrainingImageLabel" / "psd.txt"),
    "MAX_SAMPLES": 100,
    "CONFIDENCE_THRESHOLD": 50
}

############################################# FUNCTIONS ################################################

def assure_path_exists(path):
    """Create directory if it doesn't exist"""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create path {path}: {str(e)}")
        return False

def tick():
    """Update clock every 200ms"""
    try:
        time_string = time.strftime('%H:%M:%S')
        clock.config(text=time_string)
        clock.after(200, tick)
    except:
        pass

def contact():
    """Show contact information"""
    mess.showinfo('Contact Us', "Please contact us on:\nEmail: admin@attendancesystem.com\nPhone: +1-800-123-4567")

def ask_password(title, prompt):
    """Ask for a password, treating a dialog closed before appearing as cancellation."""
    try:
        return tsd.askstring(title, prompt, show='*', parent=window)
    except tk.TclError as exc:
        if "deleted before its visibility changed" in str(exc):
            logger.debug("Password prompt closed before it appeared")
            return None
        raise

def check_haarcascadefile():
    """Check if Haar Cascade file exists"""
    if not os.path.isfile(CONFIG["CASCADE_PATH"]):
        logger.error(f"Haar Cascade file missing: {CONFIG['CASCADE_PATH']}")
        mess.showerror('File Missing', f'Haar Cascade file missing!\n\nPlease download it from:\nhttps://github.com/opencv/opencv/tree/master/data/haarcascades')
        return False
    return True

def save_pass():
    """Save new password"""
    assure_path_exists(CONFIG["MODEL_DIR"])
    
    try:
        password_file = CONFIG["PASSWORD_FILE"]
        
        if os.path.isfile(password_file):
            with open(password_file, "r") as tf:
                key = tf.read()
        else:
            new_pas = ask_password('Setup Password', 'Please enter a new password below')
            if new_pas is None:
                mess.showerror('Error', 'Password not set! Please try again')
                return
            
            with open(password_file, "w") as tf:
                tf.write(new_pas)
            mess.showinfo('Success', 'Password registered successfully!')
            master.destroy()
            return
        
        op = old.get()
        newp = new.get()
        nnewp = nnew.get()
        
        if op != key:
            mess.showerror('Error', 'Incorrect old password')
            return
        
        if newp != nnewp:
            mess.showerror('Error', 'New passwords do not match')
            return
        
        if len(newp) < 3:
            mess.showerror('Error', 'Password must be at least 3 characters')
            return
        
        with open(password_file, "w") as txf:
            txf.write(newp)
        
        mess.showinfo('Success', 'Password changed successfully!')
        master.destroy()
        
    except Exception as e:
        logger.error(f"Error in save_pass: {str(e)}")
        mess.showerror('Error', f'An error occurred: {str(e)}')

def change_pass():
    """Open password change window"""
    global master
    master = tk.Tk()
    master.geometry("400x180")
    master.resizable(False, False)
    master.title("Change Password")
    master.configure(background="white")
    
    lbl4 = tk.Label(master, text='Enter Old Password', bg='white', font=('times', 12, 'bold'))
    lbl4.place(x=10, y=10)
    global old
    old = tk.Entry(master, width=25, fg="black", relief='solid', font=('times', 12, 'bold'), show='*')
    old.place(x=180, y=10)
    
    lbl5 = tk.Label(master, text='Enter New Password', bg='white', font=('times', 12, 'bold'))
    lbl5.place(x=10, y=45)
    global new
    new = tk.Entry(master, width=25, fg="black", relief='solid', font=('times', 12, 'bold'), show='*')
    new.place(x=180, y=45)
    
    lbl6 = tk.Label(master, text='Confirm New Password', bg='white', font=('times', 12, 'bold'))
    lbl6.place(x=10, y=80)
    global nnew
    nnew = tk.Entry(master, width=25, fg="black", relief='solid', font=('times', 12, 'bold'), show='*')
    nnew.place(x=180, y=80)
    
    cancel = tk.Button(master, text="Cancel", command=master.destroy, fg="black", bg="red", height=1, width=25, activebackground="white", font=('times', 10, 'bold'))
    cancel.place(x=200, y=130)
    
    save1 = tk.Button(master, text="Save", command=save_pass, fg="black", bg="#3ece48", height=1, width=25, activebackground="white", font=('times', 10, 'bold'))
    save1.place(x=10, y=130)
    
    master.mainloop()

def psw():
    """Password protected training"""
    assure_path_exists(CONFIG["MODEL_DIR"])
    password_file = CONFIG["PASSWORD_FILE"]
    
    try:
        if os.path.isfile(password_file):
            with open(password_file, "r") as tf:
                key = tf.read()
        else:
            new_pas = ask_password('Setup Password', 'Please enter a new password below')
            if new_pas is None:
                mess.showerror('Error', 'Password not set! Please try again')
                return
            
            with open(password_file, "w") as tf:
                tf.write(new_pas)
            mess.showinfo('Success', 'Password registered successfully!')
            TrainImages()
            return
        
        password = ask_password('Password', 'Enter Password to train model')
        if password is None:
            return
        
        if password == key:
            TrainImages()
        else:
            mess.showerror('Error', 'Incorrect password')
    
    except Exception as e:
        logger.error(f"Error in psw: {str(e)}")
        mess.showerror('Error', f'An error occurred: {str(e)}')

def clear():
    """Clear ID field"""
    txt.delete(0, 'end')
    message1.configure(text="1) Take Images  >>>  2) Save Profile")

def clear2():
    """Clear Name field"""
    txt2.delete(0, 'end')
    message1.configure(text="1) Take Images  >>>  2) Save Profile")

#######################################################################################
# TAKE IMAGES
#######################################################################################

def TakeImages():
    """Capture training images from webcam"""
    if not check_haarcascadefile():
        return
    
    assure_path_exists(CONFIG["STUDENT_DIR"])
    assure_path_exists(CONFIG["TRAINING_DIR"])
    
    student_id = txt.get().strip()
    name = txt2.get().strip()
    
    # Validation
    if not student_id or not name:
        mess.showerror("Error", "Please enter both ID and Name")
        return
    
    if not student_id.isdigit():
        mess.showerror("Error", "Student ID must be numeric only")
        return
    
    if not all(c.isalpha() or c.isspace() for c in name):
        mess.showerror("Error", "Name must contain only letters and spaces")
        return
    
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            mess.showerror("Error", "Cannot access webcam")
            return
        
        detector = cv2.CascadeClassifier(CONFIG["CASCADE_PATH"])
        if detector.empty():
            mess.showerror("Error", "Failed to load face detector")
            cam.release()
            return
        
        sample_num = 0
        message1.configure(text=f"Capturing images for {name}... Press Q to quit")
        window.update()
        
        while True:
            ret, img = cam.read()
            if not ret:
                mess.showerror("Error", "Failed to capture frame")
                break
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5, minSize=(30, 30))
            
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                sample_num += 1
                
                # FIX: Correct path format
                filename = f"{CONFIG['TRAINING_DIR']}/{name}.{student_id}.{sample_num}.jpg"
                cv2.imwrite(filename, gray[y:y + h, x:x + w])
                
                cv2.putText(img, f"Samples: {sample_num}/{CONFIG['MAX_SAMPLES']}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Taking Images - Press Q to quit', img)
            
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break
            elif sample_num >= CONFIG['MAX_SAMPLES']:
                break
        
        cam.release()
        cv2.destroyAllWindows()
        
        if sample_num > 0:
            _save_student_details(student_id, name)
            message1.configure(text=f"✓ Captured {sample_num} images for {name}")
            logger.info(f"Captured {sample_num} images for {name} (ID: {student_id})")
            mess.showinfo("Success", f"Successfully captured {sample_num} images!\n\nNow click 'Save Profile' to train")
            txt.delete(0, 'end')
            txt2.delete(0, 'end')
            _update_registration_count()
        else:
            mess.showwarning("Warning", "No images captured")
            message1.configure(text="Failed to capture images")
    
    except Exception as e:
        logger.error(f"Error in TakeImages: {str(e)}")
        mess.showerror("Error", f"An error occurred:\n{str(e)}")

def _save_student_details(student_id, name):
    """Save student details to CSV"""
    try:
        csv_path = CONFIG["STUDENT_CSV"]
        file_exists = os.path.isfile(csv_path)
        
        with open(csv_path, 'a+', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if not file_exists:
                writer.writerow(["SERIAL NO.", "", "ID", "", "NAME"])
            writer.writerow(["", "", student_id, "", name])
        
        logger.info(f"Saved student: {name} (ID: {student_id})")
    
    except Exception as e:
        logger.error(f"Error saving student details: {str(e)}")
        mess.showerror("Error", f"Failed to save student details")

########################################################################################
# TRAIN IMAGES
########################################################################################

def TrainImages():
    """Train the face recognizer model"""
    try:
        check_haarcascadefile()
        assure_path_exists(CONFIG["MODEL_DIR"])
        
        faces, IDs = getImagesAndLabels(CONFIG["TRAINING_DIR"])
        
        if len(faces) == 0:
            mess.showerror('Error', 'No training images found!\n\n1. Click "Take Images" first\n2. Enter ID and Name\n3. Position face in camera')
            return
        
        message1.configure(text=f"Training model with {len(faces)} images...")
        window.update()
        
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(IDs))
        recognizer.save(CONFIG["MODEL_FILE"])
        
        message1.configure(text="✓ Profile Saved Successfully")
        message.configure(text=f'Total Students: {len(set(IDs))} | Total Images: {len(faces)}')
        
        logger.info(f"Model trained with {len(faces)} images from {len(set(IDs))} students")
        mess.showinfo("Success", f"Model trained successfully!\n\nStudents: {len(set(IDs))}\nImages: {len(faces)}")
    
    except Exception as e:
        logger.error(f"Error in TrainImages: {str(e)}")
        mess.showerror('Error', f'Training failed:\n{str(e)}')

############################################################################################
# GET IMAGES AND LABELS
############################################################################################

def getImagesAndLabels(path):
    """Extract images and labels from training directory"""
    try:
        if not os.path.exists(path):
            logger.error(f"Training directory not found: {path}")
            return [], []
        
        imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith('.jpg')]
        
        if not imagePaths:
            logger.error("No JPG images found in training directory")
            return [], []
        
        faces = []
        Ids = []
        
        for imagePath in imagePaths:
            try:
                filename = os.path.basename(imagePath)
                parts = filename.split(".")
                
                if len(parts) < 3:
                    logger.warning(f"Invalid filename format: {filename}")
                    continue
                
                try:
                    ID = int(parts[1])
                except ValueError:
                    logger.warning(f"Cannot parse ID from: {filename}")
                    continue
                
                pilImage = Image.open(imagePath).convert('L')
                imageNp = np.array(pilImage, 'uint8')
                
                faces.append(imageNp)
                Ids.append(ID)
            
            except Exception as e:
                logger.warning(f"Error processing image {imagePath}: {str(e)}")
                continue
        
        logger.info(f"Loaded {len(faces)} images from {len(set(Ids))} students")
        return faces, Ids
    
    except Exception as e:
        logger.error(f"Error in getImagesAndLabels: {str(e)}")
        return [], []

###########################################################################################
# TRACK IMAGES
###########################################################################################

def TrackImages():
    """Track faces and mark attendance"""
    if not check_haarcascadefile():
        return
    
    assure_path_exists(CONFIG["ATTENDANCE_DIR"])
    assure_path_exists(CONFIG["STUDENT_DIR"])
    
    # Clear treeview
    for k in tv.get_children():
        tv.delete(k)
    
    try:
        # Check if model exists
        if not os.path.isfile(CONFIG["MODEL_FILE"]):
            mess.showerror('Error', 'Model not trained!\n\n1. Click "Take Images"\n2. Click "Save Profile"\n3. Then "Take Attendance"')
            return
        
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(CONFIG["MODEL_FILE"])
        
        faceCascade = cv2.CascadeClassifier(CONFIG["CASCADE_PATH"])
        if faceCascade.empty():
            mess.showerror("Error", "Failed to load face cascade")
            return
        
        # Load student details
        if not os.path.isfile(CONFIG["STUDENT_CSV"]):
            mess.showerror('Error', 'Student details file not found')
            return
        
        df = pd.read_csv(CONFIG["STUDENT_CSV"], dtype={"ID": "string"})
        
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            mess.showerror("Error", "Cannot access webcam")
            return
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        attendance_records = []
        recognized_students = set()
        
        message1.configure(text="Taking Attendance... Press Q to quit")
        window.update()
        
        while True:
            ret, im = cam.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                try:
                    serial, conf = recognizer.predict(gray[y:y + h, x:x + w])
                    
                    if conf < CONFIG["CONFIDENCE_THRESHOLD"]:
                        # Find student by ID
                        student_row = df[pd.to_numeric(df['ID'], errors='coerce') == serial]
                        
                        if not student_row.empty:
                            name = student_row['NAME'].values[0]
                            student_id = str(student_row['ID'].iloc[0])
                            
                            if (student_id, name) not in recognized_students:
                                ts = time.time()
                                date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                
                                attendance_records.append([student_id, name, date, timeStamp])
                                recognized_students.add((student_id, name))
                            
                            cv2.putText(im, f"{name} ({conf:.0f})", (x, y - 10), font, 1, (0, 255, 0), 2)
                        else:
                            cv2.putText(im, "Unknown", (x, y - 10), font, 1, (0, 0, 255), 2)
                    else:
                        cv2.putText(im, f"Unknown ({conf:.0f})", (x, y - 10), font, 1, (0, 0, 255), 2)
                
                except Exception as e:
                    logger.error(f"Prediction error: {str(e)}")
            
            cv2.imshow('Taking Attendance - Press Q to quit', im)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cam.release()
        cv2.destroyAllWindows()
        
        # Save attendance records
        if attendance_records:
            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
            attendance_file = f"{CONFIG['ATTENDANCE_DIR']}/Attendance_{date}.csv"
            
            file_exists = os.path.isfile(attendance_file)
            
            with open(attendance_file, 'a+', newline='', encoding='utf-8') as csvFile:
                writer = csv.writer(csvFile)
                if not file_exists:
                    writer.writerow(['ID', '', 'NAME', '', 'DATE', '', 'TIME'])
                
                for record in attendance_records:
                    writer.writerow([record[0], '', record[1], '', record[2], '', record[3]])
            
            # Display records in treeview
            with open(attendance_file, 'r', encoding='utf-8') as csvFile:
                reader = csv.reader(csvFile)
                for i, lines in enumerate(reader):
                    if i > 0:  # Skip header
                        if len(lines) >= 7:
                            tv.insert('', 0, text=lines[0], values=(lines[2], lines[4], lines[6]))
            
            message1.configure(text=f"✓ Recorded attendance for {len(recognized_students)} students")
            logger.info(f"Attendance recorded for {len(recognized_students)} students")
            mess.showinfo("Success", f"Attendance recorded for {len(recognized_students)} students")
        else:
            message1.configure(text="No students recognized")
            mess.showwarning("Info", "No students recognized in this session")
    
    except Exception as e:
        logger.error(f"Error in TrackImages: {str(e)}")
        mess.showerror("Error", f"An error occurred:\n{str(e)}")

def _update_registration_count():
    """Update student registration count"""
    try:
        if os.path.isfile(CONFIG["STUDENT_CSV"]):
            df = pd.read_csv(CONFIG["STUDENT_CSV"])
            count = len(df)
            message.configure(text=f'Total Registrations till now: {count}')
    except:
        pass

######################################## USED STUFFS ############################################

global key
key = ''

ts = time.time()
date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
day, month, year = date.split("-")

mont = {
    '01': 'January', '02': 'February', '03': 'March', '04': 'April',
    '05': 'May', '06': 'June', '07': 'July', '08': 'August',
    '09': 'September', '10': 'October', '11': 'November', '12': 'December'
}

######################################## GUI FRONT-END ###########################################

window = tk.Tk()
window.geometry("1280x720")
window.resizable(True, False)
window.title("Face Recognition Attendance System")
window.configure(background='#262523')

# Frames
frame1 = tk.Frame(window, bg="#00aeff")
frame1.place(relx=0.11, rely=0.17, relwidth=0.39, relheight=0.80)

frame2 = tk.Frame(window, bg="#00aeff")
frame2.place(relx=0.51, rely=0.17, relwidth=0.38, relheight=0.80)

# Title
message3 = tk.Label(window, text="Face Recognition Based Attendance System", fg="white", bg="#262523", width=55, height=1, font=('times', 29, 'bold'))
message3.place(x=10, y=10)

# Time and Date frames
frame3 = tk.Frame(window, bg="#c4c6ce")
frame3.place(relx=0.52, rely=0.09, relwidth=0.09, relheight=0.07)

frame4 = tk.Frame(window, bg="#c4c6ce")
frame4.place(relx=0.36, rely=0.09, relwidth=0.16, relheight=0.07)

datef = tk.Label(frame4, text=day + "-" + mont[month] + "-" + year + "  |  ", fg="orange", bg="#262523", width=55, height=1, font=('times', 22, 'bold'))
datef.pack(fill='both', expand=1)

clock = tk.Label(frame3, fg="orange", bg="#262523", width=55, height=1, font=('times', 22, 'bold'))
clock.pack(fill='both', expand=1)
tick()

# Headers
head2 = tk.Label(frame2, text="For New Registrations", fg="black", bg="#3ece48", font=('times', 17, 'bold'))
head2.grid(row=0, column=0)

head1 = tk.Label(frame1, text="For Already Registered", fg="black", bg="#3ece48", font=('times', 17, 'bold'))
head1.place(x=0, y=0)

# Input labels and entries
lbl = tk.Label(frame2, text="Enter ID", width=20, height=1, fg="black", bg="#00aeff", font=('times', 17, 'bold'))
lbl.place(x=80, y=55)

txt = tk.Entry(frame2, width=32, fg="black", font=('times', 15, 'bold'))
txt.place(x=30, y=88)

lbl2 = tk.Label(frame2, text="Enter Name", width=20, fg="black", bg="#00aeff", font=('times', 17, 'bold'))
lbl2.place(x=80, y=140)

txt2 = tk.Entry(frame2, width=32, fg="black", font=('times', 15, 'bold'))
txt2.place(x=30, y=173)

# Status messages
message1 = tk.Label(frame2, text="1) Take Images  >>>  2) Save Profile", bg="#00aeff", fg="black", width=39, height=1, font=('times', 15, 'bold'))
message1.place(x=7, y=230)

message = tk.Label(frame2, text="", bg="#00aeff", fg="black", width=39, height=1, font=('times', 16, 'bold'))
message.place(x=7, y=450)

# Attendance label
lbl3 = tk.Label(frame1, text="Attendance", width=20, fg="black", bg="#00aeff", height=1, font=('times', 17, 'bold'))
lbl3.place(x=100, y=115)

# Initialize registration count
res = 0
if os.path.isfile(CONFIG["STUDENT_CSV"]):
    try:
        df = pd.read_csv(CONFIG["STUDENT_CSV"])
        res = len(df)
    except:
        res = 0

message.configure(text=f'Total Registrations till now: {res}')

# Menubar
menubar = tk.Menu(window, relief='ridge')
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label='Change Password', command=change_pass)
filemenu.add_command(label='Contact Us', command=contact)
filemenu.add_command(label='Exit', command=window.destroy)
menubar.add_cascade(label='Help', font=('times', 29, 'bold'), menu=filemenu)

# Treeview for attendance
tv = ttk.Treeview(frame1, height=13, columns=('name', 'date', 'time'))
tv.column('#0', width=82)
tv.column('name', width=130)
tv.column('date', width=133)
tv.column('time', width=133)
tv.grid(row=2, column=0, padx=(0, 0), pady=(150, 0), columnspan=4)
tv.heading('#0', text='ID')
tv.heading('name', text='NAME')
tv.heading('date', text='DATE')
tv.heading('time', text='TIME')

# Scrollbar
scroll = ttk.Scrollbar(frame1, orient='vertical', command=tv.yview)
scroll.grid(row=2, column=4, padx=(0, 100), pady=(150, 0), sticky='ns')
tv.configure(yscrollcommand=scroll.set)

# Buttons
clearButton = tk.Button(frame2, text="Clear", command=clear, fg="black", bg="#ea2a2a", width=11, activebackground="white", font=('times', 11, 'bold'))
clearButton.place(x=335, y=86)

clearButton2 = tk.Button(frame2, text="Clear", command=clear2, fg="black", bg="#ea2a2a", width=11, activebackground="white", font=('times', 11, 'bold'))
clearButton2.place(x=335, y=172)

takeImg = tk.Button(frame2, text="Take Images", command=TakeImages, fg="white", bg="blue", width=34, height=1, activebackground="white", font=('times', 15, 'bold'))
takeImg.place(x=30, y=300)

trainImg = tk.Button(frame2, text="Save Profile", command=psw, fg="white", bg="blue", width=34, height=1, activebackground="white", font=('times', 15, 'bold'))
trainImg.place(x=30, y=380)

trackImg = tk.Button(frame1, text="Take Attendance", command=TrackImages, fg="black", bg="yellow", width=35, height=1, activebackground="white", font=('times', 15, 'bold'))
trackImg.place(x=30, y=50)

quitWindow = tk.Button(frame1, text="Quit", command=window.destroy, fg="black", bg="red", width=35, height=1, activebackground="white", font=('times', 15, 'bold'))
quitWindow.place(x=30, y=450)

# Configure menu
window.configure(menu=menubar)

logger.info("Application started successfully")
window.mainloop()
logger.info("Application closed")