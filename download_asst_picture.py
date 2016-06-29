import os
from os.path import basename, dirname, join, splitext, exists
from contextlib import closing
import codecs
import time
import requests
import unicodecsv


def conv_file_to_utf16le(filepath):
    BLOCKSIZE = 4 * 1024
    fname = basename(filepath)
    tmp_fname = fname + str(time.time())
    tmp_filepath = join(dirname(filepath), tmp_fname)
    with codecs.open(filepath, 'r', 'utf-8') as src_file:
        with codecs.open(tmp_filepath, 'w', 'UTF-16LE') as dst_file:
            # dst_file.write(codecs.BOM_UTF16_LE)
            while True:
                content = src_file.read(BLOCKSIZE)
                if not content:
                    break
                dst_file.write(content)
    # remove old file and rename temp one
    # time.sleep(5)
    os.remove(filepath)
    os.rename(tmp_filepath, filepath)
    
def download_file(url, filepath):
    CHUNK_SIZE = 1024 * 8
    with closing(requests.get(url, stream=True)) as r:
        if r.status_code >= 400: 
            return None
        fd = open(filepath, 'wb')
        for chunk in r.iter_content(CHUNK_SIZE):
            fd.write(chunk)
        fd.flush()
        fd.close()
 
    
def parse_picture_field(text):
    if not text:
        return None
    lines = text.split(';')
    ret = []
    for line in lines:
        if not line:
            continue
        parts = line.split('|')
        name = parts[0].split(':')[0]
        url = parts[1]
        ret.append((name, url))
    return ret

def download_assist_tbi(filepath):
    dir = dirname(filepath)
    name = splitext(basename(filepath))[0]
    img_dir = join(dir, name)
    if not exists(img_dir):
        os.mkdir(img_dir)
    csv_reader = unicodecsv.UnicodeReader(open(filepath), dialect='excel-tab', encoding='utf-8')
    # skip 3 head lines
    csv_reader.next()
    headers = csv_reader.next()
    csv_reader.next()

    idx = -1
    for i, c in enumerate(headers):
        if c == 'picture':
            idx = i
            break
    if idx > -1:
        for row in csv_reader:
            pic_infos = parse_picture_field(row[idx])
            if not pic_infos:
                continue
            for name, url in pic_infos:
                fpath = join(img_dir, name + '.tbi')
                download_file(url, fpath)
    
download_assist_tbi('export.csv')

