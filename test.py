# from lib.dataset.aihub import AIHubDataset
# from lib.core.config import config
import matplotlib.pyplot as plt

# aihub = AIHubDataset(config, "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub", False, debug=True)
# sample = aihub[3]
# img = sample['images'][0]
# kp = sample['keypoints'][0]
img = '/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/source_9/20201024_cat-footpush-000053.mp4/frame_288_timestamp_4800.jpg'
img = plt.imread(img)
plt.imshow(img)

plt.show()



