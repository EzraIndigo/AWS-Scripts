IAM User Auditor for Organizations deployment. Generates JSON file with all IAM Users from all accounts with account ID

1.Create Lambda First & Role (Lambda Role needs minimum permissions to Org & S3 API)
2.Update CF Template with the Lambda Role in the 'AssumeRolePolicyDocument'
	2a. Update deployed Policy, it currently has 'iam:*' but it should be tuned to only iam:list-users or something similar
	
3.Create S3 bucket and update Lambda code with said bucket for JSON Upload
4. Deploy CF via Stacksets into desired accounts:

	CF Script to be used via StackSet from Master Account and deployed to desired accounts within ORG.
	CF Deploys role into each member account which has a trust relationship with the Lambda Role
	This allows Lambda function to assume deployed role in each account and Gather IAM User details


Lambda Runtime Details:
128MB of RAM should be enough, but runtime will vary depending on how many accounts you have. Tested with 17 accounts and takes around 18 seconds. I suggest deploying and tweaking RAM & Runtime based on your needs
In my testing it used around 75MB of RAM 



This may be adapted to also build a database from Data, etc
