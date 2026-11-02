# Arminia Tischfussball: Termine-Hintergrund wieder entfernen.
#   irm https://cnpartist.github.io/arminia-termine/uninstall.ps1 | iex

& {
    $TaskName = 'Arminia Termine Hintergrund'
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force (Join-Path $env:LOCALAPPDATA 'ArminiaTermine') -ErrorAction SilentlyContinue
    Write-Host 'Arminia Termine entfernt: Das Bild wird nicht mehr aktualisiert.' -ForegroundColor Green
    Write-Host 'Das aktuelle Hintergrundbild bleibt, bis du ein anderes einstellst.'
    Write-Host 'Den Ordner "Bilder\Arminia Termine" kannst du danach loeschen.'
}
