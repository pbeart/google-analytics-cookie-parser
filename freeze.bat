rd /s /q "pyinstaller\gacp_gui"

rd /s /q "pyinstaller\gacp_cli"

"C:\Users\verya\AppData\Local\Programs\Python\Python37-32\scripts\pyinstaller.exe" --distpath "pyinstaller" --workpath "pyinstaller\work" --icon "src\icon.ico" --add-data "src\icon.png;." --windowed --noconfirm --name gacp_gui src\start.py 

"C:\Users\verya\AppData\Local\Programs\Python\Python37-32\scripts\pyinstaller.exe" --distpath "pyinstaller" --workpath "pyinstaller\work" --icon "src\icon_cli.ico" --noconfirm --name gacp_cli src\cli.py 

pause