import time
import numpy as np
import picamera
from threading import Thread
import logging

class BaseSensor(object):

    def start(self):
        '''
        Start receiving values from the sensor
        '''
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        time.sleep(1)
        return self

    def update(self):
        '''
        Performs sensor update steps. This is called
        in a separate thread
        '''
        pass

class BaseCamera(BaseSensor):

    def __init__(self, resolution=(640,480), **kwargs):
        super(BaseCamera, self).__init__(**kwargs)

        self.resolution = resolution
        self.frame = np.zeros(
            shape=(
                self.resolution[1],
                self.resolution[0],
                3))
        self.frame_time = 0
        self.encoded_time = 0
        self.base64_time = 0

    def image_buffer(self):
        '''
        Returns the JPEG image buffer corresponding to
        the current frame. Caches result for
        efficiency.
        '''
        if self.frame_time > self.encoded_time:
            arr = self.frame
            img = Image.fromarray(arr, 'RGB')
            encoded_buffer = cStringIO.StringIO()
            img.save(encoded_buffer, format="JPEG",
                     quality=100, subsampling=0)
            self.encoded_buffer = encoded_buffer
            self.encoded_time = time.time()
        else:
            encoded_buffer = self.encoded_buffer
        return encoded_buffer

    def base64(self):
        '''
        Returns a base-64 encoded string corresponding
        to the current frame. Caches result for
        efficiency.
        '''
        if self.frame_time > self.base64_time:
            image_buffer = self.image_buffer()
            image_buffer.seek(0)
            base64_buffer = base64.b64encode(image_buffer.read())
            self.base64_buffer = base64_buffer
            self.base64_time = time.time()
        else:
            base64_buffer = self.base64_buffer
        return base64_buffer

class PiVideoStream(BaseCamera):

    def __init__(self, resolution=(640,480),
                 framerate=32,
                 rotation=0, **kwargs):
        from picamera.array import PiRGBArray
        from picamera import PiCamera

        super(PiVideoStream, self).__init__(resolution, **kwargs)

        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.rotation = rotation
        self.camera.exposure_mode = "sports"
        self.rawCapture = PiRGBArray(self.camera, size=resolution)

        self.frame = None
        self.stopped = False

        logging.info("PiVideoStream loaded.. .warming camera")

        time.sleep(2)
        self.start()

    def update(self):
        for f in self.camera.capture_continuous(
                self.rawCapture, format="rgb", use_video_port=True):
            self.frame = f.array

            self.rawCapture.truncate(0)
            self.frame_time = time.time()

            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def stop(self):
        self.stopped = True

BaseCamera()
