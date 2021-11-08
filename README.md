# imgs2pdf

This Python script converts images (png, jpg, etc..) in a directory to one pdf file.

## Usage

```bash
$ python3 /path/to/imgs2pdf.py -o /path/to/output.pdf -f /path/to/image_folder -e .png .jpg -c 188 65 1290 829
```

You can run this script from any directory.

Run the following command for any help.

```bash
$ python3 imgs2pdf.py -h
```

## Options

- `--output`, `-o`: output pdf file name (default: output.pdf)
- `--folder`, `-f`: source images directory name (default: .)
- `--extensions`, `-e`: source images extensions (default: png)
- `--crop`, `-c`: left top right bottom (default: -1)
- `--reverse`, `-r`: concat images in reverse order
- `--store`, `-s`: store intermediate outputs