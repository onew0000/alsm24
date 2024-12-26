import cv2
import time

class BlinkDetector:
    def __init__(self):
        self.eye_cascPath = '/Users/jaeminahn/Desktop/2024 ALSM/haarcascade_eye_tree_eyeglasses.xml'
        self.face_cascPath = '/Users/jaeminahn/Desktop/2024 ALSM/haarcascade_frontalface_alt.xml'
        self.faceCascade = cv2.CascadeClassifier(self.face_cascPath)
        self.eyeCascade = cv2.CascadeClassifier(self.eye_cascPath)
        
        self.blink_counter = 0
        self.blink_start_time = time.time()
        self.BLINK_THRESHOLD = 5 
        self.TIME_WINDOW = 10 
        
        self.total_time = 0
        self.eyes_closed_start = None

    def calculate_blink_rate(self):
        current_time = time.time()
        time_elapsed = current_time - self.blink_start_time
        
        if time_elapsed >= self.TIME_WINDOW:
            blink_rate = self.blink_counter / time_elapsed
            self.blink_counter = 0
            self.blink_start_time = current_time
            return blink_rate
        return None

    def run(self):
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, img = cap.read()
            if not ret:
                break
                
            frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.faceCascade.detectMultiScale(
                frame,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
            )
            
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    frame_tmp = img[y:y+h, x:x+w:1, :]
                    frame_roi = frame[y:y+h, x:x+w:1]
                    
                    eyes = self.eyeCascade.detectMultiScale(
                        frame_roi,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30),
                    )
                    
                    if len(eyes) == 0:
                        if self.eyes_closed_start is None:
                            self.eyes_closed_start = time.time()
                            self.blink_counter += 1
                        print('눈 감음 감지')
                        self.total_time += 1
                    else:
                        if self.eyes_closed_start is not None:
                            self.eyes_closed_start = None
                        #print('탐지중... 눈 감은 시간:', self.total_time, '초')
                    
                    blink_rate = self.calculate_blink_rate()
                    if blink_rate is not None:
                        print(f'현재 분당 눈 깜빡임 횟수: {blink_rate * 60:.1f}회')
                        if blink_rate * 60 > 20: 
                            print('경고: 빠른 눈 깜빡임이 감지되었습니다. 불안 증세일 수 있습니다.')
                    
                    frame_tmp = cv2.resize(frame_tmp, (400, 400), interpolation=cv2.INTER_LINEAR)
                    cv2.imshow('Eye Blink Detector', frame_tmp)
            
            waitkey = cv2.waitKey(1)
            if waitkey == ord('q') or waitkey == ord('Q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = BlinkDetector()
    detector.run()