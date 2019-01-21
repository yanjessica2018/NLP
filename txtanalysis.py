################## Functions
# (1) TF and DF;
def tfdic(text):  #text = rob['lossdespt_c']; 
    dic={}
    for i in text:
        for j in i.split():
            if j in dic:
                dic[j]+=1  
            else:
                dic[j]=1
    return dic  
rob_tfdic=tfdic(rob['lossdespt_c'])

def dfdic(text):
    dic={}
    for i in text: 
        for j in set(i.split()):
            if j in dic:
                dic[j]+=1
            else:
                dic[j]=1
    return dic
rob_dfdic=dfdic(rob['lossdespt_c'])    
for i in sorted(list(set([v for k, v in rob_dfdic.items()])), reverse=True):  #Print out the vocabulary: from most frequent to less frequent  
    print(i, ':')
    a=[k for k, v in rob_dfdic.items() if v==i]
    print(a)
    print(len(a))

#(2) Check % of data availability (for Python 2); 
ls=['LossCauseCode', 'LossCauseDescription', 'LossCauseDetailCode', 'LossCauseDetailDescription', 'LossDescription']
print('Overall data availabilty')
getcontext().prec = 2
for i in ls:
    a=Decimal(datac[i].value_counts().sum())/Decimal(len(datac.index))
    print('{}: {}'.format(i, a))

#(3) Recode the feature to categorize;
def lcd(x):
    if pd.isnull(x)==True:
        return 'null'
    elif x in ['allother_Ext', 'unknown_Ext']:
        return 'alloth_unkn'
    else:
        return 'useful'
sel['LossCauseCode_2']=sel['LossCauseCode'].apply(lcd)

#(4) Coordinate the similar words; 
def similiar(w):
    if w=='theif':
        return 'theft'
    elif w=='stole':
        return 'steal'
    elif w=='build':
        return 'building'
    elif w=='broken':
        return 'break'
    elif w=='gunpoint':
        return 'gun', 'point'
    elif w=='knifepoint':
        return 'knife', 'point'
    elif w=='armed':
        return 'arm'
    elif w=='pointed':
        return 'point'
    elif w in ['robbed', 'robbery']:
        return 'rob'
    elif w=='unk':
        return 'unknown'
    else:
        return w
cmall['lossdespt_c2']=cmall['lossdespt_c'].apply(lambda x: [similiar(i) for i in x.split()])


#(5) Create CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer
cvec = CountVectorizer(lowercase=False)
wm = cvec.fit_transform(rob['lossdespt_c'])  #change rob['lossdespt_c'] to others for generating countvectorizer; 

def wm2df(wm, feat_names):
    doc_names = ['Doc{:d}'.format(idx) for idx, _ in enumerate(wm)]
    df = pd.DataFrame(data=wm.toarray(), index=doc_names,
                      columns=feat_names)
    return(df)

tokens = cvec.get_feature_names()
a=wm2df(wm, tokens)

a['rob_sum']=a['rob']+a['robbed']+a['robbery']  #create higher level counters; 
a['gun_sum']=a['gun']+a['gunpoint']
a['point_sum']=a['gunpoint']+a['point']+a['pointed']+a['knifepoint']

b=a.corr()
c=b.loc['point_sum', :].sort_values()  #check individual corr; 


#(6) Create new variable; 
def robbery(text):
    if 'rob' in text.split() or 'robbed' in text.split() or 'robbery' in text.split() or 'gun' in text.split() or 'gunpoint' in text.split(): 
        return 'Robbery'
lcnull['new']=lcnull['lossdespt_c'].apply(robbery)


#(7) Create new variables based on key search;
key1=['rob', 'robbery', 'robbed']
key2=['rob', 'robbery', 'robbed']

lcnull['lossdespt_c'].fillna('', inplace=True)
lcnull2=lcnull.iloc[:, :]

ct1=[]
ct2=[]
for i in range(len(lcnull2['lossdespt_c'])): 
    row=lcnull2.iloc[i, 5]
    c1=0
    c2=0
    for j in set(row.split()):
        c1+=(j in key1)
        c2+=(j in key2)
        
    ct1.append(c1)
    ct2.append(c2)
    
lcnull2['c1']=ct1
lcnull2['c2']=ct2

#(8) Check words surrounding the key values
res=[]
def sexword(b):
    global res  #global to interact with function and store values; 
    c=b.split()
    ind1 = [i for i, x in enumerate(c) if x == "sexual"]
    ind2 = [i for i, x in enumerate(c) if x == "sexually"]

    if 'sexual' in c:
        for i in ind1:
            res.append(c[i])
            res.append(c[i+1])
            res.append(c[i-1])
            res.append(c[i-2])
    elif 'sexually' in c: 
        for j in ind2:
            res.append(c[j])
            res.append(c[j+1])
            res.append(c[j-1])
            res.append(c[j-2])
            
a['pos']=a['lossdespt_c'].apply(sexword)



################## Dataframes
#Select the dataframe based on string values; 
searchfor = ['Bodily', 'Bodiliy']
data_bodyinjury=datac[datac['c_cvg_cvgdescription'].str.contains('|'.join(searchfor), case=False, na=False)] 

#Subset the dataframe; 
c3_2=sel[sel['LossCauseDetailCode'].isin(['allother', 'other','unknowncauseoranother', 'unknown'])]  #selected rows/columns
extra=lcnull2.loc[(lcnull2['c1']>0) & (lcnull2['c2']>0), [i for i in list(lcnull2.columns) if i not in ['c1', 'c2']]]  #conditional on rows, exclude certain columns; 
a=part.loc[(part['lossdespt_c'].str.contains('sexual')) | (part['lossdespt_c'].str.contains('sexually')), :]  #conditional on string rows
test=datac[(datac['c_cvg_lob']=='C09 ') & (datac['ClaimType']=='Prop_Claim') & (datac['c_cvg_cvg']==17) & (datac['aslob']==51)]  #mutiple row conditions

#Create crosstab dataframes; 
k=pd.crosstab(sel['LossCauseDescription'].fillna('missing'), sel['TypeOfLossCode'].fillna('missing'))  #fill the missing part of both; 

#Merge & append; 
a=a.merge(b, left_index=True, right_index=True)  
allmix=mix.append(robbery_n)

#De-dup the dataframe
sel.drop_duplicates(inplace=True) 


################## Features
#Check the values; 
sub['ExposureType'].value_counts(dropna=False).sum()
pd.DataFrame(sel['sum'].value_counts()).apply(lambda x: x/233382)
sel['LossCauseCode_1']=sel['LossCauseCode'].isnull()  #Null check;
pd.crosstab(sel['LossCauseCode_1'], sel['LossCauseDescription_1']).apply(lambda x: x/len(sel.index), axis=1)  #crosstab % check

#Create the boolean values; 
sel['level_1']=(sel['LossCauseCode_2']=='useful') + (sel['LossCauseDescription_2']=='useful')>0
sel['both_levels']=(sel['level_1']==True) & (sel['level_2']==True)
sel['either_levels']=(sel['level_1']==True) | (sel['level_2']==True)
sel['sum']=(1-sel['LossCauseCode_1'])+(1-sel['LossCauseDescription_1'])+(1-sel['LossCauseDetailCode_1'])+(1-sel['LossCauseDetailDescription_1'])
sel['both_levels'].value_counts()/len(datac.index)

dsn['LossCauseDetailDescription_']=dsn.index  #Create feature based on index

b.rename(columns={0: 'columns_sum'}, inplace=True) #Rename column; 

list(c4.index) #To list out All values of certain feature (value_counts() first, then list out the index);


#Trim the strings; 
c1['values']=c1.index.str.strip()
c1.sort_values(by='values')

#Normalize the unicode print-out (for Python 2)
res = repr([x.encode(sys.stdout.encoding) for x in set(res)]).decode('string-escape')   


################## Files
data.to_hdf('text.h5', key='text', mode='w') #save the quick temp file; 
datac=pd.read_hdf('text.h5', 'text')

b.to_csv('losscause.txt', sep="\t") #individual table; 

writer = pd.ExcelWriter('losscause_values.xlsx', engine='xlsxwriter')  #Excel table with different sheets;
dsn=pd.DataFrame((sel['LossCauseCode']).value_counts())
dsn.to_excel(writer, sheet_name='lc_code', encoding='utf8')
dsn=pd.DataFrame((sel['LossCauseDescription']).value_counts())
dsn.to_excel(writer, sheet_name='lc_descp', encoding='utf8')
writer.save()























