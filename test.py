import pdftotext
import json
import os
import re

PDF_TYPE = "VN103933"
CURR_CONFIG = {}

with open(PDF_TYPE + '/' + PDF_TYPE + '.json', 'r', encoding='utf8') as json_file:
    CONFIG = json.load(json_file)

KEYWORD = [
            'SHIPPING REQUEST', 'Shipper', 'Consignee', 'Notify', 'Reference No.', 'Booking No.', 'TO  ',
            'TEL  ','FAX  ','ATTN', 'FROM', 'E-MAIL', 'M.B/L Type', 'HS Code', 'M.Vessel/Voyage',
            'Port of Loading', 'Delivery', 'ETD', 'ETA', 'Port of Discharge', 'Final Destination', 'Mark & Number',
            'No of Package', 'Description of Goods', 'Weight', 'Measurement', 'FREIGHT PREPAID'
            ]

# KEYWORD = ['From','To','Booking No.','Date','Shipper Name & Address',
#             'Consignee Name & Address','Notify Party','Port of Loading',
#             'Port of Discharge','Place of Delivery','Vessel',
#             'Etd','Container/Seal No.','Packages','Description of Goods',
#             'CBM','Remarks  ','Payment','Total','G.W (KGS)','page']

fileName = list(filter(lambda pdf: pdf[-3:] == 'pdf' ,os.listdir(PDF_TYPE)))
# fileName = ["SI_HANV08177300.pdf"]

if __name__ == '__main__':
    for file in fileName:
        # Reset Current CONFIG
        print('====================',file,'====================')
        CURR_CONFIG = {}

        # Load PDF
        with open(PDF_TYPE + '/' + file, "rb") as f:
            pdf = pdftotext.PDF(f)

        page=pdf[0].split('\n')

        for page in pdf:
            lineList=page.split('\n')

        length=len(lineList)

        kwpos_temp={}
        for key in KEYWORD:
            found=[]
            for r in range(length):
                if (lineList[r].find(key)!=-1):
                    found.append([r,lineList[r].find(key)])
            kwpos_temp[key]=found

        
        kwpos={}
        
        for key in KEYWORD:
            l=len(kwpos_temp[key])
            pos=key.rfind('  ')
            if (pos!=-1): newKey=key[:pos] 
            else: newKey=key
            if (l!=1):
                for i in range(l): kwpos[newKey+str(i+1)]=kwpos_temp[key][i]
            else:
                kwpos[newKey]=kwpos_temp[key][0]
       
        for key in CONFIG:
            if (CONFIG[key]['isFlex']): 
                top=CONFIG[key]['endObject']['top']
                bot=CONFIG[key]['endObject']['bottom']
                topAndKeywordOnSingleLine=CONFIG[key]['topAndKeywordOnSingleLine']
                contentSameLineWithKeyword=CONFIG[key]['contentSameLineWithKeyword']
                toprow=-1
                botrow=-1
                minDistance=100000
                for kw in kwpos:
                    # print('In the loop key and kw',key,kw)
                    if (top==kw and abs(kwpos[kw][0]-kwpos[key][0])<minDistance): 
                        minDistance=abs(kwpos[kw][0]-kwpos[key][0])
                        toprow=kwpos[kw][0]
                minDistance=100000
                for kw in kwpos:
                    if (bot==kw and abs(kwpos[kw][0]-kwpos[key][0])<minDistance): 
                        minDistance=abs(kwpos[kw][0]-kwpos[key][0])
                        botrow=kwpos[kw][0]
                # print(key)
                if (top!=-1): 
                    if (topAndKeywordOnSingleLine): CONFIG[key]['row'][0]=toprow
                    elif (contentSameLineWithKeyword==0): CONFIG[key]['row'][0]=toprow+CONFIG[key]['row'][0]-kwpos[top][0]
                    else: CONFIG[key]['row'][0]=toprow+1
                if (bot!=-1): CONFIG[key]['row'][1]=botrow

        data={}
        for key in CONFIG:
            row=CONFIG[key]['row']
            column=CONFIG[key]['column']
            lines=lineList[row[0]:row[1]]
            data[key]='\n'.join([x[column[0]:column[1]] for x in lines])

        for key in CONFIG:
            if (CONFIG[key]['hasSubfield']):
                pos=0
                for subfield in CONFIG[key]['subfields']:
                    if CONFIG[key]['subfields'][subfield]!=10: 
                        result=re.search(CONFIG[key]['subfields'][subfield],data[key]).span()
                        data[key+'_'+subfield]=data[key][result[0]:result[1]+1]
                        pos=result[1]
                    else:
                        data[key+subfield]=data[key][pos:]
                del data[key]

        for key in data:
            data_pros=data[key]
            data_pros=data_pros.strip()
            data_pros=re.sub('\n+','\n',data_pros)
            data_pros=re.sub('\n\s+','\n',data_pros)
            print('%s:\n%s' % (key,data_pros))
