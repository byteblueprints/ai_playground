param(
    [string]$ContainerName = "my-container"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI not found."
}

$exists = docker ps -a --filter "name=^$ContainerName$" --format "{{.Names}}"
if ($exists -ne $ContainerName) {
    Write-Host "Container '$ContainerName' does not exist."
    exit 0
}

$running = docker ps --filter "name=^$ContainerName$" --format "{{.Names}}"
if ($running -eq $ContainerName) {
    Write-Host "Stopping '$ContainerName' ..."
    docker stop $ContainerName | Out-Null
}
else {
    Write-Host "Container '$ContainerName' is already stopped."
}

Write-Host "Done."
