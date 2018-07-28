#!/usr/bin/python3

# Inspired from https://gist.github.com/duhaime/211365edaddf7ff89c0a36d9f3f7956c

import time
import os
import glob
import imageio
import numpy
import concurrent.futures
import multiprocessing


def read_image(path, rectangular_area):
    image = imageio.imread(path)

    cropped_image = image[rectangular_area[0][1]:rectangular_area[1][1],
            rectangular_area[0][0]:rectangular_area[1][0]]

    # imageio.imwrite("/tmp/test.jpg", cropped_image)

    return cropped_image


def pixel_similarity(image_a, image_b):
    return numpy.sum(numpy.absolute(image_a - image_b))


def seconds_to_minutes_seconds(seconds):
    m, s = divmod(seconds, 60)
    return "{}m {:02}s".format(int(m), int(s))


def process_image(image_path, rectangular_area, output_directory, base_image, starts_timestamp, counter, total):
    image = read_image(image_path, rectangular_area)
    similarity_index = pixel_similarity(base_image, image)
    similarity = "{:010}".format(similarity_index)
    image_basename = os.path.splitext(os.path.basename(image_path))[0]
    base_filename = "{}_{}".format(similarity, image_basename)
    output_path = "{output_directory}/{base_filename}.jpg".format(output_directory=output_directory,
                                                                   base_filename=base_filename)
    os.symlink(image_path, output_path)

    counter.value += 1

    counter_value = counter.value

    if counter_value % 50 == 0:
        time_elapsed = time.time() - starts_timestamp
        percentage = (counter_value / total) * 100
        # eta = (total * time_elapsed) / counter_value
        total_time = (total * time_elapsed) / counter_value
        eta = total_time - starts_timestamp
        print("Images processed: {} Percentage: {:.2f}% Elapsed: {} ETA: {}".format(counter_value, percentage,
                                                                                    seconds_to_minutes_seconds(
                                                                                        time_elapsed),
                                                                                    seconds_to_minutes_seconds(eta)))


def rank_images(base_image_path, directory_path, rectangular_area, output_directory):
    base_image = read_image(base_image_path, rectangular_area)

    image_paths = glob.glob(directory_path)

    starts_timestamp = time.time()

    counter = multiprocessing.Value('i', 0)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(lambda image_path: process_image(image_path,
                                                      rectangular_area,
                                                      output_directory,
                                                      base_image,
                                                      starts_timestamp,
                                                      counter,
                                                      len(image_paths)), image_paths)


if __name__ == "__main__":
    base_image_path = "/media/carles/c3726133-fb1b-4bf8-a2be-56d88ecfb291/camera/images/test000062069.jpg"
    rectangular_area = ((380, 356), (970, 664))

    rank_images(base_image_path,
               "/media/carles/c3726133-fb1b-4bf8-a2be-56d88ecfb291/camera/images/*",
               rectangular_area,
               "/tmp/output_images")