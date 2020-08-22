import os
import xlsxwriter
import math

documents = os.listdir('./0Mytest')
n = len(documents)
print("We have "+str(n)+" documents.") 


def Preparation(text):
    Faults = [",", "!" , "'s" , "?" , ":" , "(" , ")" , "-" , '"']
    text = text.lower()
    for x in Faults:
        text = text.replace( x , "")
    words = text.split()
    for i in range(len(words)):
        if words[i][-1] == ".":
            words[i] = words[i].replace("." , "")
    return words


x = ["t-e-r-m","f-r-e-q-u-e-nc-y"]
for i in documents:
    x.append(i)
matrix = [x]

x1 = ["t-e-r-m"]
for i in documents:
    x1.append(i)
matrix_tf = [x1]

x2 = ["t-e-r-m","d-f"]
matrix_df = [x2]


for d in documents:
    text_IO = open('./0Mytest/'+d , "rt")
    text = text_IO.read()
    words = Preparation(text)
    for word in words:
        if word in [row[0] for row in matrix]:
            matrix_words = [row[0] for row in matrix]
#             matrix[matrix_words.index(word)][1]+= 1
            matrix[matrix_words.index(word)][matrix[0].index(d)] = 1
            matrix_tf[matrix_words.index(word)][matrix_tf[0].index(d)] += 1
        else:
            l = [word , 1]
            for j in range(n):
                l.append(0) 
            matrix.append(l)
            l_tf = [word]
            for j in range(n):
                l_tf.append(0) 
            matrix_tf.append(l_tf)
            matrix_words = [row[0] for row in matrix]
            matrix[matrix_words.index(word)][matrix[0].index(d)] = 1
            matrix_tf[matrix_words.index(word)][matrix_tf[0].index(d)] = 1
 
# computing focument frequency
matrix_words = [row[0] for row in matrix]
for i in range(1,len(matrix_words)):
    freq = 0
    for j in range(2,len(matrix[0])):
        if matrix[i][j] == 1:
            freq += 1
    matrix_df.append([matrix[i][0],freq])
    matrix[i][1]= freq
            

workbook = xlsxwriter.Workbook('./term_document.xlsx')
worksheet = workbook.add_worksheet()
row = 0
for col, data in enumerate(matrix):
    worksheet.write_column(row, col, data)
workbook.close()

workbook = xlsxwriter.Workbook('./term_frequency.xlsx')
worksheet = workbook.add_worksheet()
row = 0
for col, data in enumerate(matrix_tf):
    worksheet.write_column(row, col, data)
workbook.close()

workbook = xlsxwriter.Workbook('./document_frequency.xlsx')
worksheet = workbook.add_worksheet()
row = 0
for col, data in enumerate(matrix_df):
    worksheet.write_column(row, col, data)
workbook.close()


def w_t(t_f):
    if t_f > 0:
        return 1 + math.log10(t_f)
    else:
        return 0
    
def idf(N,df):
    return math.log10(N/df)

def norm_q(x,w_t):
    divisor = 0
    for i in w_t[1:]:
        divisor += i**2
    if divisor == 0:
        return 0
    else:
        return x/(math.sqrt(divisor))

def score(l):
    score = 0
    for i in l[1:]:
        score += i
    return score


def score_computer(query,matrix_tf,matrix_df,documents,n):
    scores = []
    score_table = []
    h = ["documents","scores"]
    score_table = [h]
    hq = ["t-e-r-m","q_tf_raw","q_tf_wt","q_df","q_idf","q_wt","q_norm"]
    mat = [hq]
    for term in query:
        if term in [row[0] for row in mat]:
            matrix_words = [row[0] for row in mat]
            mat[matrix_words.index(term)][1] += 1  #q_tf_raw
        else:
            l = [term]
            for j in range(6):
                l.append(0) 
            mat.append(l)
            matrix_words = [row[0] for row in mat]
            mat[matrix_words.index(term)][1] = 1 #q_tf_raw
    matrix_words = [row[0] for row in mat]
    for term in matrix_words[1:len(matrix_words)]:
        mat[matrix_words.index(term)][2] = w_t(mat[matrix_words.index(term)][1])  #q_tf_wt
        mat_df_words = [row[0] for row in matrix_df]
        mat[matrix_words.index(term)][3] = matrix_df[mat_df_words.index(term)][1]  #q_df
        mat[matrix_words.index(term)][4] = idf(n,mat[matrix_words.index(term)][3])  #q_idf
        mat[matrix_words.index(term)][5] = (mat[matrix_words.index(term)][2])*(mat[matrix_words.index(term)][4])  #q_wt
    w_ts = [row[5] for row in mat]
    for term in matrix_words[1:len(matrix_words)]:
        mat[matrix_words.index(term)][6] = norm_q(mat[matrix_words.index(term)][5],w_ts)  #q_norm
    for d in range(len(documents)):
        hd = ["term","d_tf_raw","d_tf_wt","d_norm","pro_d"]
        mat2 = [hd]
        matrix_words = [row[0] for row in mat]
        for term in matrix_words[1:]:
            l = [term]
            for j in range(4):
                l.append(0) 
            mat2.append(l)
            mat2_words = [row[0] for row in mat2]
            matrix_tf_words = [row[0] for row in matrix_tf]
            mat2[mat2_words.index(term)][1] = matrix_tf[matrix_tf_words.index(term)][d+1]       #d_tf_raw
            mat2[mat2_words.index(term)][2] = w_t(mat2[mat2_words.index(term)][1])      #d_tf_wt
        w_ts = [row[2] for row in mat2]
        for term in matrix_words[1:len(matrix_words)]:   
            mat2[mat2_words.index(term)][3] = norm_q(mat2[matrix_words.index(term)][2],w_ts)  #d_norm
            mat2[mat2_words.index(term)][4] = (mat[mat2_words.index(term)][6])*(mat2[mat2_words.index(term)][3])  #pro_d
        score_tmp = [row[4] for row in mat2]
        scores.append(score(score_tmp))
        score_table.append([documents[d],score(score_tmp)])
        del mat2
    workbook = xlsxwriter.Workbook('./score_table.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0
    for col, data in enumerate(score_table):
        worksheet.write_column(row, col, data)
    workbook.close()
    scores, documents = (list(x) for x in zip(*sorted(zip(scores,documents))))
    return scores,documents


def search(q,matrix_tf,matrix_df,documents,n,k):
    q_words = Preparation(q)
    scores,documents = score_computer(q_words,matrix_tf,matrix_df,documents,n)
    result = documents[n-k:]
#     print(result)
    result = reversed(result)
    return result


k = int(input("Please enter k : "))
while(1==1):
    q = input("Please Enter The Query :")  
    result = search(q,matrix_tf,matrix_df,documents,n,k)
    output = "Result : "
    print(result)
    for i in result:
        output += " "+i+" "
    print(output)



