import os
import logging
import csv

class Importer():
    def __init__(self, mydb, csv_basepath):
        self.mydb = mydb
        self.csv_basepath = csv_basepath
    
    def process_person_row (self, row):
        try:
            cur = self.mydb.cursor(dictionary=True)
            cur.execute('''
                INSERT INTO persons (id, first_name, last_name, email, gender, ip_address) 
                VALUES (%s,%s,%s,%s,%s,%s); 
                ''', 
                (
                    row['id'],
                    row['first_name'],
                    row['last_name'],
                    row['email'],
                    row['gender'],
                    row['ip_address']
                ))
            self.mydb.commit()
            logging.debug("processed person row: " + row['id'] +", "+ row['first_name'] + ", "+ row['last_name'])
        except Exception as e:
            logging.error("process person row: " + str(e))
            self.mydb.rollback()
    
    def process_country_row (self, row):
        try:
            cur = self.mydb.cursor(dictionary=True)
            cur.execute('''
                INSERT INTO countries (id, person_id, country) 
                VALUES (%s,%s,%s); 
                ''', 
                (
                    row['id'],
                    row['person_id'],
                    row['country']
                ))
            self.mydb.commit()
            logging.debug("processed country row: " + row['id'] +", "+ row['country'] )
        except Exception as e:
            logging.error("process country row: " + str(e))
            self.mydb.rollback()
    
    def process(self):
        logging.info("Importer.process ")
        # load persons.csv file
        with open( os.path.join(self.csv_basepath, 'persons.csv') ) as fp:
            reader = csv.DictReader(fp, delimiter=',')
            for row in reader:
                self.process_person_row(row)
        # load countries.csv file 
        with open( os.path.join(self.csv_basepath, 'countries.csv')) as fc:
            reader = csv.DictReader(fc, delimiter=',')
            for row in reader:
                self.process_country_row(row)
