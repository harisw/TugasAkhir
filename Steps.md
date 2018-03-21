# A. Preprocessing
    1. Delete all outlier, such as : "No responses"
    2. Lowercasing all documents
    3. Removing punctuation and number(including "st"/"nd"/etc)
    4. Removing stopwords
    5. Lemmatizating
# B. Building bow
    1. Create dictionary table that containing this column : id, word, number of occurences on each class, word probabilities on each class 
    2. Make empty array to count word occurences among all document
    3. Iterate through all the documents
        2.1 Iterate through all the word on each document
            2.1.1 Check within the dictionary's table, 
                if it is there increment the number of occurences on corresponding class
                else insert it into the table as new row, and add 1 as the number of occurences


*P.S : each class probs = number of word occurences on x Class / number of x Class 
