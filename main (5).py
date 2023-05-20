import numpy as np
import cv2
import pygame

cap = cv2.VideoCapture(0)  # Mettre votre video ou webcam!

kernel_blur = 39
seuil = 15
surface = 20000
ret, originale = cap.read()
if ret is False:
    quit()

originale = cv2.cvtColor(originale, cv2.COLOR_BGR2GRAY)
originale = cv2.GaussianBlur(originale, (kernel_blur, kernel_blur), 0)
kernel_dilate = np.ones((5, 5), np.uint8)

pygame.mixer.init()

alarme_active = False
alarme_temps = 0

while True:
    ret, frame = cap.read()
    if ret is False:
        quit()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.GaussianBlur(gray, (kernel_blur, kernel_blur), 0)
    mask = cv2.absdiff(originale, gray_blur)
    mask = cv2.threshold(mask, seuil, 255, cv2.THRESH_BINARY)[1]
    mask = cv2.dilate(mask, kernel_dilate, iterations=3)
    contours, nada = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    frame_contour = frame.copy()

    for c in contours:
        if cv2.contourArea(c) < surface:
            continue

        cv2.drawContours(frame_contour, [c], 0, (0, 255, 0), 2)
        x, y, w, h = cv2.boundingRect(c)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        if not alarme_active:
            alarme_active = True
            cv2.putText(frame, " Entrez le code ! ", (x, y - 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
            sound = pygame.mixer.Sound("assets/audio/alarme.ogg")
            sound.play()

    originale = gray_blur

    cv2.putText(frame, "[o|l]seuil: {:d}  [p|m]blur: {:d}  [i|k]surface: {:d}".format(seuil, kernel_blur, surface),
                (10, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 255), 2)
    cv2.imshow("frame", frame)

    if alarme_active:
        cv2.putText(frame, "Intrus Détécté", (10, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
        alarme_temps += 1
        if alarme_temps > 50:
            alarme_active = False
            alarme_temps = 0
            sound.stop()

    key = cv2.waitKey(30) & 0xFF
    k = cv2.waitKey(33)

    if key == ord('q'):
        alarme_temps = 0
        alarme_active = False
        sound.stop()
        break
    elif key == ord(' ') and alarme_active:
        alarme_temps = 0
        alarme_active = False
        sound.stop()
    elif key == ord('p'):
        kernel_blur = min(43, kernel_blur + 2)
    elif key == ord('m'):
        kernel_blur = max(1, kernel_blur - 2)
    elif key == ord('o'):
        seuil = min(255, seuil + 1)
    elif key == ord('l'):
        seuil = max(1, seuil - 1)
    elif key == ord('i'):
        surface += 1000
    elif key == ord('k'):
        surface = max(1000, surface - 1000)

cap.release()
cv2.destroyAllWindows()
