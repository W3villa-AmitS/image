from jobs.PynamoOps import Database
from jobs.models import Job_Model,Task_Model
from django.test import SimpleTestCase

db = Database()

class TestPynamo(SimpleTestCase):
    ModelObj = Job_Model
    data = {
                        "job_name": "amit",
                        "job_type": "P",
                        "job_attributes":"test",
                        "job_description": "hello",
                        "job_instructions": "hi",
                        "job_max_occurrence":4,
                        "job_criteria_age_min":19,
                        "job_criteria_age_max":58,
                        "job_criteria_location":"India",
                        "job_criteria_grade": "A",
                        "job_initial_qats": 3,
                        "job_qat_frequency":1,
                        "job_criteria_gender":["M"],
                        "job_boxing_type" : "Rectangle",
                    }
#In this test case, first we insert the item in the table
#Then we read the item with primary key from the model.
    def test_pynamo_insert(self):
        job_id = '2015257'
        db.insert(self.ModelObj,job_id,self.data)
        self.assertEqual(db.read_item(self.ModelObj,job_id)['job_id'],job_id)
        db.delete_item(self.ModelObj,'2015257')
#In this test case we read the table and then check the length of the result
    def test_pynamo_read_table(self):
        items= db.read_Table(self.ModelObj)
        status = True
        if len(items)>0:
            test_case_pass = True
        self.assertEqual(status, test_case_pass)
#in this we insert an item and then we read the item
    def test_pynamo_read_items(self):
        hash_key = 'job_id'
        pk_value = '20152566'
        db.insert(self.ModelObj, pk_value, self.data)
        item = db.read_item(self.ModelObj, pk_value)
        self.assertEqual(item[hash_key], pk_value)
        db.delete_item(self.ModelObj, pk_value)
#in this test case we insert the item and update its value.and read the new value.
    def test_update_items(self):
        pk_value = '20115260'
        attribute_to_be_updated = self.ModelObj.job_name
        attribute_to_be_updated_string = 'job_name'
        value = 'testing_job'
        db.insert(self.ModelObj, pk_value, self.data)
        db.update_item(self.ModelObj, pk_value, attribute_to_be_updated, value)
        self.assertEqual(db.read_item(self.ModelObj, pk_value)[attribute_to_be_updated_string], value)
        db.delete_item(self.ModelObj, pk_value)
    def test_delete_item(self):
        test_case_pass = True
        deleted = False
        db.insert(self.ModelObj, '2015257', self.data)
        ex = db.delete_item(self.ModelObj, '20115257')
        if not ex == "Item deleted successfully":
                deleted = False
        else:
                deleted = True
        self.assertEqual(test_case_pass, deleted)
    '''def read_Table_by_attribute(self, attribute, value):
        result = []
        for item in self.ModelObj.scan(attribute == value):
                result.append(item.attribute_values)
        print(len(result))'''
#ab = TestPynamo()
#ab.test_pynamo_insert()
#ab.test_pynamo_read_items()
#ab.test_update_items()
#ab.test_pynamo_read_table()
#ab.test_delete_item()
#ab.read_Table_by_attribute(Task_Model.job_id,'koaEZqBU')
#print(Job_Model.count())
