import os
import sqlite3
import time

from Preprocessor import Preprocessor


class InvertedIndex:

    def __init__(self, db_name="database/ii.db", fresh=False):
        self.DB_NAME = db_name
        self.preprocessor = Preprocessor()
        if fresh:
            self.create_database()
            self.create_index(path="data")

    def create_database(self):
        try:
            print("CREATING DATABASE")
            conn = sqlite3.connect(self.DB_NAME)
            c = conn.cursor()
            with open("database/ddl.sql", encoding="utf8") as f:
                for ddl in f.read().split("###"):
                    print(ddl)
                    c.execute(ddl)
        except Exception as e:
            print(e)
        finally:
            conn.close()

    # Check if index words exists in index
    def check_word(self, w):
        word = self.preprocessor.remove_punctuations_from_word(w)
        try:
            conn = sqlite3.connect(self.DB_NAME)
            c = conn.cursor()
            c.execute("SELECT word FROM IndexWord WHERE word='" + word + "'")
            rows = c.fetchall()
            if len(rows) == 0:
                # Word does not exist yet, add it
                sql = "INSERT INTO IndexWord(word) VALUES (?)"
                c.execute(sql, [word])
                conn.commit()
            # Word exists
        except Exception as e:
            print("check_word ERROR")
            print(word)
            print(e)
        finally:
            conn.close()

    def add_posting(self, indexword, posting):
        self.check_word(indexword)
        try:
            conn = sqlite3.connect(self.DB_NAME)
            sql = "INSERT INTO Posting(word, documentName, frequency, indexes) VALUES (?, ?, ?, ?)"
            c = conn.cursor()
            c.execute(sql, posting)
            conn.commit()
        except Exception as e:
            print("add_posting ERROR")
            print(posting)
            print(e)
        finally:
            conn.close()

    def create_index(self, path="data"):
        folders = ["e-prostor.gov.si", "e-uprava.gov.si", "evem.gov.si", "podatki.gov.si"]
        print("Creating index...")
        for folder in folders:
            print(folder)
            files = os.listdir(path + "/" + folder)
            for file in files:
                file_path = path + "/" + folder + "/" + file
                print(file_path)
                if os.path.isfile(file_path) and file_path.endswith(".html"):
                    with open(file_path, encoding="utf8") as f:
                        page = self.preprocessor.preprocess_webpage(f.read())
                        document = self.preprocessor.preprocess_and_clean_text(page)
                        text = set(self.preprocessor.preprocess_text(page))
                        for word in text:
                            frequency = document.count(word)
                            indexes = ",".join([str(i) for i, x in enumerate(document) if x == word])
                            posting = (word, file_path, frequency, indexes)
                            self.add_posting(word, posting)

        print("DONE!")

    def construct_result(self, posting, snippet_range=3):
        # TODO: snippets should be from ORIGINAL text, not preprocessed or tokenized one
        #  (words should be together with punctuations etc.)
        word = posting[0]
        document = posting[1]
        frequency = str(posting[2])
        indexes = [int(x) for x in posting[3].split(",")]
        snippets = []

        with open(document, encoding="utf8") as f:
            page = self.preprocessor.preprocess_webpage(f.read())
            doc = page.strip().split()
            for i in indexes:
                i_from = max(i - snippet_range, 0)
                i_to = min(i + snippet_range + 1, len(doc) - 1)
                snippets.append(doc[i_from:i_to])
        snippets = " ... ".join([" ".join(x) for x in snippets])
        return frequency, document, snippets

    def process_all_files(self, words):
        results = {}
        path = "data"
        folders = ["e-prostor.gov.si", "e-uprava.gov.si", "evem.gov.si", "podatki.gov.si"]
        for folder in folders:
            # print(folder)
            files = os.listdir(path + "/" + folder)
            for file in files:
                file_path = path + "/" + folder + "/" + file
                # print(file_path)
                if os.path.isfile(file_path) and file_path.endswith(".html"):
                    with open(file_path, encoding="utf8") as f:
                        page = self.preprocessor.preprocess_webpage(f.read())
                        document = self.preprocessor.preprocess_and_clean_text(page)
                        text = set(self.preprocessor.preprocess_text(page))
                        for word in text:
                            if word not in words:
                                continue
                            frequency = document.count(word)
                            if frequency == 0:
                                continue
                            indexes = ",".join([str(i) for i, x in enumerate(document) if x == word])
                            posting = (word, file_path, frequency, indexes)
                            res = self.construct_result(posting)
                            if res[1] in results:
                                results[res[1]].append(res)
                            else:
                                results[res[1]] = [res]
        return results

    def search_words(self, words, use_index):
        if use_index:
            results = {}
            try:
                conn = sqlite3.connect(self.DB_NAME)
                c = conn.cursor()
                for word in words:
                    word = self.preprocessor.remove_punctuations_from_word(word)
                    c.execute("SELECT * FROM Posting WHERE word='" + word + "'")
                    rows = c.fetchall()
                    for row in rows:
                        res = self.construct_result(row)
                        if res[1] in results:
                            results[res[1]].append(res)
                        else:
                            results[res[1]] = [res]
            except Exception as e:
                print("search_word ERROR")
                print(word)
                print(e)
            finally:
                conn.close()
        else:
            results = self.process_all_files(words)

        # MERGE BY DOCUMENT
        merged_results = []
        for _, item in results.items():
            frequency = 0
            document = item[0][1]
            snippets = []
            for i in item:
                frequency += int(i[0])
                snippets.append(i[2])
            merged = (frequency, document, " ... ".join(snippets))
            merged_results.append(merged)

        # SORT AND PRINT
        results = sorted(merged_results, key=lambda res: res[0], reverse=True)
        for res in results:
            print("{0: <11} {1: <50} {2: <}".format(str(res[0]), res[1], res[2]))

    def query(self, query, use_index):
        query = self.preprocessor.preprocess_text(query)
        print(query)
        start_time = time.time()
        print("{0: <11} {1: <50} {2: <}".format("Frequencies", "Document", "Snippet"))
        print("{0: <11} {1: <50} {2: <}".format("-----------", "--------------------------------------------------",
                                                "----------------------------------------------------------"))
        self.search_words(query, use_index)
        print("**************")
        print("Took " + str(time.time() - start_time) + " seconds.")
        print("**************")
