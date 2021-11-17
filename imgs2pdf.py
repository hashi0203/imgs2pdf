import argparse
import glob
import os
import shutil
import traceback
import subprocess

from natsort import natsorted
import img2pdf
import cv2
from read_heic import read_heic

def print_size(path):
    print('%12d B: %s' % (os.path.getsize(path), path))

def main(output_name, input_folder, extensions, left, top, right, bottom, angle, flipcode, reverse, store, unique_output, pdfsettings):
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
        assert len(input_files) > 0, "No files selected. Check the directory or extensions."
        print(input_files)

        for i, filename in enumerate(input_files):
            if filename.lower().endswith('.heic'):
                img = read_heic(filename)
                input_files[i] = filename = filename[:-5] + '.png'
            else:
                img = cv2.imread(os.path.join(input_folder, filename), cv2.IMREAD_UNCHANGED)
                if img.shape[2] == 4: # remove alpha
                    img = cv2.imread(os.path.join(input_folder, filename), cv2.IMREAD_COLOR)
            # crop images
            l = left if 0 <= left < img.shape[1] else 0
            t = top if 0 <= top < img.shape[0] else 0
            r = right if left <= right < img.shape[1] else img.shape[1]-1
            b = bottom if top <= bottom < img.shape[0] else img.shape[0]-1
            img = img[t:b+1, l:r+1]
            # rotate images
            if angle == 90:
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            elif angle == 180:
                img = cv2.rotate(img, cv2.ROTATE_180)
            elif angle == 270:
                img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            # filp images
            if flipcode is not None:
                img = cv2.flip(img, flipcode)
            # save images
            cv2.imwrite(os.path.join(tmp_folder, filename), img)

        org_name = '%s.pdf' % output_name
        with open(org_name, "wb") as f:
            f.write(img2pdf.convert([os.path.join(tmp_folder, str(filename)) for filename in input_files]))

        print_size(org_name)

        if len(pdfsettings) > 0:
            for s in pdfsettings:
                compress_name = '%s-%s.pdf' % (output_name, s)
                subprocess.check_output(['gs',
                    '-sDEVICE=pdfwrite',
                    '-dPDFSETTINGS=/%s' % s,
                    '-dBATCH',
                    '-dNOPAUSE',
                    '-dSAFER',
                    '-sOUTPUTFILE=%s' % compress_name,
                    org_name
                    ])

                print_size(compress_name)

            if unique_output:
                print('$ mv %s %s' % (compress_name, org_name))
                shutil.move(compress_name, org_name)

    except Exception as e:
        print(traceback.format_exc())
    finally:
        if not(store):
            shutil.rmtree(tmp_folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converter from images to pdf')
    parser.add_argument('--output', '-o', type=str, default='output.pdf', help='output pdf file name (default: output.pdf)')
    parser.add_argument('--folder', '-f', type=str, default='.', help='source images directory name (default: .)')
    parser.add_argument('--extensions', '-e', nargs='+', type=str, default=['png'], help='source images extensions (default: png)')
    parser.add_argument('--crop', '-c', nargs='+', type=int, default=-1, help='left top right bottom (crop -> rotate -> flip) (default: -1)')
    parser.add_argument('--angle', '-a', type=int, default=0, help='clockwise image rotation angle (0, 90, 180, or 270) (crop -> rotate -> flip) (default: 0)')
    parser.add_argument('--horizontal', '-l', action='store_true', help='horizontal flip (crop -> rotate -> flip)')
    parser.add_argument('--vertical', '-u', action='store_true', help='vertical flip (crop -> rotate -> flip)')
    parser.add_argument('--reverse', '-r', action='store_true', help='concat images in reverse order')
    parser.add_argument('--store', '-s', action='store_true', help='store intermediate outputs')
    parser.add_argument('--pdfsettings', '-p', nargs='+', type=int, default=[-1], help='specify compression level (-1: all types, 0: original, ..., 5: smallest) (default: -1)')
    args = parser.parse_args()

    output_name = args.output[:-4] if args.output.endswith('.pdf') else args.output
    input_folder = args.folder
    extensions = [e if e.startswith('.') else '.' + e for e in args.extensions]
    crop = args.crop if isinstance(args.crop, list) else [args.crop]
    assert args.angle in [0, 90, 180, 270], "--angle, -a option should be either 0, 90, 180, or 270."
    angle = args.angle
    flipcode = None
    if args.horizontal and args.vertical:
        flipcode = -1
    elif args.horizontal:
        flipcode = 1
    elif args.vertical:
        flipcode = 0
    left, top, right, bottom = crop[:4] + [-1] * (4 - len(crop))
    left, top = max(left, 0), max(top, 0)
    reverse = args.reverse
    store = args.store
    pdfsettings = set()
    unique_output = len(args.pdfsettings) == 1 and args.pdfsettings[0] != -1
    settings = ['1:default', '2:prepress', '3:printer', '4:ebook', '5:screen']
    for s in args.pdfsettings if isinstance(args.pdfsettings, list) else [args.pdfsettings]:
        assert -1 <= s <= 5, "--pdfsettings, -p option should be integer in range [-1, 5]."
        if s == -1:
            pdfsettings |= set(settings)
        elif s > 0:
            pdfsettings.add(settings[s-1])
    pdfsettings = [s[2:] for s in sorted(list(pdfsettings))]
    print(pdfsettings)

    main(output_name, input_folder, extensions, left, top, right, bottom, angle, flipcode, reverse, store, unique_output, pdfsettings)
