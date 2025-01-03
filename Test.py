import cv2
from cvzone.PoseModule import PoseDetector
import socket
cap = cv2.VideoCapture(1)

detector = PoseDetector()
posList = []

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 8193)

while True:
    success, img = cap.read()
    img = detector.findPose(img)

    lmList, bboxInfo = detector.findPosition(img)

    if bboxInfo:
        lmString = ''

        for lm in lmList:
            lmString += f'{lm[0]},{img.shape[0] - lm[1]},{lm[2]},'
        posList.append(lmString)

        # 執行均值濾波
        if len(posList) >= 5:
            avgPos = []
            for i in range(len(lmList)):
                xPos = []
                yPos = []
                zPos = []
                for j in range(len(posList) - 2, len(posList) + 3):
                    if j >= 0 and j < len(posList):
                        coords = posList[j].split(',')
                        if i * 3 + 2 < len(coords):
                            xPos.append(float(coords[i * 3]))
                            yPos.append(float(coords[i * 3 + 1]))
                            zPos.append(float(coords[i * 3 + 2]))
                avgX = sum(xPos) / len(xPos)
                avgY = sum(yPos) / len(yPos)
                avgZ = sum(zPos) / len(zPos)
                avgPos.append(f'{avgX},{avgY},{avgZ},')

            avgPosString = ''.join(avgPos)
            sock.sendto(avgPosString.encode(), serverAddressPort)
    # breakpoint()
    # print(len(posList))

    cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
