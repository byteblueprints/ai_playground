param(
    [string]$ImageName = "ai-playground-sandbox",
    [string]$ContainerName = "my-container"
)

$ErrorActionPreference = "Stop"

Write-Host "Checking Docker CLI..."
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker CLI not found. Install Docker Desktop and ensure 'docker' is on PATH."
}

Write-Host "Checking Docker daemon..."
$null = docker info 2>$null
if ($LASTEXITCODE -ne 0) {
    throw "Docker daemon is not running. Start Docker Desktop and try again."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "..")
$dockerfileDir = $projectRoot

if (-not (Test-Path $dockerfileDir)) {
    throw "Sandbox Dockerfile folder not found: $dockerfileDir"
}

Write-Host "Building image '$ImageName' from $dockerfileDir ..."
docker build -t $ImageName $dockerfileDir
if ($LASTEXITCODE -ne 0) {
    throw "Docker build failed."
}

$existing = docker ps -a --filter "name=^$ContainerName$" --format "{{.Names}}"
if ($existing -eq $ContainerName) {
    $isRunning = docker ps --filter "name=^$ContainerName$" --format "{{.Names}}"
    if ($isRunning -eq $ContainerName) {
        Write-Host "Container '$ContainerName' is already running."
    }
    else {
        Write-Host "Starting existing container '$ContainerName' ..."
        docker start $ContainerName | Out-Null
    }
}
else {
    Write-Host "Creating and starting container '$ContainerName' ..."
    docker run -d --name $ContainerName --restart unless-stopped $ImageName | Out-Null
}

if ($LASTEXITCODE -ne 0) {
    throw "Failed to start sandbox container '$ContainerName'."
}

Write-Host "Sandbox container is ready."
Write-Host "Set DOCKER_SANDBOX_CONTAINER_ID=$ContainerName in your .env if needed."
