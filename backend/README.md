# ResumeTry Backend - AWS Lambda Functions

This backend is built using AWS SAM (Serverless Application Model) with Python Lambda functions.

## Prerequisites

1. **AWS CLI** - Install and configure with your AWS credentials
   ```bash
   aws configure
   ```

2. **AWS SAM CLI** - Install from [AWS SAM CLI documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
   ```bash
   # Windows (using Chocolatey)
   choco install aws-sam-cli
   
   # Or download from: https://github.com/aws/aws-sam-cli/releases
   ```

3. **Docker** - Required for local testing (SAM uses Docker to simulate Lambda environment)

## Project Structure

```
backend/
├── health/          # Health check Lambda function
│   ├── app.py
│   └── requirements.txt
├── resume/          # Resume processing Lambda function
│   ├── app.py
│   └── requirements.txt
└── README.md
```

## Local Development

### Build the application

```bash
# From the project root
sam build
```

### Run locally with SAM Local

```bash
# Start the API locally (simulates API Gateway + Lambda)
sam local start-api

# The API will be available at http://localhost:3000
```

### Test individual functions

```bash
# Test health check
sam local invoke HealthCheckFunction

# Test resume processing
sam local invoke ProcessResumeFunction -e events/resume-event.json
```

## Deployment

### First-time deployment

```bash
# Build the application
sam build

# Deploy to AWS (guided)
sam deploy --guided

# This will prompt you for:
# - Stack name: resumetry-backend
# - AWS Region: us-east-1 (or your preferred region)
# - Confirm changes before deploy: Yes
# - Allow SAM CLI IAM role creation: Yes
# - Disable rollback: No
# - Save arguments to samconfig.toml: Yes
```

### Subsequent deployments

```bash
# Build and deploy (uses samconfig.toml)
sam build && sam deploy
```

### View deployment outputs

After deployment, SAM will output the API Gateway URL. You can also find it in:
- AWS CloudFormation console (Stack outputs)
- AWS API Gateway console

## API Endpoints

Once deployed, you'll have the following endpoints:

- `GET /health` - Health check endpoint
- `POST /api/resume` - Process a new resume
- `GET /api/resume/{id}` - Get resume by ID

## Adding New Lambda Functions

1. Create a new directory under `backend/` (e.g., `backend/users/`)
2. Add `app.py` with your handler function
3. Add `requirements.txt` for dependencies
4. Update `template.yaml` to include the new function:

```yaml
NewFunction:
  Type: AWS::Serverless::Function
  Properties:
    Handler: app.handler
    CodeUri: backend/users/
    Events:
      NewEndpoint:
        Type: Api
        Properties:
          RestApiId: !Ref ResumeTryApi
          Path: /api/users
          Method: GET
```

5. Rebuild and redeploy:
```bash
sam build && sam deploy
```

## Environment Variables

Add environment variables in `template.yaml` under the `Globals.Function.Environment.Variables` section or per-function:

```yaml
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Environment:
      Variables:
        MY_VAR: "value"
```

## Testing

### Unit Testing

Create test files following Python conventions:
```bash
# Install test dependencies
pip install pytest pytest-mock

# Run tests
pytest backend/
```

### Integration Testing

Use `sam local` to test locally before deploying:
```bash
sam local invoke FunctionName -e events/test-event.json
```

## Monitoring and Logging

- **CloudWatch Logs**: Each Lambda function automatically logs to CloudWatch
- **X-Ray**: Enable tracing in `template.yaml` for distributed tracing
- **CloudWatch Metrics**: Monitor function invocations, errors, and duration

## Cost Optimization

- Lambda functions are charged per invocation and execution time
- API Gateway charges per API call
- Consider using provisioned concurrency only if needed
- Use appropriate memory sizes (more memory = faster execution but higher cost)

## Troubleshooting

### Build fails
- Ensure Docker is running (required for SAM builds)
- Check Python version matches (python3.11)

### Deployment fails
- Verify AWS credentials: `aws sts get-caller-identity`
- Check IAM permissions for CloudFormation, Lambda, API Gateway
- Review CloudFormation stack events in AWS Console

### Local testing issues
- Ensure Docker Desktop is running
- Check port 3000 is not in use
- Review SAM logs: `sam local start-api --debug`

