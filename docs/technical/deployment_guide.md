# Deployment Guide

© 2025 AustralMetrics SpA. All rights reserved.

## Overview

This guide provides comprehensive instructions for deploying the PASCAL NDVI Block across different environments, ensuring ISO 42001 compliance and optimal performance. The deployment process is designed for simplicity while maintaining enterprise-grade reliability.

## Prerequisites

### System Requirements

#### Minimum Requirements
- **OS**: Windows 10+, Ubuntu 18.04+, macOS 10.15+
- **RAM**: 4GB available memory
- **Storage**: 10GB free space (5GB for software + 5GB for processing)
- **CPU**: Dual-core processor (x64 architecture)
- **Python**: Version 3.7 or higher

#### Recommended Requirements
- **OS**: Windows 11, Ubuntu 20.04+, macOS 12+
- **RAM**: 8GB+ available memory
- **Storage**: 50GB+ free space (SSD preferred)
- **CPU**: Quad-core processor or better
- **Python**: Version 3.9 or higher

#### Network Requirements
- Internet access for initial setup and dependency installation
- Corporate firewall exceptions for Python package repositories (if applicable)

### Pre-Installation Checklist

```bash
# Check Python version
python --version  # Should be 3.7+

# Check available memory
# Windows:
systeminfo | findstr "Available Physical Memory"
# Linux/macOS:
free -h  # or: vm_stat (macOS)

# Check disk space
# Windows:
dir c:\ 
# Linux/macOS:
df -h

# Verify Git installation (if cloning from repository)
git --version
```

## Installation Methods

### Method 1: Production Deployment (Recommended)

#### Step 1: Environment Preparation

```bash
# Create dedicated user (Linux/macOS - optional but recommended)
sudo useradd -m -s /bin/bash pascal_ndvi
sudo usermod -aG sudo pascal_ndvi  # If admin access needed

# Create application directory
mkdir -p /opt/pascal-ndvi-block  # Linux/macOS
# or
mkdir C:\opt\pascal-ndvi-block   # Windows

# Set proper permissions (Linux/macOS)
sudo chown pascal_ndvi:pascal_ndvi /opt/pascal-ndvi-block
```

#### Step 2: Repository Setup

```bash
# Clone repository
cd /opt  # or C:\opt on Windows
git clone https://github.com/australmetrics/pascal-ndvi-block.git
cd pascal-ndvi-block

# Verify repository integrity
git verify-commit HEAD  # If GPG signatures are used
```

#### Step 3: Python Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m src.main --help
```

#### Step 4: Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
# Linux/macOS:
nano .env
# Windows:
notepad .env
```

**Required `.env` Configuration**:
```bash
# User identification for audit logs
USERNAME=production_user

# Logging configuration
LOG_LEVEL=INFO
LOG_RETENTION_DAYS=90

# Processing configuration
DEFAULT_OUTPUT_DIR=results
TEMP_DIR=/tmp/pascal_ndvi  # Linux/macOS
# TEMP_DIR=C:\temp\pascal_ndvi  # Windows

# Performance tuning
MAX_MEMORY_MB=4096
PARALLEL_PROCESSING=true
```

#### Step 5: Directory Structure Setup

```bash
# Create required directories
mkdir -p data results logs backup temp

# Set permissions (Linux/macOS)
chmod 755 data results
chmod 750 logs backup  # Restricted access for audit logs
chmod 700 temp         # Temporary files

# Windows equivalent (run as administrator):
# icacls data /grant Users:F
# icacls results /grant Users:F
# icacls logs /grant Administrators:F
# icacls backup /grant Administrators:F
```

#### Step 6: Validation Testing

```bash
# Run system validation
python -m src.main validate-system

# Test with sample data (if available)
python -m src.main indices --image=data/sample.tif --output=results/test

# Check log generation
ls -la results/logs/  # Linux/macOS
# dir results\logs\   # Windows
```

### Method 2: Development Deployment

#### Quick Development Setup

```bash
# Clone and setup
git clone https://github.com/australmetrics/pascal-ndvi-block.git
cd pascal-ndvi-block

# Create development environment
python -m venv dev_env
source dev_env/bin/activate  # Linux/macOS
# dev_env\Scripts\activate    # Windows

# Install with development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Setup pre-commit hooks (if using)
pre-commit install

# Create development configuration
cp .env.example .env.dev
# Edit .env.dev with development settings
```

#### Development Configuration

```bash
# .env.dev example
USERNAME=developer
LOG_LEVEL=DEBUG
DEFAULT_OUTPUT_DIR=dev_results
TEMP_DIR=./temp
MAX_MEMORY_MB=2048
PARALLEL_PROCESSING=false  # Easier debugging
```

### Method 3: Container Deployment

#### Docker Setup (Future Enhancement)

```dockerfile
# Dockerfile example for future implementation
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

CMD ["python", "-m", "src.main"]
```

## Environment-Specific Configurations

### Windows Deployment

#### PowerShell Setup Script

```powershell
# PowerShell deployment script
$ErrorActionPreference = "Stop"

# Check prerequisites
$pythonVersion = python --version 2>$null
if (-not $pythonVersion) {
    Write-Error "Python not found. Please install Python 3.7+"
    exit 1
}

# Create installation directory
$installDir = "C:\Program Files\PASCAL-NDVI-Block"
New-Item -ItemType Directory -Path $installDir -Force

# Download and extract (modify URL as needed)
# Or use git clone if Git is available
git clone https://github.com/australmetrics/pascal-ndvi-block.git $installDir

# Setup virtual environment
Set-Location $installDir
python -m venv venv
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
pip install -r requirements.txt

# Create Windows service (optional)
# New-Service -Name "PASCAL-NDVI" -BinaryPathName "$installDir\venv\Scripts\python.exe -m src.main service"

Write-Host "Installation completed successfully"
Write-Host "Location: $installDir"
Write-Host "To activate: $installDir\venv\Scripts\activate"
```

#### Windows Service Configuration

```xml
<!-- Windows Service configuration (if needed) -->
<configuration>
  <appSettings>
    <add key="InstallPath" value="C:\Program Files\PASCAL-NDVI-Block" />
    <add key="LogPath" value="C:\ProgramData\PASCAL-NDVI\Logs" />
    <add key="DataPath" value="C:\ProgramData\PASCAL-NDVI\Data" />
  </appSettings>
</configuration>
```

### Linux Deployment

#### Systemd Service Setup

```bash
# Create service file
sudo nano /etc/systemd/system/pascal-ndvi.service
```

```ini
[Unit]
Description=PASCAL NDVI Block Service
After=network.target

[Service]
Type=simple
User=pascal_ndvi
Group=pascal_ndvi
WorkingDirectory=/opt/pascal-ndvi-block
Environment=PATH=/opt/pascal-ndvi-block/venv/bin
ExecStart=/opt/pascal-ndvi-block/venv/bin/python -m src.main service
Restart=on-failure
RestartSec=5

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pascal-ndvi

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/opt/pascal-ndvi-block/results /opt/pascal-ndvi-block/logs

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable pascal-ndvi.service
sudo systemctl start pascal-ndvi.service

# Check service status
sudo systemctl status pascal-ndvi.service
```

#### Ubuntu/Debian Package Installation

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# Install geospatial libraries
sudo apt install -y gdal-bin libgdal-dev python3-gdal
sudo apt install -y libproj-dev proj-data proj-bin
sudo apt install -y libgeos-dev

# Create application user
sudo useradd -r -m -s /bin/bash pascal_ndvi
sudo mkdir -p /opt/pascal-ndvi-block
sudo chown pascal_ndvi:pascal_ndvi /opt/pascal-ndvi-block
```

#### CentOS/RHEL Deployment

```bash
# Install system dependencies
sudo yum update -y
sudo yum install -y python3 python3-pip git

# Install EPEL repository for additional packages
sudo yum install -y epel-release

# Install geospatial libraries
sudo yum install -y gdal gdal-devel gdal-python3
sudo yum install -y proj proj-devel geos geos-devel

# Setup application
sudo useradd -r -m pascal_ndvi
sudo mkdir -p /opt/pascal-ndvi-block
sudo chown pascal_ndvi:pascal_ndvi /opt/pascal-ndvi-block
```

### macOS Deployment

#### Homebrew Setup

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.9 gdal proj geos

# Create application directory
sudo mkdir -p /opt/pascal-ndvi-block
sudo chown $(whoami):admin /opt/pascal-ndvi-block

# Clone and setup
cd /opt
git clone https://github.com/australmetrics/pascal-ndvi-block.git
cd pascal-ndvi-block

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### macOS LaunchDaemon (Service)

```xml
<!-- /Library/LaunchDaemons/com.australmetrics.pascal-ndvi.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.australmetrics.pascal-ndvi</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/pascal-ndvi-block/venv/bin/python</string>
        <string>-m</string>
        <string>src.main</string>
        <string>service</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/opt/pascal-ndvi-block</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/opt/pascal-ndvi-block/logs/service.log</string>
    <key>StandardErrorPath</key>
    <string>/opt/pascal-ndvi-block/logs/service_error.log</string>
</dict>
</plist>
```

```bash
# Load service
sudo launchctl load /Library/LaunchDaemons/com.australmetrics.pascal-ndvi.plist
sudo launchctl start com.australmetrics.pascal-ndvi
```

## Performance Optimization

### Memory Optimization

```bash
# Calculate optimal memory settings based on system RAM
total_ram=$(free -m | awk 'NR==2{printf "%.0f", $2}')  # Linux
# total_ram=$(sysctl hw.memsize | awk '{print $2/1024/1024}')  # macOS

# Set memory limits in .env
echo "MAX_MEMORY_MB=$((total_ram * 60 / 100))" >> .env  # Use 60% of RAM
echo "CHUNK_SIZE_MB=$((total_ram * 10 / 100))" >> .env   # 10% chunk size
```

### Storage Optimization

```bash
# Create optimized directory structure
mkdir -p results/{indices,clipped,metadata,logs,backup}
mkdir -p temp/{processing,cache}

# Set up log rotation
# Linux - using logrotate
cat > /etc/logrotate.d/pascal-ndvi << EOF
/opt/pascal-ndvi-block/results/logs/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 644 pascal_ndvi pascal_ndvi
    postrotate
        systemctl reload pascal-ndvi 2>/dev/null || true
    endscript
}
EOF
```

### Network Optimization

```bash
# Configure proxy settings if behind corporate firewall
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1,.company.com

# Add to .env file
echo "HTTP_PROXY=http://proxy.company.com:8080" >> .env
echo "HTTPS_PROXY=http://proxy.company.com:8080" >> .env
```

## Security Configuration

### File Permissions

```bash
# Linux/macOS security setup
# Application files - read-only for application user
chmod -R 755 /opt/pascal-ndvi-block/src
chmod -R 644 /opt/pascal-ndvi-block/src/*.py

# Configuration files - restricted access
chmod 600 /opt/pascal-ndvi-block/.env
chown pascal_ndvi:pascal_ndvi /opt/pascal-ndvi-block/.env

# Data directories - controlled access
chmod 750 /opt/pascal-ndvi-block/data
chmod 755 /opt/pascal-ndvi-block/results
chmod 700 /opt/pascal-ndvi-block/logs  # Audit logs - restricted

# Temporary directories - secure
chmod 700 /opt/pascal-ndvi-block/temp
```

### Windows Security

```powershell
# Windows ACL configuration
# Restrict configuration file access
icacls "C:\opt\pascal-ndvi-block\.env" /grant Administrators:F /inheritance:r

# Set log directory permissions
icacls "C:\opt\pascal-ndvi-block\logs" /grant Administrators:F /grant "SYSTEM:F" /inheritance:r

# Application directory permissions
icacls "C:\opt\pascal-ndvi-block" /grant Users:RX /grant Administrators:F
```

### Firewall Configuration

```bash
# Linux - UFW rules (if needed for service mode)
sudo ufw allow from 192.168.1.0/24 to any port 8080  # Internal network only
sudo ufw deny 8080  # Deny external access

# Windows Firewall (if running as service)
netsh advfirewall firewall add rule name="PASCAL NDVI Block" dir=in action=allow protocol=TCP localport=8080 remoteip=192.168.1.0/24
```

## Monitoring and Maintenance

### Health Check Script

```bash
#!/bin/bash
# health_check.sh

INSTALL_DIR="/opt/pascal-ndvi-block"
LOG_FILE="$INSTALL_DIR/logs/health_check.log"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check service status
check_service() {
    if systemctl is-active --quiet pascal-ndvi; then
        log_message "INFO: Service is running"
        return 0
    else
        log_message "ERROR: Service is not running"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    local usage=$(df "$INSTALL_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -gt 80 ]; then
        log_message "WARNING: Disk usage is ${usage}%"
        return 1
    else
        log_message "INFO: Disk usage is ${usage}%"
        return 0
    fi
}

# Check memory usage
check_memory() {
    local mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$mem_usage" -gt 90 ]; then
        log_message "WARNING: Memory usage is ${mem_usage}%"
        return 1
    else
        log_message "INFO: Memory usage is ${mem_usage}%"
        return 0
    fi
}

# Check log file sizes
check_log_files() {
    local max_size=104857600  # 100MB
    for log in "$INSTALL_DIR"/logs/*.log; do
        if [ -f "$log" ]; then
            local size=$(stat -c%s "$log")
            if [ "$size" -gt "$max_size" ]; then
                log_message "WARNING: Log file $log is large (${size} bytes)"
            fi
        fi
    done
}

# Run all checks
main() {
    log_message "Starting health check"
    
    local status=0
    check_service || status=1
    check_disk_space || status=1
    check_memory || status=1
    check_log_files
    
    if [ $status -eq 0 ]; then
        log_message "Health check completed successfully"
    else
        log_message "Health check completed with warnings/errors"
    fi
    
    return $status
}

main "$@"
```

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

INSTALL_DIR="/opt/pascal-ndvi-block"
BACKUP_DIR="/backup/pascal-ndvi"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup configuration
tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" \
    -C "$INSTALL_DIR" .env requirements.txt

# Backup logs (last 7 days)
find "$INSTALL_DIR/logs" -name "*.log" -mtime -7 \
    -exec tar -rzf "$BACKUP_DIR/logs_backup_$DATE.tar.gz" {} +

# Backup results metadata (not the large image files)
find "$INSTALL_DIR/results" -name "*.json" -o -name "*.txt" \
    -exec tar -rzf "$BACKUP_DIR/metadata_backup_$DATE.tar.gz" {} +

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "*backup*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Monitoring Cron Jobs

```bash
# Add to crontab (crontab -e)
# Health check every hour
0 * * * * /opt/pascal-ndvi-block/scripts/health_check.sh

# Daily backup at 2 AM
0 2 * * * /opt/pascal-ndvi-block/scripts/backup.sh

# Weekly log cleanup
0 3 * * 0 find /opt/pascal-ndvi-block/temp -type f -mtime +7 -delete

# Monthly disk usage report
0 0 1 * * df -h /opt/pascal-ndvi-block > /opt/pascal-ndvi-block/logs/disk_usage_$(date +\%Y\%m).log
```

## Troubleshooting Deployment Issues

### Common Installation Problems

#### Python Version Issues
```bash
# Problem: Wrong Python version
# Solution: Use specific Python version
python3.9 -m venv venv
# or install specific version
sudo apt install python3.9 python3.9-venv  # Ubuntu
brew install python@3.9  # macOS
```

#### Missing System Dependencies
```bash
# Problem: GDAL/GEOS not found
# Linux solution:
sudo apt install gdal-bin libgdal-dev
sudo apt install libgeos-dev libproj-dev

# macOS solution:
brew install gdal geos proj

# Windows solution: Use conda
conda install -c conda-forge gdal geos proj
```

#### Permission Errors
```bash
# Problem: Permission denied errors
# Solution: Fix ownership and permissions
sudo chown -R pascal_ndvi:pascal_ndvi /opt/pascal-ndvi-block
chmod -R 755 /opt/pascal-ndvi-block
chmod 600 /opt/pascal-ndvi-block/.env
```

#### Memory Issues
```bash
# Problem: Out of memory errors
# Solution: Adjust memory settings in .env
MAX_MEMORY_MB=2048  # Reduce if system has limited RAM
CHUNK_SIZE_MB=256   # Smaller chunks for processing
```

### Verification Commands

```bash
# Test basic functionality
python -m src.main --version

# Test with verbose output
python -m src.main indices --image=data/test.tif --output=results/test --verbose

# Check log generation
ls -la results/logs/
cat results/logs/pascal_ndvi_*.log | tail -20

# Test system resources
python -c "
import psutil
print(f'Available RAM: {psutil.virtual_memory().available / 1024**3:.2f} GB')
print(f'Available disk: {psutil.disk_usage(\"/\").free / 1024**3:.2f} GB')
"
```

## Deployment Checklist

### Pre-Deployment
- [ ] System requirements verified
- [ ] Network access confirmed
- [ ] Backup system in place
- [ ] Security requirements reviewed
- [ ] User accounts created
- [ ] Directory permissions planned

### During Deployment
- [ ] Repository cloned successfully
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Configuration files created
- [ ] Directory structure established
- [ ] Permissions set correctly

### Post-Deployment
- [ ] Basic functionality tested
- [ ] Log generation verified
- [ ] Service configured (if applicable)
- [ ] Monitoring setup complete
- [ ] Backup scripts deployed
- [ ] Health checks working
- [ ] Documentation updated

### Production Readiness
- [ ] Performance testing completed
- [ ] Security audit passed
- [ ] Disaster recovery tested
- [ ] User training completed
- [ ] Support procedures documented
- [ ] Maintenance schedule established

## Support and Maintenance

### Regular Maintenance Tasks

**Daily**:
- Monitor log files for errors
- Check disk space usage
- Verify service status

**Weekly**:
- Review processing statistics
- Clean temporary files
- Update system packages

**Monthly**:
- Security updates
- Performance review
- Backup verification
- User access audit

### Emergency Procedures

#### Service Recovery
```bash
# If service fails
sudo systemctl status pascal-ndvi  # Check status
sudo journalctl -u pascal-ndvi -f  # Check logs
sudo systemctl restart pascal-ndvi  # Restart service
```

#### Data Recovery
```bash
# Restore from backup
cd /backup/pascal-ndvi
tar -xzf config_backup_YYYYMMDD_HHMMSS.tar.gz -C /opt/pascal-ndvi-block/
sudo systemctl restart pascal-ndvi
```

### Contact Information

For deployment support:
- **Technical Issues**: AustralMetrics SpA Development Team
- **System Administration**: Internal IT Department
- **Security Concerns**: Information Security Team
- **Business Continuity**: Operations Manager

This deployment guide ensures consistent, secure, and maintainable installations across all supported platforms while maintaining ISO 42001 compliance requirements.