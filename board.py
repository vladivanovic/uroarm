"""Calibrate Camera

See below
    naoki-mizuno/charuco_webcam.py
    https://gist.github.com/naoki-mizuno/c80e909be82434ddae202ff52ea1f80a
"""
#
# As above, this code is used for Camera Calibiration using CharucoBoard
#

import sys
import time
import cv2
from cv2 import aruco
import cv2

from util import write_params, read_params
from camera import initCamera, closeCamera, getCameraFrame

if __name__ == '__main__':

    params = read_params()
    
    initCamera(params)

    dictionary_name = '4X4_50'
    dictionary = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

    squares_x = 5
    squares_y = 7
    square_length = 0.0325
    marker_length = 0.01625
    board = aruco.CharucoBoard_create(squares_x, squares_y, square_length, marker_length, dictionary)

    total_frame_count = 50

    all_corners = []
    all_ids = []

    camera_matrix   = None
    dist_coeffs      = None

    last_capture = time.time()
    while True:

        frame = getCameraFrame()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        imsize = gray.shape

        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, dictionary)

        if len(corners) > 0:
            ret, c_corners, c_ids = cv2.aruco.interpolateCornersCharuco(corners, ids, gray, board)
            # ret is the number of detected corners
            if ret > 0:

                aruco.drawDetectedCornersCharuco(frame, c_corners, c_ids, (255, 0, 0))
                if len(c_corners) == (squares_x - 1) * (squares_y - 1) and 1 <= time.time() - last_capture:
                    all_corners.append(c_corners)
                    all_ids.append(c_ids)

                    print(f'frame count {len(all_corners)}/{total_frame_count}')

                    last_capture = time.time()

                    if len(all_corners) == total_frame_count:

                        print('calibrating camera. It may take several tens of seconds.')
                        ret, camera_matrix, dist_coeffs, rvec, tvec = cv2.aruco.calibrateCameraCharuco(
                            all_corners, all_ids, board, imsize, None, None
                        )

                        params = read_params()
                        params['cameras'][dictionary_name] = {
                            "camera-matrix": camera_matrix.tolist(),
                            "dist-coeffs": dist_coeffs.tolist()
                        }

                        write_params(params)
                        print(f'camera calibration completed. time:{time.time() - last_capture:.1f}sec')
                        break

            if c_ids is not None:
                cv2.putText(frame, text=f'detected markers:{len(c_ids)}', org=(5, 25),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.8,
                    color=(0, 0, 255),
                    thickness=1,
                    lineType=cv2.LINE_AA
                )

        else:
            c_corners   = None
            c_ids       = None

        if frame.shape[0] == 720:
            frame2 = frame
        else:
            frame2 = cv2.resize(frame, (720, 720))

        cv2.imshow("camera", frame2)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    closeCamera()    
