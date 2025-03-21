import * as cdk from "aws-cdk-lib";
import * as lambda from "aws-cdk-lib/aws-lambda";
import { Construct } from "constructs";
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class PptMakerDeployStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here
    const dockerFunction = new lambda.DockerImageFunction(
      this,
      "DockerFunction",
      {
        code: lambda.DockerImageCode.fromImageAsset("./ppt-maker-image"),
        memorySize: 1024,
        timeout: cdk.Duration.seconds(10),
      }
    );

    const functionUrl = dockerFunction.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedHeaders: ["*"],
        allowedOrigins: ["*"],
      },
    });

    new cdk.CfnOutput(this, "FunctionUrlValue", {
      value: functionUrl.url,
    });
    // example resource
    // const queue = new sqs.Queue(this, 'PptMakerDeployQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });
  }
}
