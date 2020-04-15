import boto3
from boto3.dynamodb.conditions import Key, Attr
from django.conf import settings
from pynamodb.connection import Connection,TableConnection
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.transform import TransformationInjector


class Database:
    '''def __init__(self,db_name = 'dynamodb'):
       self.db_name = db_name


#function used to connect to the dynamodb
    def connect(self):
        conn = Connection(host=settings.DYNAMO['URL'])
        return conn
    '''
    def __init__(self,databaseName='dynamodb', region_name=settings.DYNAMO['REGION']):
        self.databaseName = databaseName
        self.region_name = region_name
        self.endpoint_url = settings.DYNAMO['URL']
        #self.session = boto3.resource(databaseName,
        #    aws_access_key_id=settings.DYNAMO_AWS_ACCESS['AWS_ACCESS_KEY_ID'],
        #    aws_secret_access_key = settings.DYNAMO_AWS_ACCESS['AWS_SECRET_ACCESS_KEY'],
        #                              region_name=self.region_name
        #)
        self.session = boto3.session.Session(
            region_name=region_name,
            aws_access_key_id=settings.DYNAMO_AWS_ACCESS['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=settings.DYNAMO_AWS_ACCESS['AWS_SECRET_ACCESS_KEY'])


        # function used to connect to the dynamodb

    def connect(self,ModelObj):
        conn = TableConnection(ModelObj.Meta.table_name,host=settings.DYNAMO['URL'],aws_access_key_id=settings.DYNAMO_AWS_ACCESS['AWS_ACCESS_KEY_ID'],
                 aws_secret_access_key=settings.DYNAMO_AWS_ACCESS['AWS_SECRET_ACCESS_KEY'])
        return conn

#To create table in Dyanodb using Pynamodb
    def createTable(self,ModelObj):
       if not ModelObj.exists():
            ModelObj.create_table(read_capacity_units=4, write_capacity_units=4, wait=True)
            print("Table created")
       else:
            print("Table already exists")
       return "Table created successfully"



#function to insert the item in the table
    def insert(self, ModelObject, pk, item):
        item = ModelObject(pk,**item)
        item.save()
        return "Item inserted successfully"


# function to read the item from the table
    def read_item(self, ModelObject, pk):
        return ModelObject.get(pk).attribute_values



#function to read all the items in the table

    def read_Table(self,ModelObj):

        #conn=self.connect(ModelObj)
        #response = conn.scan()
        data=[]
        #data = response['Items']
        #while response.get('LastEvaluatedKey'):
         #   response = self.dynamoTable.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
         #   data.extend(response['Items'])

        client = boto3.client('dynamodb',region_name = self.region_name,aws_access_key_id=settings.DYNAMO_AWS_ACCESS['AWS_ACCESS_KEY_ID'],
                             aws_secret_access_key=settings.DYNAMO_AWS_ACCESS['AWS_SECRET_ACCESS_KEY'],
                             endpoint_url=settings.DYNAMO['URL'])
        paginator = client.get_paginator('scan')
        service_model = client._service_model.operation_model('Scan')
        operation_parameters = {
            'TableName': ModelObj.Meta.table_name,
            }
        trans = TransformationInjector(deserializer=TypeDeserializer())
        for page in paginator.paginate(**operation_parameters):
            trans.inject_attribute_value_output(page, service_model)
            while page.get('LastEvaluatedKey'):
                page = self.dynamoTable.scan(ExclusiveStartKey=page['LastEvaluatedKey'])
                data.extend(page['Items'])
            else:
                data.extend(page['Items'])
        return data



# function to read items on the basis of attribute

    def read_Table_by_attribute(self, ModelObj, attribute, value):
        result = []
        for item in ModelObj.scan(attribute == value):
            result.append(item.attribute_values)
        return result

    # function to update an item in the table
    def update_item(self,ModelObj,pk,attribute_to_be_updated,value):
        db_item = ModelObj(pk)
        db_item.update(actions=[attribute_to_be_updated.set(value)])
        return "Item updated successfully"



# function to delete an item from the table
    def delete_item(self,ModelObj,pk):
        item = ModelObj(pk)
        item.delete()
        return "Item deleted successfully"


# function to delete the entire table
    def delete_dynamo_table(self,Modelobj):
        if not Modelobj.exists():
            return Modelobj.Meta.table_name+" "+"table does not exists"
        else:
            Modelobj.delete_table()
            return Modelobj.Meta.table_name+" "+"table deleted successfully"


#function to get table metdata
    def get_table_metadata_pynamo(self, ModelObj):
        return ModelObj.describe_table()


#Get ID function is not boto3 sdk or pynamodb function. It is a custom function
# created just to get the IDs.
class Dynamo_with_boto:
    def __init__(self, databaseName='dynamodb', region_name=settings.DYNAMO['REGION']):
        self.databaseName = databaseName
        self.region_name = region_name
        self.endpoint_url = settings.DYNAMO['URL']
        self.session = boto3.Session(
            aws_access_key_id=settings.DYNAMO_AWS_ACCESS['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=settings.DYNAMO_AWS_ACCESS['AWS_SECRET_ACCESS_KEY'],
        )

    # function used to connect to the dynamodb
    def connect(self):
        self.dynamodb = self.session.resource(self.databaseName, region_name=self.region_name,
                                              endpoint_url=self.endpoint_url)

    def getID(self, TableName, key):
       self.dynamoTable = self.dynamodb.Table(TableName)
       response = self.dynamoTable.get_item(Key=key)
       return response['Item']
