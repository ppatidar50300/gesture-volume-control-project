import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


import mediapipe as mp
import math
import numpy as np
import os
from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse

# Volume Control (Windows)
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize Volume
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
distance_list = []
volume_list = []
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
minVol, maxVol = volume.GetVolumeRange()[:2]

# MediaPipe Setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands_detector = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = None
camera_active = False

gesture_data = {
    "distance": 0,
    "gesture": "None",
    "volume": 0,
    "fps": 0,
    "hands": 0,
    "resolution": "0x0",
    "detection_conf": 0.7,
    "tracking_conf": 0.7
}


def final_page(request):
    return render(request, "final.html")


def start_camera(request):
    global cap, camera_active
    cap = cv2.VideoCapture(0)
    camera_active = True
    return JsonResponse({"status": "started"})


def stop_camera(request):
    global cap, camera_active
    camera_active = False
    if cap:
        cap.release()
    return JsonResponse({"status": "stopped"})


def capture_frame(request):
    global cap
    if cap:
        ret, frame = cap.read()
        if ret:
            if not os.path.exists("captures"):
                os.makedirs("captures")
            cv2.imwrite("captures/capture.jpg", frame)
            return JsonResponse({"status": "captured"})
    return JsonResponse({"status": "failed"})

def generate_frames():
    global cap, gesture_data

    prev_time = 0

    # Ensure camera is opened properly (Windows fix included)
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:
        success, img = cap.read()
        if not success:
            print("Frame not captured")
            break

        h, w, _ = img.shape
        gesture_data["resolution"] = f"{w}x{h}"

        # Convert to RGB for Mediapipe (DO NOT overwrite original img)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands_detector.process(img_rgb)

        lmList = []

        if results.multi_hand_landmarks:
            gesture_data["hands"] = len(results.multi_hand_landmarks)

            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    img, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )

                for id, lm in enumerate(hand_landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append((id, cx, cy))
        else:
            gesture_data["hands"] = 0

        # -------- Distance + Gesture + Volume --------
        if len(lmList) > 8:   # Safety check

            x1, y1 = lmList[4][1], lmList[4][2]   # Thumb tip
            x2, y2 = lmList[8][1], lmList[8][2]   # Index tip

            cv2.circle(img, (x1, y1), 8, (255, 0, 255), -1)
            cv2.circle(img, (x2, y2), 8, (255, 0, 255), -1)
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

            # length = int(math.hypot(x2 - x1, y2 - y1))
            # gesture_data["distance"] = length
                 # Pixel distance between thumb & index
            pixel_distance = math.hypot(x2 - x1, y2 - y1)

# -------- Hand Reference Scaling --------
# Wrist (0) and Index MCP (5)
            wrist = results.multi_hand_landmarks[0].landmark[0]
            index_mcp = results.multi_hand_landmarks[0].landmark[5]

            w_x, w_y = int(wrist.x * w), int(wrist.y * h)
            i_x, i_y = int(index_mcp.x * w), int(index_mcp.y * h)

            reference_pixel = math.hypot(i_x - w_x, i_y - w_y)

            real_reference_mm = 70   # Approx average wrist→index MCP length

            if reference_pixel != 0:
                   mm_per_pixel = real_reference_mm / reference_pixel
                   distance_mm = pixel_distance * mm_per_pixel
            else:
                 distance_mm = 0

            gesture_data["distance"] = round(distance_mm, 2)

# Use pixel_distance for gesture logic & volume (important!)
            length = pixel_distance
            # Gesture Classification
            if length < 40:
                gesture = "Closed"
            elif length < 100:
                gesture = "Pinch"
            else:
                gesture = "Open"

            gesture_data["gesture"] = gesture

            # Volume Mapping (SAFE)
            try:
                vol = np.interp(length, [20, 200], [minVol, maxVol])
                volume.SetMasterVolumeLevel(vol, None)

                vol_percent = int(np.interp(length, [20, 200], [0, 100]))
                gesture_data["volume"] = vol_percent
                distance_list.append(length)
                volume_list.append(vol_percent)

                if len(distance_list) > 40:
                    distance_list.pop(0)
                    volume_list.pop(0)
                plt.figure(figsize=(4,3))
                plt.clf()
                plt.plot(distance_list, volume_list)

                plt.xlabel("Finger Distance")
                plt.ylabel("Volume %")
                plt.title("Distance vs Volume")

                # plt.savefig("volumeapp/static/graph.png")
            except:
                gesture_data["volume"] = 0

            cv2.putText(img, gesture, (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 3)

        else:
            gesture_data["distance"] = 0
            gesture_data["gesture"] = "None"

        # -------- FPS Calculation --------
        curr_time = cv2.getTickCount() / cv2.getTickFrequency()
        fps = int(1 / (curr_time - prev_time)) if prev_time != 0 else 0
        prev_time = curr_time
        gesture_data["fps"] = fps

        cv2.putText(img, f"FPS: {fps}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 0, 0), 2)
        cv2.putText(img,
            f"Distance: {gesture_data['distance']} mm",
            (50, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0),
            2)
        # Encode frame properly
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
       # Normalize FPS
        normalized_fps = min(fps / 30, 1)

        detection_conf = round(0.5 + (normalized_fps * 0.4), 2)
        tracking_conf = round(0.6 + (normalized_fps * 0.3), 2)

        gesture_data["detection_conf"] = detection_conf
        gesture_data["tracking_conf"] = tracking_conf
        
def video_feed(request):
    return StreamingHttpResponse(generate_frames(),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def get_gesture_data(request):
    return JsonResponse(gesture_data)

