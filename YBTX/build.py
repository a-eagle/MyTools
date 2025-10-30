import os, shutil

for d in os.listdir('dist/assets'):
    path = 'dist/assets/' + d
    dx = d.index('-')
    dd = d.index('.')
    name = d[0 : dx] + d[dd : ]
    shutil.copyfile(f'dist/assets/{d}', f'../YBTX_Server/dist/assets/{name}')
