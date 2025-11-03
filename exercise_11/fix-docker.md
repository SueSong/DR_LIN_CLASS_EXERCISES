# Fixing Docker Connection Issues

## Problem
You're getting: `request returned 500 Internal Server Error for API route`

This means Docker Desktop isn't fully running or the Docker daemon is stuck.

## Solutions (Try in order):

### Solution 1: Restart Docker Desktop
1. **Close Docker Desktop completely:**
   - Right-click Docker Desktop icon in system tray
   - Click "Quit Docker Desktop"
   - Wait 10 seconds

2. **Start Docker Desktop again:**
   - Open Docker Desktop from Start menu
   - Wait for it to fully start (whale icon stops animating)
   - This may take 30-60 seconds

3. **Test:**
   ```bash
   docker ps
   ```
   Should show containers (or empty list if none running)

### Solution 2: Restart Docker Service (if Solution 1 doesn't work)
1. Open PowerShell as Administrator
2. Run:
   ```powershell
   Restart-Service docker
   ```
   If that doesn't work, try:
   ```powershell
   net stop com.docker.service
   net start com.docker.service
   ```

### Solution 3: Full Docker Desktop Reset
1. Quit Docker Desktop
2. Open Task Manager (Ctrl+Shift+Esc)
3. End all Docker-related processes:
   - `Docker Desktop`
   - `com.docker.backend`
   - Any other Docker processes
4. Start Docker Desktop again
5. Wait for full startup

### Solution 4: Restart Windows (last resort)
Sometimes Windows networking/Docker integration gets stuck and a reboot fixes it.

## After Docker is Working

Once `docker ps` works, restart observability services:

```bash
cd exercise_11
docker-compose down
docker-compose up -d
```

Wait 15 seconds, then check:
- http://localhost:16686 (Jaeger)
- http://localhost:3001 (Grafana)

## Check Status

After Docker Desktop starts, verify:
```bash
docker ps                    # Should work without errors
docker-compose ps            # Check your containers
docker ps -a                 # See all containers (including stopped)
```

