rd /s /q "pyinstaller\gacp_gui"

rd /s /q "pyinstaller\gacp_cli"

pyinstaller.exe --distpath "pyinstaller" --workpath "pyinstaller\work" --icon "src\icon.ico" --add-data "src\icon.png;." --windowed --noconfirm --name gacp_gui src\start.py 

pyinstaller.exe --distpath "pyinstaller" --workpath "pyinstaller\work" --icon "src\icon_cli.ico" --noconfirm --name gacp_cli src\cli.py 

pause