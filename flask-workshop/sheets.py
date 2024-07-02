import pygsheets
import pandas as pd
import datetime
from numpy import genfromtxt

def get_index_of_last(list):
    list.reverse()
    for item in range(len(list)):
        if list[item] != '':
            index_of_last = len(list) - item
            break
        else:
            index_of_last = 0
        
    # print(index_of_last)
    return index_of_last

def write_to_file(upload_csv):
    gc = pygsheets.authorize(service_file='./utils/drivedecoder-6d045ce8f885.json')
    path = "./utils/" + upload_csv
    csvFile = pd.read_csv(path)
    csvFile.fillna(.01, inplace=True)
    csvFile = csvFile[["Product Name", "Set Name", "Condition", "Add to Quantity"]] #, "Total Quantity" , "Number", "Rarity"
    date = datetime.datetime.today()
    sh = gc.open('decoder')
    wks1 = sh[0]
    numAr = csvFile.to_numpy()
    length =  wks1.get_col(1)
    index_of_last = get_index_of_last(length)
    if index_of_last > 50:
        last_fifty = wks1.get_values((index_of_last-50,1),(index_of_last,6),returnas='matrix',include_tailing_empty=False)

    all_lines = []
    cards = 1
    if index_of_last == 0:
        lastSerialNumber = 10000
        batch = 1
    else:
        lastSerialNumber = int(wks1.get_value((index_of_last, 7)))
        index = 0
        old_count = 1
        for line in last_fifty:
            if index != 0:
                if batch_check == line[4]:
                    old_count+=1
                else:
                    old_count = 1

            batch_check = line[4]
            index+=1
        cards = old_count + 1
        if  old_count == 50:
            batch = int(wks1.get_value((index_of_last, 5))) + 1
        else:
            batch = int(wks1.get_value((index_of_last, 5)))
    for lines in numAr:
        lines = list(lines)
        lastSerialNumber+=1
        

        lines.append(batch)
        lines.append(date.strftime("%x"))
        lines.append(lastSerialNumber)

        count = int(lines[3])
        if count > 1:
            while count > 1:
                all_lines.append(lines[:])
                if cards % 50 == 0:
                    batch+=1
                    lines[4] = batch
                cards+=1
                count-=1
                lastSerialNumber+=1
                lines[6]+=1
                lines[3] = str(count)

        all_lines.append(lines) 
        index_of_last+=1
        if cards % 50 == 0:
            batch+=1
        cards+=1

    wks1.append_table(all_lines,dimension='ROWS',overwrite=False)


def read_and_pull():
    gc = pygsheets.authorize(service_file='./utils/drivedecoder-6d045ce8f885.json')
    sh = gc.open('decoder')
    wksZap = sh[2]
    wksPull = sh[1]
    wks = sh[0]
    length = wksZap.get_col(1)
    last = get_index_of_last(length)
    order_list = wksZap.get_values((2,1),(last,6),returnas='matrix',include_tailing_empty=False)
    pull_list = []
    for order in order_list:
        # print(order)
        # print(len(order))
        if len(order) > 5:
            
            if  order[5] == 'DoNotShip TCGplayerDirect' or order[5] == '':
                # order_list.pop(order_list.index(order))
                continue
        if len(order) <= 5:
            # print('too small')
            continue
        
        if order[2] == '' or order[2] == 'New':
            # print('not right')
            continue
        name_set = order[0].split('[')
        name = name_set[0].strip()
        sett = name_set[1].replace(']', '')
        orderstr = order.pop(0)
        orderstr = order.pop(0)
        order.insert(0, sett)
        order.insert(0, name)
        pull_list.append(order)
        # print(order)

    # get the cards from the master list

    length = wks.get_col(1)
    last_master = get_index_of_last(length)
    master_list = wks.get_values((1,1),(last_master,7),returnas='matrix',include_tailing_empty=False)
    # length = wks.get_col(1)
    # last_pull_master = get_index_of_last(length)
    # master_pull_list = wksPull.get_values((1,1),(last_pull_master,6),returnas='matrix',include_tailing_empty=False)

    master_pull = []
    not_pull = []
    to_remove = []
    
    for card in pull_list:
        found = False
        qty = int(card[3])
        for master_card in master_list:
            if card[0] == master_card[0]:
                if card[1] == master_card[1]:
                    if card[2] == master_card[2]:
                        master_card.insert(6,card[4])
                        master_card.insert(7,card[5])
                        master_pull.append(master_card)
                        to_remove.append(master_list.index(master_card))
                        found = True
                        if qty > 1:
                            qty-=1
                            found = False
                        else:
                            break
        if not found:
            not_pull.append(card)
    # print(master_pull)
    # print("not pull:")
    # print(not_pull)
    to_remove.sort(reverse=True)
    print(to_remove)
    # remove from master list
    for line in to_remove:
        wks.delete_rows(line+1,number=1)
    # put on a new sheet
    # length1 =  wksPull.get_col(1)
    # last1 = get_index_of_last(length1)
    # wksPull.update_values(crange=(last1+2,1),values=master_pull,majordim='ROWS')
    wksZap.clear(start='A2')
    
    return master_pull


def  tcg_order_puller(csv):
    gc = pygsheets.authorize(service_file='./utils/drivedecoder-6d045ce8f885.json')
    sh = gc.open('decoder')
    wks = sh[0]
    length = wks.get_col(1)
    last = get_index_of_last(length)
    master_list = wks.get_values((2,1),(last,7),returnas='matrix',include_tailing_empty=False)
    # csvFile = genfromtxt('R20240617-0f261c59.csv', delimiter=',', skip_header=1)
    path = './utils/' + csv
    csvFile = pd.read_csv(path, skiprows=1)
    csvFile = csvFile[["Card Name", "Set Name", "Condition", "Quantity"]]
    # print(csvFile)
    # csvFile.fillna(.01, inplace=True)
    pull_list = csvFile.to_numpy()
    # print(numAr)

    master_pull = []
    not_pull = []
    to_remove = []
    
    for card in pull_list:
        found = False
        qty = int(card[3])
        for master_card in master_list:
            if card[0] == master_card[0]:
                if card[1] == master_card[1]:
                    if card[2] == master_card[2]:
                        print(master_card)
                        master_pull.append(master_card)
                        to_remove.append(master_list.index(master_card))
                        found = True
                        if qty > 1:
                            qty-=1
                            found = False
                        else:
                            break
        if not found:
            not_pull.append(card)

    to_remove.sort(reverse=True)
    for line in to_remove:
        wks.delete_rows(line+1,number=1)

    wksPull = sh[1]
    length1 =  wksPull.get_col(1)
    last1 = get_index_of_last(length1)
    wksPull.update_values(crange=(last1+2,1),values=master_pull,majordim='ROWS')
    

def separate_by_order(pull_list):
    gc = pygsheets.authorize(service_file='./utils/drivedecoder-6d045ce8f885.json')
    sh = gc.open('decoder')
    wks = sh[3]
    # length = wks.get_col(1)
    # last = get_index_of_last(length)
    call_break = ['---------------','---------------','-----------','------------','------------','------------','------------','------------','-------------','-------------']
    index = 0
    l1 = 0
    count=0
    last_count = 0
    order_lists = []
    for card in pull_list:
        if len(card) > 6:
            order = card[6]
        else:
            break
        if index == 0:
            order_lists.append(card)
            # print(order_lists)
        elif order_lists[0][6] == order:
           order_lists.append(card)
        #    print(order_lists)
        #    print(index)
        #    print(len(pull_list))
           if index == len(pull_list) - 1:
                length = wks.get_col(1)
                last = get_index_of_last(length)
                wks.update_values(crange=(last+2,1),values=order_lists,majordim='ROWS')
        elif order_lists[0][6] != order:
            length = wks.get_col(1)
            last = get_index_of_last(length)
            if count < 1:
                order_lists.insert(0,call_break)
            wks.update_values(crange=(last+2,1),values=order_lists,majordim='ROWS')

            order_lists = []
            # l1+=1
            order_lists.append(card)
            count+=1
            
        index+=1




# write_to_file()













# print(csvFile.values[0])
# csvFile["Number"] = csvFile["Number"].replace({1: str(1)})
# for r in csvFile:
#     row = {'Product Name': r['Product Name'],
#            'Set Name': r['Set Name'],
#            'Rarity': r['Rarity'],
#            'Number': r[str('Number')],
#            'Condition': r['Condition']
#            }

# print(csvFile)
# csvRow = csvFile.loc[1]
# print(numAr[1])
# add_worksheet("")


# df['name'] = ['John', 'Steve', 'Sarah']
# ar = ['John', 'Steve', 'Sarah']
# print(ar)
# cell = wks1.find("Paper Tiger")
# print(cell)
# row1 = wks1.get_row(2, returnas='matrix')
# print(row1)

# for lines in numAr:
#     lines[3] = str(lines[3])

# addr = 'F'+ str(wks1.rows - 2)

#  wks1.get_value(addr)
# print(length)
# index = length.index('')