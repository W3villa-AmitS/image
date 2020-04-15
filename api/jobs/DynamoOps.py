import boto3
from boto3.dynamodb.conditions import Key, Attr
from django.conf import settings

class Databases:
    def __init__(self, databaseName='dynamodb', region_name=settings.DYNAMO['REGION']):
        self.databaseName=databaseName
        self.region_name=region_name
        self.endpoint_url=settings.DYNAMO['URL']
        self.session = boto3.Session(
            aws_access_key_id='fakeaCCesskey62532',
            aws_secret_access_key='faKEsecretKey343454e67754335ggvdr4fFG',
        )

#function used to connect to the dynamodb
    def connect(self):
        self.dynamodb = self.session.resource(self.databaseName, region_name=self.region_name, endpoint_url=self.endpoint_url)

    def createTable(self,TableName,Attributes,KeySchema,ReadCapacityUnits,WriteCapacityUnits,Enable_SSESpecification,Enable_StreamSpecification):

        response = self.dynamodb.create_table(
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
        return "Table created successfully"


#function to insert the item in the table
    def insert(self,TableName,item,):

        self.dynamoTable = self.dynamodb.Table(TableName)
        self.dynamoTable.put_item(Item=item)
        return "Item inserted successfully"


# function to read the item in the table
    def read_item(self,TableName,key):
        self.dynamoTable = self.dynamodb.Table(TableName)
        response = self.dynamoTable.get_item(Key=key)
        return response['Item']

#function to read all the items in the table
    def read_Table(self,TableName):
        self.dynamoTable = self.dynamodb.Table(TableName)
        response = self.dynamoTable.scan()
        data = response['Items']
        while response.get('LastEvaluatedKey'):
            response = self.dynamoTable.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
        return data

# function to update an item in the table
    def update_item(self,TableName,key,attribute_to_be_updated,value):
        self.dynamoTable = self.dynamodb.Table(TableName)
        response = self.dynamoTable.update_item(
            Key=key,
            UpdateExpression='SET '+attribute_to_be_updated+'=:value',
            ExpressionAttributeValues={
                ':value': value
            }

        )
        return "Item updated successfully"


    # function to delete an item from the table
    def delete_item(self,TableName,key):
        self.dynamoTable = self.dynamodb.Table(TableName)
        self.dynamoTable.delete_item(Key=key)
        return "Item deleted successfully"


# function to delete the entire table
    def delete_table(self,TableName):
        self.dynamoTable = self.dynamodb.Table(TableName)
        self.dynamoTable.delete()
        return "Table deleted successfully"

#function for query in dynamodb
    def query(self,TableName,key,attribute_name):
        self.dynamoTable = self.dynamodb.Table(TableName)
        response = self.dynamoTable.query(
            KeyConditionExpression=Key(attribute_name).eq(key[attribute_name])
        )
        items = response['Items']
        return items

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

        return response
#Get ID function is not boto3 sdk or pynamodb function. It is a custom function
# created just to get the IDs.
    def getID(self, TableName, key):
       self.dynamoTable = self.dynamodb.Table(TableName)
       response = self.dynamoTable.get_item(Key=key)
       return response['Item']

