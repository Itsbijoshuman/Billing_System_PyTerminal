import random
import mysql.connector
from tabulate import tabulate
import random
import csv
from datetime import date
from datetime import datetime
import time 

try:
    mydb=mysql.connector.connect(host='localhost',user='root',password='')
    print('Connection Sucessful')
except:
    print('Database Connection error')

try:
    sub1='create database shop;'  
    cur=mydb.cursor()
    cur.execute(sub1)
    print('database created')
except:
    print('database alredy created ') 

cur.execute('use  shop;')

try:
    cur.execute('Create table currentprice(Sn1 int, item_name varchar(100),Mass float,Unit varchar(10),Price int(10),Unique_Code int,PRIMARY KEY(Unique_Code)); ')
    print('Table created')
except:
    print('Table already exists')

cur.execute('create table if not exists dt(TableName varchar(20),Date_And_Time varchar(30))')

cur.execute('Delete from currentprice')

with open('SmpleFile.csv', 'r') as csv_file:
    data_reader = csv.reader(csv_file)
    for row in data_reader:
        cur.execute('Insert into currentprice values(%s,"%s",%s,"%s",%s,%s)'%(row[0],row[1],row[2],row[3],row[4],row[5]))
        mydb.commit()
print('Insertion Complete')


def live_bill():
    #bill live
    cur.execute('drop table if exists temp')
    cur.execute('Create table temp(Sn2 int,Product varchar(100), Quantity int, weight float); ')
    c='Y'
    re='N'
    z=0
    while c=='Y' :
        #Search
        while re.upper()=='N':
            name_like=input('Enter the Product to be searched: ')
            cur.execute(f'select * from currentprice where item_name like "%{name_like}%"')
            name_like_data=cur.fetchall()
            print(tabulate(name_like_data,headers=['S.No','Product','Weight','Unit','Price','Unique_Code']))
            print()
            re=input('Did U find waht You Searched For?- Y Or N :  ')
        
        list_data1=[]
        unique=int(input('Enter the Unique_Code : '))
        cur.execute(f'select item_name from currentprice where Unique_Code={unique}') 
        data=cur.fetchall()
        for i in data:
            for j in i:
                list_data1.append(j)
        input_product=list_data1[0]
        input_quantity=int(input('Quantity : '))
        we1=[]
        cur.execute(f'select Mass from currentprice where Unique_Code={unique}')
        data1=cur.fetchall()
        for i in data1:
            for j in i:
                we1.append(j)   

        input_weight=we1[0]
        z=z+1
        cur.execute("insert into temp values('%s','%s','%s','%s')" %(z,input_product,input_quantity,input_weight))
        mydb.commit()
        user=input('To Continue Press Y else press anything to leave : ')
        c=user.title()
        if c=='Y':
            re='N'


#Bill number determination
    choices = list(range(9999999))
    random.shuffle(choices)
    final_bill=str(choices.pop())
#two tables connecting
    cur.execute('create table if not exists t{tab} (select Sn2,Product,Quantity,weight,Unit,Price,Unique_code,Quantity*Price as Sum from temp,currentprice where temp.Product=currentprice.item_name  and temp.weight=currentprice.Mass   order by Sn2);'.format(tab=final_bill))
    print(f'No old Data found so new table temp{final_bill} is created')
    cur.execute('drop table temp;')
    cur.execute("select * from t"+f"{final_bill}")
    out_data=cur.fetchall()
#Csv file with new billno and data is created
    with open("t"+f"{final_bill}"".csv", 'w',newline='') as out_file:
        data_writer = csv.writer(out_file)
        for custom in out_data:
            data_writer.writerow(custom)
    a='t'+f'{final_bill}'
    b=datetime.now()
    cur.execute('insert into dt values("%s","%s")'%(a,b))
    mydb.commit()
    list_data=[]
    print()
    print(f"Bill NO.: {final_bill}                 DATE & Time: {b} " ) 
    print()         
    #Display of file which is created Just now
    with open("t"+f"{final_bill}"".csv", 'r') as csv_bill:
        data_reader = csv.reader(csv_bill)
        for row1 in data_reader:
            list_data.append(row1)
    print(tabulate(list_data,headers=['S.No','Product','Quantity','Weight','Unit','Price','Unique_Code','Sum']))
    cur.execute(f'select sum(Sum) from t{final_bill}')
    sum_data=cur.fetchall()
    for row in sum_data:
        for j in row:
            print()
            print('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*')
            print(f'                                                     TOTAL PRICE   :         {j} ')

def update_stock():
    user_input1=int(input('''
    Press 1 or 2 To:

    1.Update A Existing Product
    2.Add A New Product 

    What Do You Want?: '''))

    updation='Y'
    if user_input1==1: 
        while updation.upper()=='Y':
            product_code=int(input('Enter the  unique code of the product whose price to be Updated : '))
            new_price=int(input('Enter the New Price: '))
            cur.execute('UPDATE currentprice set Price=%s where Unique_Code=%s '%(new_price,product_code))
            updation=input('Enter Y to update more product or anything to exit : ')
        mydb.commit()

        #csv stock file updation
        cur.execute('select * from currentprice')
        updated_table=cur.fetchall()    
        with open("SmpleFile.csv", 'w',newline='') as updated_file:
            data_writer = csv.writer(updated_file)

            for custom1 in updated_table:
                data_writer.writerow(custom1)


    adding_data='Y'
    if user_input1==2:
        #uniquecode & Sn  automation
        with open("SmpleFile.csv", 'r') as added_file:
            qq=added_file.readlines(-1)
            temp_list=[]
            v=qq
            temp_sn_no=v[-1]
            temp_list.append(temp_sn_no)
            sub_final_sno=temp_list[0]
            li=list(sub_final_sno.split(','))
            index=int(li[0])
            final_sn_no=index
            last_index1=int(li[-1])
            input_unique_code=last_index1

        while adding_data.upper()=='Y':
            final_sn_no+=1
            input_unique_code+=1
            raw_product=input('Product :')
            input_product=raw_product.title()
            input_weight=float(input('Weight : '))
            input_unit=input('Enter the Unit of the Above Added Product : ')
            input_price=int(input('Enter the price of the Added Product : '))
            cur.execute("insert into currentprice values('%s','%s','%s','%s','%s','%s')" %(final_sn_no,input_product,input_weight,input_unit,input_price,input_unique_code))
            mydb.commit()

            #csvfile update
            cur.execute('select * from currentprice')
            new_edited_table=cur.fetchall()
            with open("SmpleFile.csv", 'w+',newline='') as edited_updated_table: 
                edited_writer=csv.writer(edited_updated_table) 
                for custom2 in new_edited_table:
                    edited_writer.writerow(custom2)
            adding_data=input('To Add more Data Press y or press anything to exit: ')

def print_bill():
    print_input=int(input('Enter the Bill Number To Be Viewed: '))
    final_input1='t'+f'{print_input}'
    cur.execute(f'select Date_And_Time from dt where TableName ="{final_input1}" ')
    datentime1=cur.fetchall()
    print(datentime1)
    data=''
    for column in datentime1:
        for ace in column:
            data=ace
    print()
    print(f'                                   DATE AND TIME:       {data}')   
    print() 
    cur.execute(f'Select * from {final_input1}')
    print_data=cur.fetchall()
    print(tabulate(print_data,headers=['S.No','Product','Quantity','Weight','Unit','Price','Unique_Code','Sum']))
    cur.execute(f'select sum(Sum) from {final_input1}')
    sum_data=cur.fetchall()
    for row in sum_data:
        for j in row:
            print()
            print('*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*')
            print(f'                                                       TOTAL PRICE   :       {j} ')            
    time.sleep(2)

def stock():
    cur.execute('select * from currentprice')
    stock_data=cur.fetchall()
    time.sleep(1)
    print(tabulate(stock_data,headers=['S.No','Product','Weight','Unit','Price','Unique_Code']))
    print()
    time.sleep(2)
exit=False

while exit==False:
    print('*_*_*_*_*_*_* WELCOME TO BILLEASE _*_*_*_*_*_*_*_*')
    print('_____________________________________________________________________________________')
    ultimate_user_choice=int(input('''
    Press 1,2 or 3 To:

    1.Update Stock File
    2.Create Bill
    3.View Previous Bill
    4.View The Stock File
    5.Exit

    What Do You Want?: '''))  
    print('______________________________________________________________________________________')
    print()
    if ultimate_user_choice==1:
        update_stock()
    if ultimate_user_choice==2:
        live_bill()
    if ultimate_user_choice==3:
        print_bill()
    if ultimate_user_choice==4:
        stock()
    if ultimate_user_choice==5:
        exit=True
    

print('END')