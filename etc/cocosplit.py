"""
usage
$ python cocosplit.py --having-annotations -s 0.8 /path/to/your/coco_annotations.json train.json test.json
python3 cocosplit.py --having-annotations -s 0.8 /home/butler/Desktop/Dataset/aihub/Training/COCO/aihub_coco.json /home/butler/Desktop/Dataset/aihub/Training/COCO/train_sum.json /home/butler/Desktop/Dataset/aihub/Training/COCO/test.json
python3 cocosplit.py --having-annotations -s 0.75 /home/butler/Desktop/Dataset/aihub/Training/COCO/train_sum.json /home/butler/Desktop/Dataset/aihub/Training/COCO/train.json /home/butler/Desktop/Dataset/aihub/Training/COCO/valid.json
"""


import json
import argparse
import funcy
from sklearn.model_selection import train_test_split

parser = argparse.ArgumentParser(description='Splits COCO annotations file into training and test sets.')
parser.add_argument('annotations', metavar='coco_annotations', type=str,
                    help='Path to COCO annotations file.')
parser.add_argument('train', type=str, help='Where to store COCO training annotations')
parser.add_argument('test', type=str, help='Where to store COCO test annotations')
parser.add_argument('-s', dest='split', type=float, required=True,
                    help="A percentage of a split; a number in (0, 1)")
parser.add_argument('--having-annotations', dest='having_annotations', action='store_true',
                    help='Ignore all images without annotations. Keep only these with at least one annotation')

args = parser.parse_args()

def save_coco(file, info, licenses, images, annotations, categories):
    with open(file, 'wt', encoding='UTF-8') as coco:
        json.dump({ 'info': info, 'licenses': licenses, 'images': images, 
            'annotations': annotations, 'categories': categories}, coco, indent=2, sort_keys=True)

def filter_annotations(annotations, images):
    image_ids = funcy.lmap(lambda i: int(i['id']), images)
    return funcy.lfilter(lambda a: int(a['image_id']) in image_ids, annotations)

def main(args):
    with open(args.annotations, 'rt', encoding='UTF-8') as annotations:
        print("loaded")
        coco = json.load(annotations)
        info = coco['info']
        licenses = coco['licenses']
        images = coco['images']
        annotations = coco['annotations']
        categories = coco['categories']

        number_of_images = len(images)
        print(number_of_images)
        images_with_annotations = funcy.lmap(lambda a: int(a['image_id']), annotations)
        print("images with annotations")
        # if args.having_annotations:
        #     images = funcy.lremove(lambda i: i['id'] not in images_with_annotations, images)
        print("anno check")
        x, y = train_test_split(images, train_size=args.split)
        print("splited")
        save_coco(args.train, info, licenses, x, filter_annotations(annotations, x), categories)
        print("save train")
        save_coco(args.test, info, licenses, y, filter_annotations(annotations, y), categories)

        print("Saved {} entries in {} and {} in {}".format(len(x), args.train, len(y), args.test))


if __name__ == "__main__":
    main(args)