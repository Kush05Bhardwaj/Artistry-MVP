from segment import Segmenter

segmenter = Segmenter()
seg_map, image = segmenter.segment("room.jpg")

print("Segmentation successful")