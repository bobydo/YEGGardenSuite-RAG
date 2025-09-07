# run_refresh.ps1
$Project = "D:\YEGGardenSuite-RAG"
$Python  = "$Project\.venv\Scripts\python.exe"   # or just "python" if on PATH
$LogDir  = "$Project\logs"
$LogFile = "$LogDir\refresh.log"
$OutFile = "$LogDir\refresh.stdout"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Set-Location $Project

# Run refresh with rich logs; capture stdout+stderr
& $Python "..\refresh.py" --log-file $LogFile 2>&1 | Tee-Object -FilePath $OutFile -Append
