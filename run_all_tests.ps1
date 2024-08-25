# Define a function to check if a command executed successfully
function Check-Command {
    param (
        [string]$CommandName,
        [int]$ExitCode
    )
    if ($ExitCode -ne 0) {
        Write-Error "$CommandName failed with exit code $ExitCode"
        exit $ExitCode
    }
}

# Step 1: Run pytest to test the build_function Lambda
Write-Host "Running pytest for build_function Lambda tests..."
pytest tests/test_build_function.py -v
Check-Command "pytest for build_function Lambda" $LASTEXITCODE

# Step 2: Run pytest to test the deploy_function Lambda
Write-Host "Running pytest for deploy_function Lambda tests..."
pytest tests/test_deploy_function.py -v
Check-Command "pytest for deploy_function Lambda" $LASTEXITCODE

# Step 3: Run pytest to test the notifications Lambda
Write-Host "Running pytest for notifications Lambda tests..."
pytest tests/test_notifications.py -v
Check-Command "pytest for notifications Lambda" $LASTEXITCODE

# Step 4: Run pytest to test the pipeline_manager Lambda
Write-Host "Running pytest for pipeline_manager Lambda tests..."
pytest tests/test_pipeline_manager.py -v
Check-Command "pytest for pipeline_manager Lambda" $LASTEXITCODE

# Step 5: Run pytest to test the trigger_pipeline Lambda
# Write-Host "Running pytest for trigger_pipeline Lambda tests..."
# pytest tests/test_trigger_pipeline.py -v
# Check-Command "pytest for trigger_pipeline Lambda" $LASTEXITCODE

# Step 6: Invoke build_function Lambda locally
Write-Host "Invoking build_function Lambda locally..."
sam local invoke "BuildFunction" -e events/build_function_event.json
Check-Command "sam local invoke BuildFunction" $LASTEXITCODE

# Step 7: Invoke deploy_function Lambda locally
Write-Host "Invoking deploy_function Lambda locally..."
sam local invoke "DeployFunction" -e events/deploy_function_event.json
Check-Command "sam local invoke DeployFunction" $LASTEXITCODE

# Step 8: Invoke notifications Lambda locally
Write-Host "Invoking notifications Lambda locally..."
sam local invoke "NotificationFunction" -e events/notifications_event.json
Check-Command "sam local invoke NotificationsFunction" $LASTEXITCODE

# Step 9: Invoke pipeline_manager Lambda locally
# List of event files
$eventFiles = @("pipeline_create_event.json", "pipeline_delete_event.json", "pipeline_update_event.json", "pipeline_read_event.json")

# Loop through each event file and invoke the Lambda function
foreach ($eventFile in $eventFiles) {
    Write-Host "Invoking PipelineManagerFunction Lambda locally with event file: $eventFile..."
    sam local invoke "PipelineManagerFunction" -e "events/$eventFile"
    
    # Check the command result and exit if it failed
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Command failed for event file: $eventFile" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}


# Step 10: Invoke trigger_pipeline Lambda locally
# $eventFiles = @("trigger_create_event.json", "trigger_delete_event.json", "trigger_update_event.json", "trigger_read_event.json")

# Loop through each event file and invoke the Lambda function
# foreach ($eventFile in $eventFiles) {
#     Write-Host "Invoking PipelineManagerFunction Lambda locally with event file: $eventFile..."
#     sam local invoke "PipelineManagerFunction" -e "events/$eventFile"
    
#     # Check the command result and exit if it failed
#     if ($LASTEXITCODE -ne 0) {
#         Write-Host "Command failed for event file: $eventFile" -ForegroundColor Red
#         exit $LASTEXITCODE
#     }
# }

Write-Host "All tests and local invocations completed successfully!"
