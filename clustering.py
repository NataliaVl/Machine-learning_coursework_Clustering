import connection
import nltk
import json
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import connection
import numpy as np
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
from sklearn.cluster import AgglomerativeClustering

def load_stopwords():
    with open("stopwords.json", "r", encoding="utf-8") as read_file:
        stopwords = json.load(read_file)
    return stopwords


def check_text_for_stopwords(words, stopwords):
    words_without_stopwords = []
    words = [element.lower() for element in words]  # преобразование списка в нижний регистр

    count = 0
    for text_word in words:
        for stopword in stopwords:
            if text_word == stopword:
                count += 1
                # words.remove(text_word)

        if count == 0:
            words_without_stopwords.append(text_word)
        count = 0

    return words_without_stopwords

def create_processed_texts_list(words_without_stopwords, processed_texts_list, id):
    new_text = ""
    for word in words_without_stopwords:
        new_text += word + " "
    processed_texts_list.append(new_text)
    count_words_in_text.append(len(words_without_stopwords))
    hash_list.append(id)

def get_stems_frequency(vector_list, count_words_in_text):
    # преобразование numpy.int64 во numpy.float64
    vector_list = np.float64(vector_list)

    i = 0
    for vector in vector_list:
        j = 0
        count_text = count_words_in_text[i]
        for elem_vector in vector:
            if elem_vector != 0:
                frequency = round(elem_vector / count_text * 100, 3)
                #vector_list[vector][elem_vector]
                vector_list[i][j] = frequency
            j = j + 1
        i = i + 1

    return vector_list

def Create_Bag_of_Words(documents, count_words_in_text):
    # Design the Vocabulary
    # The default token pattern removes tokens of a single character. That's why we don't have the "I" and "s" tokens in the output
    count_vectorizer = CountVectorizer()

    # Create the Bag-of-Words Model
    bag_of_words = count_vectorizer.fit_transform(documents)
    bag = bag_of_words.toarray()
    # print(bag)

    bag_with_frequency = get_stems_frequency(bag, count_words_in_text)

    # Show the Bag-of-Words Model as a pandas DataFrame
    feature_names = count_vectorizer.get_feature_names()  # названия стемм

    df = pd.DataFrame(bag_with_frequency, columns=feature_names)
    # print(df)
    # названия строк: номер строки соответствует индексу данного текста в массиве
    # названия столбцов: неповторяющиеся стеммы
    return bag_with_frequency

def cluster_kmeans(count_clusters, bag):
    kmeans = KMeans(n_clusters=count_clusters, random_state=0).fit(bag)
    clusters_list = kmeans.labels_
    return clusters_list

def cluster_miniBatchKMeans(count_clusters, bag):
    mbk = MiniBatchKMeans(n_clusters=count_clusters, random_state=0, batch_size=6)
    #mbk.fit_transform(bag)
    mbk.fit(bag)
    clusters_list = mbk.labels_
    return clusters_list

def cluster_agglomerativeClustering(count_clusters, bag):
    agglomer = AgglomerativeClustering(n_clusters=count_clusters).fit(bag)
    clusters_list = agglomer.labels_
    return clusters_list

def distribute_texts_on_clusters(clusters_list, hash_list):
    # создание списка списков
    # кластер 1 [hash1, hash3]
    # кластер 2 [hash2]
    list_clusters = init_list_of_objects(count_clusters)
    for i in range(len(clusters_list)):
        cluster = int(clusters_list[i])
        hash = hash_list[i]
        #col = len(list_clusters[cluster])
        list_clusters[cluster].append(hash)
    return list_clusters

def init_list_of_objects(size):
    list_of_objects = list()
    for i in range(0, size):
        list_of_objects.append( list() ) #different object reference each time
    return list_of_objects

def show_resalt(list_clusters):
    i = 0
    for clust in list_clusters:
        print("Cluster " + str(i) +":")
        for item in clust:
            #print("hash of text: " + item)

            for text in col.find({"_id": item}):
                title = text["title"]
                description = text["description"]
                print("title: " + title)
                print("description: " + description)
        print("__________________")
        i = 1 + int(i)

def serialize(list_clusters, res):
    i = 0
    for clust in list_clusters:
        res = res + "CLUSTER " + str(i) + ":\n"
        for item in clust:
            # print("hash of text: " + item)
            for text in col.find({"_id": item}):
                title = text["title"]
                description = text["description"]
                res = res + "title: " + title
                res = res + "description: " + description + '\n\n'
        res = res + "\n***\n"
        i = 1 + int(i)
    return res

def result_kmeans(bag):
    res = "Метод K-means.\n\n"
    kmeans = cluster_kmeans(count_clusters, bag)
    clusters_kmeans = distribute_texts_on_clusters(kmeans, hash_list)
    result = serialize(clusters_kmeans, res)
    return result

def result_mbk(bag):
    res = "Метод Mini batch K-means.\n\n"
    mbk = cluster_miniBatchKMeans(count_clusters, bag)
    clusters_mbk = distribute_texts_on_clusters(mbk, hash_list)
    result = serialize(clusters_mbk, res)
    return result

def result_agglomerat(bag):
    res = "Agglomerative Clustering.\n\n"
    agglomerat = cluster_agglomerativeClustering(count_clusters, bag)
    clusters_agglomerat = distribute_texts_on_clusters(agglomerat, hash_list)
    result = serialize(clusters_agglomerat, res)
    return result

def all_methods(bag):
    result = result_kmeans(bag) + result_mbk(bag) + result_agglomerat(bag)
    return result





col = connection.connection_mongodb_texts()
count_clusters = 6

punctuation_mark = ['.', ',', ':', ';', '?', '!', '...', '—', '"', '(', ')', '/', '№', '$', '%', '*', '&', '`', '~',
                        '#', '@', '+', '»', '«']
stopwords = load_stopwords()
stopwords.extend(punctuation_mark)

processed_texts_list = []  # =document. данные на вход для создания мешка
hash_list = []  # список хеш-сумм
count_words_in_text = []  # список количеста слов. индекс совпадает с индексом hash_list

res = ""


def main():
    # ЭКСПОРТ ТЕКСТА
    for item in col.find({}):
        text = item["doc"]
        id = item["_id"]

        words = nltk.word_tokenize(text)

        words_without_stopwords = check_text_for_stopwords(words, stopwords)

        create_processed_texts_list(words_without_stopwords, processed_texts_list, id)

    bag = Create_Bag_of_Words(processed_texts_list, count_words_in_text)  #
    return bag


