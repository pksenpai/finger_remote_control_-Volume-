# os: Windows mode

import cv2
import mediapipe as mp
import math
import sounddevice as sd
from comtypes import CLSCTX_ALL, POINTER, cast # os: Windows mode
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume # os: Windows mode
from pyautogui import press
import os


def calculate_distance(point1, point2):
    """ Calculate the distance between index finger & thumb
    (Using Euclidean distance formula) """
    x1, y1 = point1
    x2, y2 = point2
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def set_system_volume(volume):
    """ connect to kernel for change volume [Windows] """
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume_object = cast(interface, POINTER(IAudioEndpointVolume))
    if volume == None:
        pass
    else:
        volume_object.SetMasterVolumeLevelScalar(volume, None)

cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands()

# Settings:
max_distance = 100  # Maximum distance (100% opening between fingers)
threshold = 15  # Limit for detecting finger sticking
min_volume = 0
max_volume = 1
rep_blocker = False # Just a flag for click!
debug = True # Show the Camera-Webcam for DEBUG
pouse_mode = True # If the volume was 0%(mute), pause the video or music in progress...


while True:
    success, img = cap.read()
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    
    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(img, hand, mpHands.HAND_CONNECTIONS)
            
            for idx, landmark in enumerate(hand.landmark):
                if idx == 4:  # thumb finger
                    thumb_x, thumb_y = int(landmark.x * img.shape[1]), int(landmark.y * img.shape[0])
                elif idx == 8:  # index finger
                    index_x, index_y = int(landmark.x * img.shape[1]), int(landmark.y * img.shape[0])
            
            # Distance calculation and percentage display
            distance = calculate_distance((thumb_x, thumb_y), (index_x, index_y))
            if max_distance is None:
                max_distance = distance
            if distance < threshold:
                percentage = 0
            else:
                percentage = int((distance / max_distance) * 100)
                if percentage > 100:
                    percentage = 100

            # DEBUG MODE --------------------------------------------------------
            # Connect the index & thumb points!
            cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 0), 2) if debug else None
            # -------------------------------------------------------------------
            
            # POUSE MODE -------------------------------------------------------
            if pouse_mode:
                # If the volume was 0%(mute), pause the video or music in progress...
                if percentage == 0:
                    if rep_blocker == False:
                        press('space')
                        rep_blocker = True
                else:
                    if rep_blocker == True:
                        press('space')
                        rep_blocker = False
            # -------------------------------------------------------------------
            
            volume = (percentage / 100) * (max_volume - min_volume) + min_volume
            set_system_volume(volume)
            
            # DEBUG MODE --------------------------------------------------------
            # Display the volume percentage next to the hand!
            cv2.putText(img, f"{percentage}%", (thumb_x, thumb_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2) if debug else None
            # -------------------------------------------------------------------
    
    if debug:
        cv2.imshow("Finger Picker", img)
        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()