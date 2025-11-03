import os, shutil

def copyDistFiles():
    for d in os.listdir('dist/assets'):
        path = 'dist/assets/' + d
        dx = d.index('-')
        dd = d.index('.')
        name = d[0 : dx] + d[dd : ]
        shutil.copyfile(path, f'../YBTX_Server/dist/assets/{name}')
        print(f'copy file {d} ==> YBTX_Server/dist/assets/{name}')

def begin():
    print('compile begin...')
    # modify config.js DEBUG MODE
    f = open('src/config.js', 'r+')
    lines = f.readlines()
    f.truncate()
    lines[0] = 'const DEBUG = false; // Note: First Line Must be define DEBUG \n'
    f.seek(0, 0)
    f.writelines(lines)
    f.close()
    print('Modify DEBUG mode to false')

def end():
    # restore config.js DEBUG MODE
    f = open('src/config.js', 'r+')
    lines = f.readlines()
    lines[0] = 'const DEBUG = true; // Note: First Line Must be define DEBUG \n'
    f.seek(0, 0)
    f.truncate()
    f.writelines(lines)
    f.close()
    print('Resotore DEBUG mode to true')
    print('compile end.....')

if __name__ == '__main__':
    begin()
    os.system('npm run build')
    end()
    copyDistFiles()

