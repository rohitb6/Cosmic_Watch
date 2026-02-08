#####################################################################################
# Cosmic Watch - AWS Deployment Script for Windows PowerShell
# This script automates the entire AWS infrastructure setup and deployment
#
# Usage: .\aws\deploy.ps1 -Environment production
#####################################################################################

param(
    [Parameter(Mandatory=$false)]
    [string]$Environment = "production",
    
    [Parameter(Mandatory=$false)]
    [string]$AWSRegion = "us-east-1"
)

# Configuration
$ErrorActionPreference = "Stop"
$WarningPreference = "SilentlyContinue"

$ProjectDir = Split-Path -Parent $PSScriptRoot
$StackName = "$Environment-cosmic-watch-stack"

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
    exit 1
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Check-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check AWS CLI
    $awsCli = Get-Command aws -ErrorAction SilentlyContinue
    if (-not $awsCli) {
        Write-Error-Custom "AWS CLI not found. Download from: https://aws.amazon.com/cli/"
    }
    
    # Check Docker
    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if (-not $docker) {
        Write-Error-Custom "Docker not found. Download from: https://www.docker.com/"
    }
    
    # Check AWS credentials
    try {
        $null = aws sts get-caller-identity
    }
    catch {
        Write-Error-Custom "AWS credentials not configured. Run: aws configure"
    }
    
    Write-Success "All prerequisites met"
}

function Get-AWSAccountId {
    $accountId = aws sts get-caller-identity --query Account --output text
    return $accountId
}

function Create-Secrets {
    Write-Info "Creating AWS Secrets Manager secrets..."
    
    # Get passwords securely
    $dbPassword = Read-Host "Enter RDS password (min 12 chars)" -AsSecureString
    $dbPasswordPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($dbPassword)
    )
    
    $jwtSecret = Read-Host "Enter JWT secret key (min 32 chars)" -AsSecureString
    $jwtSecretPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($jwtSecret)
    )
    
    $domainName = Read-Host "Enter your domain name (or press Enter for ALB DNS)"
    
    Write-Info "Storing secrets in AWS Secrets Manager..."
    
    try {
        aws secretsmanager create-secret `
            --name cosmic-watch/db-password `
            --secret-string $dbPasswordPlain `
            --region $AWSRegion 2>&1 | Out-Null
    }
    catch {
        aws secretsmanager update-secret `
            --secret-id cosmic-watch/db-password `
            --secret-string $dbPasswordPlain `
            --region $AWSRegion 2>&1 | Out-Null
    }
    
    try {
        aws secretsmanager create-secret `
            --name cosmic-watch/jwt-secret `
            --secret-string "{`"jwt_secret_key`":`"$jwtSecretPlain`"}" `
            --region $AWSRegion 2>&1 | Out-Null
    }
    catch {
        aws secretsmanager update-secret `
            --secret-id cosmic-watch/jwt-secret `
            --secret-string "{`"jwt_secret_key`":`"$jwtSecretPlain`"}" `
            --region $AWSRegion 2>&1 | Out-Null
    }
    
    Write-Success "Secrets stored successfully"
    
    return $dbPasswordPlain
}

function Build-DockerImages {
    Write-Info "Building Docker images..."
    
    $accountId = Get-AWSAccountId
    $ecrRegistry = "$accountId.dkr.ecr.$AWSRegion.amazonaws.com"
    
    # Create ECR repositories
    Write-Info "Creating ECR repositories..."
    
    try {
        aws ecr create-repository `
            --repository-name cosmic-watch/backend `
            --region $AWSRegion 2>&1 | Out-Null
    }
    catch { }
    
    try {
        aws ecr create-repository `
            --repository-name cosmic-watch/frontend `
            --region $AWSRegion 2>&1 | Out-Null
    }
    catch { }
    
    # Login to ECR
    Write-Info "Logging in to AWS ECR..."
    aws ecr get-login-password --region $AWSRegion | `
        docker login --username AWS --password-stdin $ecrRegistry
    
    # Build backend
    Write-Info "Building backend Docker image..."
    Push-Location "$ProjectDir\backend"
    docker build -t "$ecrRegistry/cosmic-watch/backend:latest" .
    Pop-Location
    
    # Build frontend
    Write-Info "Building frontend Docker image..."
    Push-Location "$ProjectDir\frontend"
    docker build -t "$ecrRegistry/cosmic-watch/frontend:latest" .
    Pop-Location
    
    # Push images
    Write-Info "Pushing images to ECR..."
    docker push "$ecrRegistry/cosmic-watch/backend:latest"
    docker push "$ecrRegistry/cosmic-watch/frontend:latest"
    
    Write-Success "Docker images built and pushed successfully"
}

function Deploy-CloudFormation {
    param(
        [string]$DbPassword,
        [string]$JwtSecret
    )
    
    Write-Info "Deploying CloudFormation stack..."
    
    aws cloudformation deploy `
        --template-file "$ProjectDir\aws\cloudformation-template.yaml" `
        --stack-name $StackName `
        --parameter-overrides `
            EnvironmentName=$Environment `
            DBPassword=$DbPassword `
            JWTSecretKey=$JwtSecret `
        --capabilities CAPABILITY_NAMED_IAM `
        --region $AWSRegion `
        --no-fail-on-empty-changeset
    
    Write-Success "CloudFormation stack deployed successfully"
}

function Get-StackOutputs {
    Write-Info "Retrieving stack outputs..."
    
    aws cloudformation describe-stacks `
        --stack-name $StackName `
        --region $AWSRegion `
        --query 'Stacks[0].Outputs' `
        --output table
}

function Deployment-Summary {
    Write-Info "Retrieving deployment summary..."
    
    $albDns = aws cloudformation describe-stacks `
        --stack-name $StackName `
        --region $AWSRegion `
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' `
        --output text
    
    Write-Host ""
    Write-Host "======================== DEPLOYMENT SUMMARY ========================" -ForegroundColor Cyan
    Write-Host "Environment: $Environment"
    Write-Host "CloudFormation Stack: $StackName"
    Write-Host "AWS Region: $AWSRegion"
    Write-Host ""
    Write-Host "Application URL: http://$albDns" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:"
    Write-Host "1. Point your domain to: $albDns"
    Write-Host "2. Setup SSL/TLS certificate using AWS Certificate Manager"
    Write-Host "3. Update ALB listener to use HTTPS"
    Write-Host ""
    Write-Host "For detailed information, run:"
    Write-Host "  aws cloudformation describe-stacks --stack-name $StackName --region $AWSRegion"
    Write-Host ""
    Write-Host "To view logs:"
    Write-Host "  aws logs tail /ecs/$($Environment)-cosmic-watch-backend --follow"
    Write-Host "  aws logs tail /ecs/$($Environment)-cosmic-watch-frontend --follow"
    Write-Host "====================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Main {
    Write-Host ""
    Write-Host "╔═════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║   Cosmic Watch - AWS Deployment Script (PowerShell)    ║" -ForegroundColor Cyan
    Write-Host "║   Environment: $Environment" -ForegroundColor Cyan
    Write-Host "║   Region: $AWSRegion" -ForegroundColor Cyan
    Write-Host "╚═════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Check-Prerequisites
    
    Write-Info "Starting deployment process..."
    
    # Create secrets and get credentials
    $dbPassword = Create-Secrets
    
    # Build and push Docker images
    Build-DockerImages
    
    # Deploy infrastructure
    Deploy-CloudFormation -DbPassword $dbPassword -JwtSecret "your-jwt-secret"
    
    # Display outputs
    Write-Host ""
    Write-Success "CloudFormation outputs:"
    Get-StackOutputs
    
    # Final summary
    Deployment-Summary
    
    Write-Success "🎉 Deployment completed successfully!"
}

# Run main function
Main
