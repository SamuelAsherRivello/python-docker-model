$ErrorActionPreference = 'Stop'
$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))

$listeners = Get-NetTCPConnection -LocalPort 8501 -State Listen -ErrorAction SilentlyContinue |
    Sort-Object -Property OwningProcess -Unique
$projectPython = [IO.Path]::GetFullPath((Join-Path $ProjectRoot '.venv\Scripts\python.exe'))

foreach ($listener in $listeners) {
    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
    if (-not $process) { continue }

    $command = [string]$process.CommandLine
    $isThisApp = $command.IndexOf($projectPython, [StringComparison]::OrdinalIgnoreCase) -ge 0 -and
        $command -match 'streamlit\s+run\s+' -and
        $command.IndexOf('main.py', [StringComparison]::OrdinalIgnoreCase) -ge 0
    if (-not $isThisApp) {
        Write-Error "Port 8501 is in use by another process (PID $($listener.OwningProcess))."
        exit 1
    }

    Write-Host "Stopping previous Streamlit process (PID $($listener.OwningProcess))..."
    Stop-Process -Id $listener.OwningProcess -Force
}
