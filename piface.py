from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition as fr
import argparse
import imutils
import pickle
import time
import cv2


ap = argparse.ArgumentParser()

ap.add_argument("-c","--cascade",required=True,help="path to where the face cascade resides")
ap.add_argument("-e","--encodings",required=True,help="path to serialized db of facial encodings")

args = vars(ap.parse_args())

print("[INFO] loading encoding + face detector...")
data = pickle.loads(open(args["encodings"],"rb").read())
detector = cv2.CascadeClassifier(args["cascade"])

print("[INFO] starting video stream")

vs = VideoStream(src=0).start()

time.sleep(2.0)

fps = FPS().start()

while True:
    frame = vs.read()
    frame = imutils.resize(frame,width=500)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    rects = detector.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30))

    boxes = [(y,x+w,y+h,x) for (x,y,w,h) in rects]

    encodings =fr.face_encodings(rgb,boxes)

    names = []

    for encoding in encodings:

        matches = fr.compare_faces(data["encodings"],encoding)
        name = "Unknown"

        if True in matches:

            matchesIdxs = [i for (i,b) in enumerate(matches) if b]

            counts = {}

            for i in matchesIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name,0) + 1

                name = max(counts,key=counts.get)
        
        names.append(name)

        for ((top, right, bottom, left), name) in zip(boxes, names):
            cv2.rectangle(frame, (left,top), (right, bottom),(0,255,0),2)

            y = top - 15 if top - 15 > 15 else top + 15

            cv2.putText(frame, name, (left, y),cv2.FONT_HERSHEY_SIMPLEX,0.75,(255,0,0),2)

            cv2.imshow("Frame",frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            fps.update()

fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
vs.stop()



