import cx_Freeze # pip install cx_Freeze
import os

#os.environ['key'] = val

cx_Freeze.setup(
    name = 'd-server',
    version = '1.0',
    description = 'download server pages server',
    executables = [cx_Freeze.Executable('d-server.py', target_name = 'd-server.exe')]
)


# 打包
# python s-setup.py setup