# pip install PyMuPDF
import pymupdf
import traceback, datetime, os, sys

doc = None
workDir = os.path.dirname(__file__)

def parse_cmd(cmd):
    if not cmd or not cmd.strip():
        return
    opts = []
    cmd = cmd.strip()
    i = 0
    SP = ('"', "'", ' ', '\t')
    while i < len(cmd):
        if cmd[i] not in SP:
            s = ''
            while i < len(cmd) and (cmd[i] not in SP):
                s += cmd[i]
                i += 1
            opts.append(s)
        elif cmd[i] == '"' or cmd[i] == "'":
            s = ''
            t = cmd[i]
            i += 1 # skip start
            while i < len(cmd) and cmd[i] != t:
                s += cmd[i]
                i += 1
            i += 1 # skip end
            opts.append(s)
        else: # is space
            i += 1
    return opts

def get_file_path(path : str):
    if path: path = path.strip()
    path = path.replace('$scan', 'C:\\Users\\GaoYan\\Documents\\Scanned Documents', 1)
    path = path.replace('$desktop', 'C:\\Users\\GaoYan\\Desktop', 1)
    absPath = ''
    if len(path) > 2 and path[1] == ':':
        absPath = path
    else:
        absPath = os.path.join(workDir, path)
    return absPath

def cd_(opts):
    global workDir
    if len(opts) != 2:
        return False
    path = opts[1].strip()
    workDir = get_file_path(path)
    print('[Success] Work directory: ', workDir)
    return False

def adjust_page_pos(pos, doc):
    pos = int(pos)
    if pos < 0:
        if doc.page_count == 0:
            return -1 if pos == -1 else None
        if -pos <= doc.page_count + 1:
            return pos
        return None
    if pos >= 0 and pos <= doc.page_count:
        return pos
    return None

def create(opts):
    global doc
    if doc is not None:
        doc.close()
    doc = pymupdf.open()
    print('[success]')
    return True

def open_(opts):
    global doc
    if doc is not None:
        doc.close()
    if len(opts) != 2:
        return False
    file = get_file_path(opts[1])
    doc = pymupdf.open(file)
    print('[success]')
    return True

def insert_img(opts):
    global doc
    if len(opts) != 3:
        return False
    pos = adjust_page_pos(opts[1], doc)
    if pos is not None:
        doc.insert_file(get_file_path(opts[2]), start_at = pos)
        print('[success]')
        return True
    return False

def insert_pdf(opts):
    global doc
    if len(opts) != 4:
        return False
    pos = adjust_page_pos(opts[1], doc)
    if pos is not None:
        doc.insert_file(get_file_path(opts[2]), from_page = int(opts[3]), to_page = int(opts[3]), start_at = pos)
        print('[success]')
        return True
    return False

def append_pdf(opts):
    global doc
    if len(opts) != 2:
        return False
    doc.insert_file(get_file_path(opts[1]), from_page = 0, to_page = -1, start_at = -1)
    print('[success]')
    return True

def move(opts):
    global doc
    if len(opts) != 3:
        return False
    fromPos, toPos = adjust_page_pos(opts[1], doc), adjust_page_pos(opts[2], doc)
    if fromPos is None or toPos is None:
        return False
    doc.move_page(fromPos, toPos)
    print('[success]')
    return True

def save(opts):
    now = datetime.datetime.now()
    name = now.strftime('%Y%m%d_%H%M%S.pdf')
    p = get_file_path(name)
    doc.save(p)
    print('[success]')
    return True

def attach_img(opts):
    if len(opts) != 5 and len(opts) != 7:
        return False
    pos = adjust_page_pos(opts[1], doc)
    fs = get_file_path(opts[2])
    if (not os.path.exists(fs)) or (pos is None):
        return False
    img = pymupdf.Pixmap(fs)
    x, y = int(opts[3]), int(opts[4])
    if len(opts) == 7:
        w, h = int(opts[5]), int(opts[6])
    else:
        w, h = img.width, img.height
    page = doc.load_page(pos)
    page.insert_image(pymupdf.Rect(x, y, x + w, y + h), pixmap = img)
    print('[success]')
    return True

# 电子印章
def attach_yz(opts):
    if len(opts) != 4:
        return False
    opts.insert(2, r'C:\vscode\PdfEditor\yz.png')
    # set 印章大小 118 x 118
    opts.append(118)
    opts.append(118)
    return attach_img(opts)

def delete_page(opts):
    if len(opts) != 2:
        return False
    pos = adjust_page_pos(opts[1], doc)
    if pos is None:
        return False
    doc.delete_page(pos)
    print('[success]')
    return True

def test():
    open_(['open', 'C.pdf'])
    p = doc.load_page(0)
    #pix = p.get_pixmap(dpi = 150)
    zoom = 123 / 118
    pix = p.get_pixmap(matrix = pymupdf.Matrix(zoom, zoom))
    pix.save('z.png')
    create(['create'])
    insert_img(['', 0, 'z.png'])
    save([''])

def main():
    cmds = [
        ('cd <path>', cd_), # set work dir
        ('create', create),
        ('open <pdf-file>', open_),
        ('insert-img <page-idx> <image-file>', insert_img),
        ('insert-pdf <page-idx> <pdf-file> <pdf-page-idx>', insert_pdf), # pos can be -1, -2, ...
        ('append-pdf <pdf-file>', append_pdf),
        ('move <from-page-idx> <to-page-idx>', move), # pos can be -1, -2, ...
        ('attach-img <page-idx> <image-file> <x> <y> <width?> <height?>', attach_img),
        ('attach-yz <page-idx> <x> <y>', attach_yz),
        ('delete <page-idx>', delete_page),
        ('save', save)
    ]
    print('Work directory: ', workDir)
    print('$scan = C:\\Users\\GaoYan\\Documents\\Scanned Documents')
    print('$desktop = C:\\Users\\GaoYan\\Desktop')
    print('')
    funs = {}
    for s in cmds:
        t = s[0]
        print(t)
        t = t.split(' ')[0]
        funs[t] = s[1]
    print('--------------------')

    while True:
        opts = parse_cmd(input())
        if not opts:
            continue
        try:
            if opts[0] not in funs:
                continue
            if opts[0] in ('cd', 'create', 'open'):
                funs[opts[0]](opts)
                continue
            if doc is None:
                continue
            funcName = opts[0]
            if funcName in funs:
                funs[funcName](opts)
        except Exception as e:
            #traceback.print_exc()
            print(e)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        workDir = sys.argv[1]
    #test()
    main()
    input()