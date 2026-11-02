# Arminia Tischfussball: Termine als Desktop-Hintergrund einrichten.
#
# In PowerShell (keine Admin-Rechte noetig):
#   irm https://cnpartist.github.io/arminia-termine/setup.ps1 | iex
#
# Legt eine geplante Aufgabe an, die das Bild bei der Anmeldung und dann
# stuendlich holt und als Hintergrund auf allen Bildschirmen setzt.
# Entfernen: irm https://cnpartist.github.io/arminia-termine/uninstall.ps1 | iex

& {
    $ErrorActionPreference = 'Stop'
    $Base       = 'https://cnpartist.github.io/arminia-termine'
    $InstallDir = Join-Path $env:LOCALAPPDATA 'ArminiaTermine'
    $Updater    = Join-Path $InstallDir 'update.ps1'
    $Image      = Join-Path ([Environment]::GetFolderPath('MyPictures')) 'Arminia Termine\termine.png'
    $TaskName   = 'Arminia Termine Hintergrund'
    $User       = "$env:USERDOMAIN\$env:USERNAME"

    Write-Host 'Arminia Termine: Einrichtung' -ForegroundColor Cyan

    [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
    $ProgressPreference = 'SilentlyContinue'
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
    Invoke-WebRequest -Uri "$Base/update.ps1" -OutFile $Updater -UseBasicParsing -TimeoutSec 60
    Write-Host "  Skript gespeichert: $Updater"

    $action = New-ScheduledTaskAction -Execute 'conhost.exe' `
        -Argument "--headless powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$Updater`""
    $hourly = New-ScheduledTaskTrigger -Once -At (Get-Date).Date -RepetitionInterval (New-TimeSpan -Hours 1)
    $principal = New-ScheduledTaskPrincipal -UserId $User -LogonType Interactive -RunLevel Limited
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
    $description = 'Holt die Termine der Tischfussball-Abteilung von arminia.de als Hintergrundbild.'
    try {
        $atLogon = New-ScheduledTaskTrigger -AtLogOn -User $User
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger @($atLogon, $hourly) `
            -Principal $principal -Settings $settings -Description $description -Force | Out-Null
        Write-Host '  Geplante Aufgabe angelegt: bei Anmeldung und stuendlich'
    } catch {
        # Some PCs only let administrators create logon triggers. Hourly alone
        # still works: missed runs start as soon as the user is logged on.
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $hourly `
            -Principal $principal -Settings $settings -Description $description -Force | Out-Null
        Write-Host '  Geplante Aufgabe angelegt: stuendlich'
    }

    Write-Host '  Lade das Bild zum ersten Mal ...'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $Updater
    if (Test-Path $Image) {
        Write-Host "  Fertig. Hintergrundbild: $Image" -ForegroundColor Green
    } else {
        Write-Host '  Das Bild konnte noch nicht geladen werden (Internet?). Die Aufgabe versucht es stuendlich weiter.' -ForegroundColor Yellow
    }

    Write-Host ''
    Write-Host 'Bildschirmschoner (optional), im Fenster das sich jetzt oeffnet:' -ForegroundColor Cyan
    Write-Host '  1. Bildschirmschoner "Fotos" auswaehlen'
    Write-Host '  2. "Einstellungen..." > "Durchsuchen" > Ordner "Bilder\Arminia Termine" > "Speichern"'
    Write-Host '  3. Wartezeit einstellen und mit "OK" bestaetigen'
    Start-Process control.exe -ArgumentList 'desk.cpl,,@screensaver'
}
