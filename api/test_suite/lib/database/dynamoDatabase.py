import boto3
from boto3.dynamodb.conditions import Key, Attr

class Database:
    def __init__(self, databaseName='dynamodb', region_name='ap=south-1', endpoint_url=r"http://localhost:8080"):
        self.databaseName=databaseName
        self.region_name=region_name
        self.endpoint_url=endpoint_url

        self.connect()

    #function used to connect to the dynamodb
    def connect(self):
        self.dynamodb = boto3.resource(self.databaseName, region_name=self.region_name, endpoint_url=self.endpoint_url)

    def createTable(self,TableName,Attributes,KeySchema,ReadCapacityUnits,WriteCapacityUnits,Enable_SSESpecification,Enable_StreamSpecification):
        return self.dynamodb.create_table(
            AttributeDefinitions=Attributes,
            KeySchema=KeySchema,
            ProvisionedThroughput={
                'ReadCapacityUnits': ReadCapacityUnits,
                'WriteCapacityUnits': WriteCapacityUnits
            },
            SSESpecification={
                'Enabled': Enable_SSESpecification
            },
            StreamSpecification={
                "StreamEnabled": Enable_StreamSpecification
            },
            TableName=TableName
        )


#function to insert the item in the table
    def insert(self,TableName,item,):

        self.dynamoTable = self.dynamodb.Table(TableName)
        return self.dynamoTable.put_item(Item=item)

# function to read the item in the table
    def read_item(self,TableName,key):
        self.dynamoTable = self.dynamodb.Table(TableName)
        response = self.dynamoTable.get_item(Key=key)
        return(response['Item'])

#function to read all the items in the table
    def read_Table(self,TableName):
        self.dynamoTable = self.dynamodb.Table(TableName)
        response = self.dynamoTable.scan()
        return(response['Items'])

# function to update an item in the table
    def update_item(self,TableName,key,attribute_to_be_updated,value):
        self.dynamoTable = self.dynamodb.Table(TableName)
        return self.dynamoTable.update_item(
            Key=key,
            UpdateExpression='SET '+attribute_to_be_updated+'=:value',
            ExpressionAttributeValues={
                ':value': value
            }
        )

    # function to delete an item from the table
    def delete_item(self,TableName,key):
        self.dynamoTable = self.dynamodb.Table(TableName)
        return self.dynamoTable.delete_item(Key=key)


    # function to delete the entire table
    def delete_table(self,TableName):
        self.dynamoTable = self.dynamodb.Table(TableName)
        return self.dynamoTable.delete()

    #function for query in dynamodb
    def query(self,TableName,key,attribute_name):
        self.dynamoTable = self.dynamodb.Table(TableName)
        response = self.dynamoTable.query(
            KeyConditionExpression=Key(attribute_name).eq(key[attribute_name])
        )
        items = response['Items']
        return(items)

    def get_table_metadata(self,TableName):
        """
        Get some metadata about chosen table.
        """
        self.dynamoTable = self.dynamodb.Table(TableName)

        response={
            'num_items': self.dynamoTable.item_count,
            'primary_key_name': self.dynamoTable.key_schema[0],
            'status': self.dynamoTable.table_status,
            'bytes_size': self.dynamoTable.table_size_bytes,
            'global_secondary_indices': self.dynamoTable.global_secondary_indexes
        }

        return(response)

    def create_job_table(self):
        table_name ='jobs'
        attributes=[
            {
                'AttributeName': 'job_id',
                'AttributeType': 'N'
            },
        ]
        key_schema=[
            {
                'AttributeName': 'job_id',
                'KeyType': 'HASH'
            },
        ]
        self.createTable(table_name, attributes, key_schema, 5, 5,True, False)
        

    def create_task_table(self):
        table_name ='tasks'
        attributes=[
            {
                'AttributeName': 'task_id',
                'AttributeType': 'N'
            },
        ]
        key_schema=[
            {
                'AttributeName': 'task_id',
                'KeyType': 'HASH'
            },
        ]
        self.createTable(table_name, attributes, key_schema, 5, 5,True, False)
