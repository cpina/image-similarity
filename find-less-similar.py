#!/usr/bin/python3

# Inspired from https://gist.github.com/duhaime/211365edaddf7ff89c0a36d9f3f7956c

import os
import collections
import operator
import glob
import imageio
import numpy
import scipy
import scipy.ndimage


def read_image(path, rectangular_area):
    image = imageio.imread(path)

    cropped_image = image[rectangular_area[0][1]:rectangular_area[1][1],
            rectangular_area[0][0]:rectangular_area[1][0]]

    imageio.imwrite("/tmp/test.jpg", cropped_image)

    return cropped_image


def pixel_similarity(image_a, image_b):
    return numpy.sum(numpy.absolute(image_a - image_b))


def rank_images(base_image_path, directory_path, rectangular_area):
    base_image = read_image(base_image_path, rectangular_area)

    file_simliarities = {}

    max_number_of_files = -1
    processed = 0

    image_paths = glob.glob(directory_path)
    for image_path in image_paths:
        image = read_image(image_path, rectangular_area)
        similarity_index = pixel_similarity(base_image, image)
        file_simliarities[image_path] = similarity_index

        processed += 1

        if max_number_of_files != -1 and processed > max_number_of_files:
            break

        if processed % 50 == 0:
            print("Images processed: {} Percentage: {:.2f}%".format(processed, (processed/len(image_paths))*100))

    return collections.OrderedDict(sorted(file_simliarities.items(), key=operator.itemgetter(1)))


def print_rank(rank, output_path):
    os.makedirs(output_path, exist_ok=True)
    count = 0
    width = 6
    for file_path in rank:
        print(file_path, rank[file_path])
        image_number = "%0*d" % (width, count)
        os.symlink(file_path, output_path + "/" + image_number + ".jpg")

        count += 1


if __name__ == "__main__":
    base_image_path = "/media/carles/c3726133-fb1b-4bf8-a2be-56d88ecfb291/camera/images/test000062069.jpg"
    rectangular_area = ((380, 356), (970, 664))

    rank = rank_images(base_image_path, "/media/carles/c3726133-fb1b-4bf8-a2be-56d88ecfb291/camera/images/*", rectangular_area)

    print_rank(rank, "/tmp/output_images")