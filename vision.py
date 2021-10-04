from networktables import NetworkTables
import numpy as np
import cv2
import imutils


NetworkTables.initialize(server="roborio-7672-frc.local")
table = NetworkTables.getTable("Vision")

colorLower = (20, 100, 100)
colorUpper = (30, 255, 255)

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)

x = 0
y = 0


while True:

    (
        grabbed,
        frame,
    ) = camera.read()

    frame = imutils.rotate(frame, angle=0)

    def white_balance(frame):
        result = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        avg_a = np.average(result[:, :, 1])
        avg_b = np.average(result[:, :, 2])
        result[:, :, 1] = result[:, :, 1] - (
            (avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1
        )
        result[:, :, 2] = result[:, :, 2] - (
            (avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1
        )
        result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
        return result

    result = white_balance(frame)

    hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, colorLower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None

    if len(cnts) > 0:

        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 10:
            cv2.circle(result, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(result, center, 5, (0, 0, 255), -1)

        print(radius, x, y)

    else:
        x = 0
        y = 0
        r = 0

    cv2.imshow("test", result)
    cv2.waitKey(1)

    table.putNumber("X", x)
    table.putNumber("Y", y)
    table.putNumber("R", radius)
