# Arminia Tischfussball: downloads the current dates image and sets it as the
# desktop background on all screens. Started hourly and at logon by the
# scheduled task that setup.ps1 creates.
# If anything goes wrong (offline, bad download) the current image stays.

$ErrorActionPreference = 'Stop'
$Url    = 'https://cnpartist.github.io/arminia-termine/termine.png'
$Folder = Join-Path ([Environment]::GetFolderPath('MyPictures')) 'Arminia Termine'
$Image  = Join-Path $Folder 'termine.png'
$Temp   = Join-Path $env:TEMP 'arminia-termine-download.png'

function Test-Png([string]$Path) {
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 1000) { return $false }
    $signature = 0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A
    for ($i = 0; $i -lt $signature.Length; $i++) {
        if ($bytes[$i] -ne $signature[$i]) { return $false }
    }
    return $true
}

$changed = $false
try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $ProgressPreference = 'SilentlyContinue'  # makes Invoke-WebRequest much faster in PowerShell 5.1
    New-Item -ItemType Directory -Force -Path $Folder | Out-Null
    Invoke-WebRequest -Uri ($Url + '?t=' + [DateTime]::UtcNow.Ticks) -OutFile $Temp -UseBasicParsing -TimeoutSec 60
    if (-not (Test-Png $Temp)) { throw 'download is not a PNG' }
    if ((-not (Test-Path $Image)) -or ((Get-FileHash $Temp).Hash -ne (Get-FileHash $Image).Hash)) {
        Move-Item -Force $Temp $Image
        $changed = $true
    } else {
        Remove-Item $Temp
    }
} catch {
    Remove-Item $Temp -ErrorAction SilentlyContinue
}

if (-not (Test-Path $Image)) { exit 0 }

# Re-apply only when the image changed or someone set another background.
$desktop = 'HKCU:\Control Panel\Desktop'
$current = (Get-ItemProperty $desktop -Name Wallpaper -ErrorAction SilentlyContinue).Wallpaper
if ($changed -or ($current -ne $Image)) {
    Set-ItemProperty $desktop -Name WallpaperStyle -Value '6'  # Fit: never crop
    Set-ItemProperty $desktop -Name TileWallpaper -Value '0'
    Set-ItemProperty 'HKCU:\Control Panel\Colors' -Name Background -Value '0 0 0'  # black bars blend in
    Add-Type -Namespace ArminiaTermine -Name Native -MemberDefinition @'
[DllImport("user32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
public static extern bool SystemParametersInfo(int uAction, int uParam, string lpvParam, int fWinIni);
[DllImport("user32.dll", SetLastError = true)]
public static extern bool SetSysColors(int cElements, int[] lpaElements, int[] lpaRgbValues);
'@
    [ArminiaTermine.Native]::SetSysColors(1, @(1), @(0)) | Out-Null  # COLOR_DESKTOP = black, now
    # SPI_SETDESKWALLPAPER = 20, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE = 3
    [ArminiaTermine.Native]::SystemParametersInfo(20, 0, $Image, 3) | Out-Null
}
exit 0
