import cx_Freeze # pip install cx_Freeze
import os

#os.environ['key'] = val

cx_Freeze.setup(
    name = 's-server',
    version = '1.0',
    description = 'server pages server',
    executables = [cx_Freeze.Executable('s-server.py', target_name = 's-server.exe')]
)


# 打包
# python d-setup.py setup