import subprocess

p = "C:\Users\intern.it-izaan\Desktop\Reception System\CSAPL_Reception_Backend\crop-cv2.py"
subprocess.Popen(f'python {p}', creationflags=subprocess.CREATE_NEW_PROCESS_GROUP, close_fds=True)