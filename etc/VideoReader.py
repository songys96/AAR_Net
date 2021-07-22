"""
사용방법
이 파일을 데이터셋 폴더에 놓습니다
demo1
    python VideoReader.py ./source_9/20201024_cat-sitdown-000071.mp4
    python VideoReader.py ./source_1/20201117_dog-walkrun-002853.mp4

demo2
    python VideoReader.py
    >> 파일 경로를 적어주세요 : (파일 경로 입력)

"""


import os
import time
import argparse

import cv2


parser = argparse.ArgumentParser(description="load video from folder")
parser.add_argument("-f", type=str, help="video folder path")
args = parser.parse_args()


class VideoReader():
    def __init__(self):
        pass

    def loadVideo(self, folder):
        frames = []
        frame_names = []
        frame_list = sorted(os.listdir(folder), key=lambda name: int(name.split("_")[-1].split(".")[0]))
        for frame_name in frame_list:
            frame = os.path.join(folder, frame_name)
            frame_names.append(frame_name)
            frames.append(cv2.imread(frame))

        return frames, frame_names

    def playVideo(self, folder):
        folder = os.path.abspath(folder)
        if not os.path.exists(folder):
            print(folder, " is not existed")
            raise FileNotFoundError
        video_name = folder.split("/")[-1]
        frames, frame_names = self.loadVideo(folder)
        video = zip(frames, frame_names)
        sample = frames[0]
        height, width, _ = sample.shape
        # video = cv2.VideoWriter(video_name, -1,1,(width, height))

        for frame, frame_name in video:
            cv2.putText(frame, frame_name, (20, height-20), cv2.FONT_HERSHEY_SIMPLEX, 
                   1.2, (0,0,0), 2, cv2.LINE_AA)
            cv2.imshow(video_name, frame)
            time.sleep(0.05)
            # video.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()
        # video.release()
        
if __name__ == "__main__":
    vr = VideoReader()
    if not args.f:
        args.f = input("파일 경로를 적어주세요 : ")
    vr.playVideo(args.f)


