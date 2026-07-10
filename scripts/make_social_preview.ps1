$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

$repo = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$assets = Join-Path $repo "docs\assets"
$output = Join-Path $assets "repairloop-social-preview.png"

New-Item -ItemType Directory -Force -Path $assets | Out-Null

$width = 1280
$height = 640
$bg = [System.Drawing.Color]::FromArgb(13, 17, 23)
$panel = [System.Drawing.Color]::FromArgb(22, 27, 34)
$border = [System.Drawing.Color]::FromArgb(48, 54, 61)
$text = [System.Drawing.Color]::FromArgb(230, 237, 243)
$muted = [System.Drawing.Color]::FromArgb(139, 148, 158)
$green = [System.Drawing.Color]::FromArgb(63, 185, 80)
$red = [System.Drawing.Color]::FromArgb(248, 81, 73)
$blue = [System.Drawing.Color]::FromArgb(88, 166, 255)
$yellow = [System.Drawing.Color]::FromArgb(210, 153, 34)
$orange = [System.Drawing.Color]::FromArgb(255, 107, 74)
$purple = [System.Drawing.Color]::FromArgb(188, 140, 255)

$titleFont = New-Object System.Drawing.Font("Segoe UI", 74, [System.Drawing.FontStyle]::Bold)
$subtitleFont = New-Object System.Drawing.Font("Segoe UI", 32, [System.Drawing.FontStyle]::Regular)
$loopFont = New-Object System.Drawing.Font("Segoe UI", 30, [System.Drawing.FontStyle]::Bold)
$footerFont = New-Object System.Drawing.Font("Segoe UI", 23, [System.Drawing.FontStyle]::Regular)
$monoFont = New-Object System.Drawing.Font("Consolas", 23, [System.Drawing.FontStyle]::Regular)
$smallFont = New-Object System.Drawing.Font("Segoe UI", 18, [System.Drawing.FontStyle]::Bold)

function New-Brush($color) {
    return New-Object System.Drawing.SolidBrush($color)
}

function Draw-RoundRect($graphics, $brush, $pen, [int]$x, [int]$y, [int]$w, [int]$h, [int]$r) {
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $path.AddArc($x, $y, $r, $r, 180, 90)
    $path.AddArc($x + $w - $r, $y, $r, $r, 270, 90)
    $path.AddArc($x + $w - $r, $y + $h - $r, $r, $r, 0, 90)
    $path.AddArc($x, $y + $h - $r, $r, $r, 90, 90)
    $path.CloseFigure()
    if ($brush -ne $null) { $graphics.FillPath($brush, $path) }
    if ($pen -ne $null) { $graphics.DrawPath($pen, $path) }
    $path.Dispose()
}

$bitmap = New-Object System.Drawing.Bitmap($width, $height)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
$graphics.Clear($bg)

$graphics.FillEllipse((New-Brush ([System.Drawing.Color]::FromArgb(42, 255, 107, 74))), -130, -190, 620, 620)
$graphics.FillEllipse((New-Brush ([System.Drawing.Color]::FromArgb(24, 88, 166, 255))), 890, 380, 520, 520)
$graphics.FillEllipse((New-Brush ([System.Drawing.Color]::FromArgb(20, 188, 140, 255))), 980, -150, 360, 360)

$graphics.DrawString("RepairLoop", $titleFont, (New-Brush $orange), 76, 58)
$graphics.DrawString("Broken Python command → verified run", $subtitleFont, (New-Brush $text), 82, 160)
$graphics.DrawString("Run  →  Capture  →  Repair  →  Verify", $loopFont, (New-Brush $green), 84, 235)
$graphics.DrawString("Local-first. Dry-run by default. No API key. No source upload.", $footerFont, (New-Brush $muted), 84, 548)

Draw-RoundRect $graphics (New-Brush ([System.Drawing.Color]::FromArgb(38, $blue.R, $blue.G, $blue.B))) (New-Object System.Drawing.Pen($blue, 2)) 84 330 260 46 22
$graphics.DrawString("pip install repairloop", $smallFont, (New-Brush $text), 105, 340)

Draw-RoundRect $graphics (New-Brush $panel) (New-Object System.Drawing.Pen($border, 2)) 742 80 450 410 20
$graphics.FillEllipse((New-Brush $red), 770, 105, 14, 14)
$graphics.FillEllipse((New-Brush $yellow), 794, 105, 14, 14)
$graphics.FillEllipse((New-Brush $green), 818, 105, 14, 14)

$terminalLines = @(
    @{ Text = "> python app.py"; Color = $blue },
    @{ Text = "FileNotFoundError"; Color = $red },
    @{ Text = "> repair-loop repair"; Color = $blue },
    @{ Text = "[PREVIEW] safe fix"; Color = $yellow },
    @{ Text = "> repair-loop --apply"; Color = $blue },
    @{ Text = "[VERIFY] success"; Color = $green }
)
$y = 150
foreach ($line in $terminalLines) {
    $graphics.DrawString($line.Text, $monoFont, (New-Brush $line.Color), 778, $y)
    $y += 50
}

$bitmap.Save($output, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()

Write-Output $output
