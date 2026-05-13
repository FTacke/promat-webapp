$edgePath = (Get-Command msedge.exe -ErrorAction SilentlyContinue).Source
if (-not $edgePath) {
    $paths = @(
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
        "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe"
    )
    foreach ($p in $paths) {
        if (Test-Path $p) {
            $edgePath = $p
            break
        }
    }
}
if (-not $edgePath) { throw "Edge not found" }

$routes = @(
    "/de/teaching", "/de/teaching/spanish", "/de/teaching/english",
    "/de/teaching/spanish/final-r", "/en/teaching", "/en/teaching/spanish", "/de/sample"
)
$outputDir = "C:\dev\promat\tmp\ui-qa\2026-05-11-teaching-polish-followup"
if (-not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir -Force }

foreach ($route in $routes) {
    $name = $route.Replace("/", "_").TrimStart("_")
    $url = "http://127.0.0.1:8010$route"
    
    # Save HTML
    Invoke-WebRequest -Uri $url -OutFile "$outputDir\$name.html" -ErrorAction SilentlyContinue
    
    # Absolute paths for screenshot argument
    $desktopPath = "$outputDir\$name-desktop.png"
    $mobilePath = "$outputDir\$name-mobile.png"
    
    Write-Host "Capturing $url..."
    Start-Process $edgePath "--headless=new --screenshot=`"$desktopPath`" --window-size=1440,1080 $url" -Wait
    Start-Process $edgePath "--headless=new --screenshot=`"$mobilePath`" --window-size=390,844 $url" -Wait
}
Get-ChildItem $outputDir
