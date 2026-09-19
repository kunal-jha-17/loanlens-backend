AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: LoanLens backend foundation on AWS Lambda + API Gateway

Globals:
  Function:
    Timeout: 30
    Runtime: python3.12
    MemorySize: 512
    Environment:
      Variables:
        APP_ENV: development
        AWS_REGION: ap-south-1
        S3_INPUT_BUCKET: loanlens-uploads
        DYNAMODB_RULES_TABLE: loanlens-rules
        DYNAMODB_DLA_TABLE: loanlens-dla-snapshot
        DYNAMODB_LOGS_TABLE: loanlens-interaction-log

Resources:
  LoanLensApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Cors:
        AllowMethods: '"GET,POST,OPTIONS"'
        AllowHeaders: '"Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"'
        AllowOrigin: '"*"'

  LoanLensMockFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: functions.loanlens_mock_handler.lambda_handler
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /loanlens/mock
            Method: get
            RestApiId: !Ref LoanLensApi

  LoanLensProcessFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: functions.loanlens_process_handler.lambda_handler
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /loanlens/process
            Method: post
            RestApiId: !Ref LoanLensApi

  LoanLensRulesFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: functions.loanlens_mock_handler.lambda_handler

  LoanLensFinanceFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: functions.loanlens_mock_handler.lambda_handler

  LoanLensDlaLookupFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: functions.loanlens_mock_handler.lambda_handler

  LoanLensOrchestratorFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: functions.loanlens_mock_handler.lambda_handler

Outputs:
  LoanLensApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub "https://${LoanLensApi}.execute-api.${AWS::Region}.amazonaws.com/prod/"
