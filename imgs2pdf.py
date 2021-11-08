import argparse
import glob
import os
import shutil
import traceback

from natsort import natsorted
import img2pdf
import cv2

def main(output_name, input_folder, extensions, left, top, right, bottom, reverse, store):
    # make a work directory in input_folder
    tmp_folder = os.path.join(input_folder, "tmp")
    while os.path.exists(tmp_folder):
        tmp_folder += "tmp"
    os.mkdir(tmp_folder)

    try:
        input_files = []
        for e in extensions:
            input_files += list(glob.glob(os.path.join(input_folder, "*" + e)))
        input_files = [os.path.split(filename)[-1] for filename in input_files]
        input_files = natsorted(input_files, reverse=reverse)
        print(input_files)

        for filename in input_files:
            img = cv2.imread(os.path.join(input_folder, filename), cv2.IMREAD_UNCHANGED)
            if img.shape[2] == 4: # remove alpha
                img = cv2.imread(os.path.join(input_folder, filename), cv2.IMREAD_COLOR)
            # crop images
            l = left if 0 <= left < img.shape[1] else 0
            t = top if 0 <= top < img.shape[0] else 0
            r = right if left <= right < img.shape[1] else img.shape[1]-1
            b = bottom if top <= bottom < img.shape[0] else img.shape[0]-1
            img = img[t:b+1, l:r+1]
            cv2.imwrite(os.path.join(tmp_folder, filename), img)

        with open(output_name, "wb") as f:
            f.write(img2pdf.convert([os.path.join(tmp_folder, str(filename)) for filename in input_files]))

    except Exception as e:
        print(traceback.format_exc())
    finally:
        if not(store):
            shutil.rmtree(tmp_folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converter from images to pdf')
    parser.add_argument('--output', '-o', type=str, default='output.pdf', help='output pdf file name (default: output.pdf)')
    parser.add_argument('--folder', '-f', type=str, default='.', help='source images directory name (default: .)')
    parser.add_argument('--extensions', '-e', nargs='+', type=str, default='png', help='source images extensions (default: png)')
    parser.add_argument('--crop', '-c', nargs='+', type=int, default=-1, help='left top right bottom (default: -1)')
    parser.add_argument('--reverse', '-r', action='store_true', help='concat images in reverse order')
    parser.add_argument('--store', '-s', action='store_true', help='store intermediate outputs')
    args = parser.parse_args()

    output_name = args.output if args.output.endswith('.pdf') else args.output + ".pdf"
    input_folder = args.folder
    extensions = args.extensions if isinstance(args.extensions, list) else [args.extensions]
    extensions = [e if e.startswith('.') else '.' + e for e in extensions]
    crop = args.crop if isinstance(args.crop, list) else [args.crop]
    left, top, right, bottom = crop[:4] + [-1] * (4 - len(crop))
    left, top = max(left, 0), max(top, 0)
    reverse = args.reverse
    store = args.store

    main(output_name, input_folder, extensions, left, top, right, bottom, reverse, store)
