from lib.dataset.aihub import AIHubDataset
from lib.core.config import config
import matplotlib.pyplot as plt

aihub = AIHubDataset(config, "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub", False, debug=True)
sample = aihub[3]
img = sample['images'][0]
kp = sample['keypoints'][0]
plt.imshow(img)
for i in kp:
    if i[0]==0:
        continue
    plt.plot(i[0], i[1], 'ro')
plt.show()



