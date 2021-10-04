import cv2

# distance from camera to object(face) measured
# centimeter
known_distance = 47

# width of face in the real world or Object Plane
# centimeter
known_width = 16

colorLower = (20, 100, 100)
colorUpper = (30, 255, 255)

fonts = cv2.FONT_HERSHEY_COMPLEX

GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# focal length finder function
def focal_length_finder(measured_distance, real_width, width_in_rf_image):

    # finding the focal length
    focal_length = (width_in_rf_image * measured_distance) / real_width
    return focal_length


# distance estimation function
def distance_finder(focal_length, real_face_width, face_width_in_frame):

    distance = (real_face_width * focal_length) / face_width_in_frame

    # return the distance
    return distance


def circle(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
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
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)

        print(radius, x, y)

    else:
        x = 0
        y = 0
        r = 0

    try:
        return cv2.minAreaRect(c)

    except UnboundLocalError:
        pass


# reading reference_image from directory
ref_image = cv2.imread("test.jpg")

# find the face width(pixels) in the reference_image
ref_image_face_width = 520

# get the focal by calling "Focal_Length_Finder"
# face width in reference(pixels),
# Known_distance(centimeters),
# known_width(centimeters)
Focal_length_found = focal_length_finder(
    known_distance, known_width, ref_image_face_width
)

print(Focal_length_found)

# show the reference image
cv2.imshow("ref_image", ref_image)

# initialize the camera object so that we
# can get frame from it
cap = cv2.VideoCapture(0)

# looping through frame, incoming from
# camera/video
while True:

    # reading the frame from camera
    _, frame = cap.read()

    circle_var = circle(frame)

    # calling face_data function to find
    # the width of face(pixels) in the frame
    try:
        circle_var0, circle_var1, circle_var2 = circle_var

    except TypeError:
        pass
    face_width_in_frame = float(list(map(float, circle_var0))[0])
    # check if the face is zero then not
    # find the distance
    if face_width_in_frame != 0:

        # finding the distance by calling function
        # Distance distance finder function need
        # these arguments the Focal_Length,
        # Known_width(centimeters),
        # and Known_distance(centimeters)
        Distance = distance_finder(Focal_length_found, known_width, face_width_in_frame)

        # draw line as background of text
        cv2.line(frame, (30, 30), (230, 30), RED, 32)
        cv2.line(frame, (30, 30), (230, 30), BLACK, 28)

        # Drawing Text on the screen
        cv2.putText(
            frame, f"Distance: {round(Distance,2)} CM", (30, 35), fonts, 0.6, GREEN, 2
        )

    # show the frame on the screen
    cv2.imshow("frame", frame)

    # quit the program if you press 'q' on keyboard
    if cv2.waitKey(1) == ord("q"):
        break

# closing the camera
cap.release()

# closing the the windows that are opened
cv2.destroyAllWindows()
