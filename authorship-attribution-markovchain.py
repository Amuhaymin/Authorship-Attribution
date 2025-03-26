# import chardet
# import random
# pylint: disable=invalid-name
# import curses
import time
import json
import math

TRAINING_DATA_FILE = "victorian+era+authorship+attribution/dataset/Gungor_2018_VictorianAuthorAttribution_data-train.csv""" # pylint: disable=line-too-long
TEST_DATA_FILE = "victorian+era+authorship+attribution/dataset/Gungor_2018_VictorianAuthorAttribution_data.csv" # pylint: disable=line-too-long
README_FILE = "victorian+era+authorship+attribution/dataset/Gungor_2018_VictorianAuthorAttribution_readme.txt" # pylint: disable=line-too-long
MODEL_TRAINED_FILE = "saved_trained_model.json"
MODEL_TESTING_FILE = "saved_testing_model.json"

def get_similarity(markov_one, markov_two):
    '''
    Calculates a similarity score. Where the lower the score, the more similar the two matrices.
    Calculated by finding the sum of the squares of the differences for each entry.
    '''
    score = 0
    for prev_word in markov_one:
        if prev_word not in markov_two:
            continue
        for next_word in markov_one[prev_word]:
            # if next_word not in markov_two[prev_word]:
                # difference = markov_one[prev_word][next_word] - 0
            # else:
            if next_word in markov_two[prev_word]:
                difference = markov_one[prev_word][next_word] - markov_two[prev_word][next_word]
                score += math.pow(difference,2)
    return score

def TEST_create_document_author_pairs(file_name):
    '''
    Takes the csv for the victorian era authorship attribution dataset.
    Makes into an array of arrays of this form:
        [ 
            [document, author_id], 
            [document, author_id], 
            ... 
        ]
    Works only with this dataset, because the encoding is hardcoded.
    And because the last line in this dataset is an empty line, 
    and dealing with that has also been harcoded.
    '''
    document_author_pairs = []
    with open(file_name, 'rb') as file:
        data_as_bytes = file.read()
        data_as_string = data_as_bytes.decode('latin1')
        csv_lines =  data_as_string.split("\r\n")
        document_author_pairs = []
        for line in csv_lines[1:]:
            # print(line)
            return
            pair = line.split(",")
            document_author_pairs.append(pair)

        # delete the last element in the list because, for THIS dataset, its blank
        del document_author_pairs[-1]
    return document_author_pairs

# def create_document_author_pairs_in_place(file_name, training_list, testing_list, percent_training):
def create_document_author_pairs_in_place(file_name):
    '''
    Takes the csv for the victorian era authorship attribution dataset.
    Also takes two empty lists, and a percent between 0 and 1 inclusive.
    Makes into an array of arrays of this form:
        [ 
            [document, author_id], 
            [document, author_id], 
            ... 
        ]
    Works only with this dataset, because the encoding is hardcoded.
    And because the last line in this dataset is an empty line, 
    and dealing with that has also been harcoded.
    '''

    # document_author_pairs = []
    with open(file_name, 'rb') as file:
        data_as_bytes = file.read()
        data_as_string = data_as_bytes.decode('latin1')
        csv_lines =  data_as_string.split("\r\n")

        # document_quantity = len(csv_lines) - 1
        # threshold = document_quantity * percent_training
        document_author_pairs = []
        # count = 0
        for line in csv_lines[1:]:
            pair = line.split(",")
            # count += 1
            # if count == document_quantity:
            #     return # this dataset has a blank space in the last line
            # if count <= threshold:
            #     training_list.append(pair)
            # else:
            #     testing_list.append(pair)
            document_author_pairs.append(pair)

        # delete the last element in the list because, for THIS dataset, its blank
        del document_author_pairs[-1]
    return document_author_pairs

def create_author_dict(document_author_pairs):
# def create_author_dict_in_place(document_author_pairs, training_dict, testing_dict):
    '''
    Takes document_author_pairs list of this form:
        [ 
            [document, author_id], 
            [document, author_id], 
            ... 
        ]
    And returns a dict of this form:
        {
            author_id: 
                {
                    "documents": [document, document, ...],
                    "markov_chain": markov_chain
                }
            author_id: 
                {
                    ...
                }
            ...
        }
    '''
    authors = {}
    # count = 0
    for pair in document_author_pairs:
        # print(count,end="")
        # print(",",end="")
        # count += 1
        author_id = pair[1]
        document = pair[0]
        if author_id not in authors:
            authors[author_id] = {}
            authors[author_id]["documents"] = []
            authors[author_id]["markov_chain"] = {}
        authors[author_id]["documents"].append(document)
    return authors

def create_transition_counts(tokens):
    '''
    Takes a list of tokens and returns a transition_counts dict of this form:
    {
        prev_token:
        {
            next_token: count,
            next_token: count,
            ...
        },
        prev_token:
        {
            ...
        },
        ...
    }
    '''
    prev_token = tokens[0]
    transition_counts = {}
    for token in tokens[1:]:
        if prev_token not in transition_counts:
            transition_counts[prev_token] = {}
        if token not in transition_counts[prev_token]:
            transition_counts[prev_token][token] = 1
        else:
            transition_counts[prev_token][token] += 1
        prev_token = token
    return transition_counts

# def update_markov_chain_in_place(authors_markov_chains, author_id, markov_chain):

def add_transition_counts_in_place(original_counts, counts_to_add):
    '''
    Takes two transition_counts dicts, and adds the counts of the second to the first, in place.
    '''
    for prev_token in counts_to_add:
        if prev_token not in original_counts:
            original_counts[prev_token] = {}
        for next_token in counts_to_add[prev_token]:
            if next_token not in original_counts[prev_token]:
                original_counts[prev_token][next_token] = 0
            original_counts[prev_token][next_token] += counts_to_add[prev_token][next_token]

def make_into_markov_chain_in_place(transition_counts):
    '''
    Takes a transition_counts dict, and makes it into a markov_chain.
    The transition_counts dict has this form: 
        {prev_token: {next_token: count}}
    The markov_chain dict has this form: 
        {prev_token: next_token: probability}
    '''
    for prev_token in transition_counts:
        total = 0
        # get total count
        for next_token in transition_counts[prev_token]:
            total += transition_counts[prev_token][next_token]
        # compute probability: count / total count
        for next_token in transition_counts[prev_token]:
            count = transition_counts[prev_token][next_token]
            transition_counts[prev_token][next_token] = count / total
        # the transition counts dict is now a markov chain

# def classifer(author_markov_chains, document_to_classify):
    # get markov chain for document
    # compute similarities with markov chains of all authors
    # return author_id with highest similarity

def clear_line():
    '''Clears line using \r (carriage return) and the 033[K ansii escape sequence'''
    # time.sleep(1)
    # print("clear this line",end="",flush=True)
    # time.sleep(1)
    print("\r\33[K",end="",flush=True)
    # print("cleared",end="",flush=True)
    # time.sleep(1)
def move_cursor_up():
    '''Moves cursor up using the 033[F ansii escape sequence'''
    # time.sleep(1)
    # print("move up from here",end="",flush=True)
    # time.sleep(1)
    print("\33[1A\r",end="",flush=True)
    # time.sleep(1)



class ProgressTracker: #pylint: disable=missing-class-docstring
    #pylint: disable=missing-function-docstring
    def __init__(self):
        self.converted_documents = 0
        self.total_documents_to_convert = 0

        self.updated_transition_count = 0
        self.total_transition_counts_to_update = 0

        self.markov_chains_completed = 0
        self.total_markov_chains_to_complete = 0

        self.start_time = time.time()
        self.time_step = 0
        self.previous_duration = 0
        self.current_duration = 0
        self.estimated_total_duration = 0

        self.message = ""
        self.print_message()

    def print_message(self):
        self.message = f"{self.converted_documents} / {self.total_documents_to_convert} documents made into transition counts\
            \n{self.updated_transition_count} / {self.total_transition_counts_to_update} transition_counts updated\
            \n{self.markov_chains_completed} / {self.total_markov_chains_to_complete} authors markov chains completed\
            \nEstimated Total Duration: {round(self.estimated_total_duration)} seconds\
            \nDuration so far: {round(self.current_duration)} seconds"
        print(self.message,end="",flush=True)

    def clear_message(self):
        message_lines = self.message.split('\n')
        line_count = len(message_lines)
        count = 1
        while count < line_count:
            move_cursor_up()
            clear_line()
            count += 1

    def setDocumentTotal(self, total):
        self.converted_documents = 0
        self.total_documents_to_convert = total
        length = len(self.message)
        self.clear_message()
        self.print_message()
    def setTransitionCountTotal(self, total):
        self.updated_transition_count = 0
        self.total_transition_counts_to_update = total
        self.clear_message()
        self.print_message()
    def setMarkovChainTotal(self, total):
        self.markov_chains_completed = 0
        self.total_markov_chains_to_complete = total
        self.clear_message()
        self.print_message()
    def convertedDocument(self):
        self.current_duration = time.time() - self.start_time
        self.converted_documents += 1
        self.clear_message()
        self.print_message()
    def updatedTransitionCount(self):
        self.current_duration = time.time() - self.start_time
        self.updated_transition_count += 1
        self.clear_message()
        self.print_message()
    def madeMarkovChain(self):
        self.current_duration = time.time() - self.start_time
        self.markov_chains_completed += 1
        self.clear_message()
        self.print_message()
        if self.markov_chains_completed == self.total_markov_chains_to_complete:
            print()
            print(f"Time taken: {round(time.time() - self.start_time)} seconds")
        else:
            # # time_step = self.current_duration - self.previous_duration
            # # remaining = self.total_markov_chains_to_complete - self.markov_chains_completed
            percent_complete = self.markov_chains_completed / self.total_markov_chains_to_complete
            self.estimated_total_duration = self.current_duration / percent_complete
            self.previous_duration = self.current_duration
            # # self.estimated_total_duration = self.current_duration





def main():
    # print("hi")
    # print("hi")
    # progress_tracker = ProgressTracker()
    # for i in range(0,10):
    #     # print(f"{i} ",end="",flush=True)
    #     time.sleep(1)
    #     # stop = input("Continue?")
    #     # move_cursor_up()
    #     # move_cursor_up()
    #     progress_tracker.madeMarkovChain()

    '''The main function and entry point for the program.'''

    # train model
    choice = input("Type 'T' to train model (takes ~55s) or 'L' to load already trained model (takes ~10s)\n> ")
    # choice = "T"

    author_dict = {}
    training_author_dict = {}
    testing_author_dict = {}
    if choice == "T":
        print("Training model. Usually takes about 55s. ...")
        # change csv into a data structure that is easier to work with
        training_pairs = []
        testing_pairs = []
        # create_document_author_pairs_in_place(TRAINING_DATA_FILE, training_pairs, testing_pairs, percent_training) #pylint: disable=line-too-long
        document_author_pairs = create_document_author_pairs_in_place(TRAINING_DATA_FILE) #pylint: disable=line-too-long
        # print(document_author_pairs[0])
        # training_author_dict = create_author_dict(training_pairs)
        # testing_author_dict = create_author_dict(testing_pairs)
        author_dict = create_author_dict(document_author_pairs)
        # training_author_dict = author_dict
        # create_author_dict(document_author_pairs, training_author_dict, testing_author_dict)

        # split into training and testing
        percent_training = 80/100
        for author_id in author_dict: # pylint: disable=consider-using-dict-items
            training_author_dict[author_id] = {}
            training_author_dict[author_id]["documents"] = []
            training_author_dict[author_id]["markov_chain"] = {}
            testing_author_dict[author_id] = {}
            testing_author_dict[author_id]["documents"] = []
            testing_author_dict[author_id]["markov_chain"] = {}
            documents = author_dict[author_id]["documents"]
            threshold = len(documents) * percent_training
            total = len(documents)
            count = 1
            # print("author_dict")
            # print(author_dict[author_id]["documents"])
            for doc in documents:
                # print("in inner loop")
                # print(doc)
                if count <= threshold:
                    training_author_dict[author_id]["documents"].append(doc)
                else:
                    testing_author_dict[author_id]["documents"].append(doc)
                count += 1


        # print(f"testing_author_dict: {testing_author_dict}")

        # print(training_author_dict)
        # go through data structure and create a markov chain for each author
        progress_tracker = ProgressTracker()
        total = len(training_author_dict)
        progress_tracker.setMarkovChainTotal(total)
        # input("?")
        # count = 0 # debug
        # for author_id in author_dict: # pylint: disable=consider-using-dict-items
        for author_id in training_author_dict: # pylint: disable=consider-using-dict-items
            # count += 1 # debug
            transition_counts = {}
            # print("next")
            total = len(training_author_dict[author_id]["documents"])
            progress_tracker.setDocumentTotal(total)
            progress_tracker.setTransitionCountTotal(total)
            for document in training_author_dict[author_id]["documents"]:
                tokens = document.split(' ')
                transition_counts_to_add = create_transition_counts(tokens)
                progress_tracker.convertedDocument()
                add_transition_counts_in_place(transition_counts, transition_counts_to_add)
                progress_tracker.updatedTransitionCount()
            training_author_dict[author_id]["markov_chain"] = transition_counts
            make_into_markov_chain_in_place(transition_counts)
            progress_tracker.madeMarkovChain()
            # if count == 4: # debug
                # break

        save = input("Model trained!\nWould you like to save it? Takes ~35s. y/n\n> ")
        # save = "n"

        if save == "y":
            with open(MODEL_TRAINED_FILE, "w",encoding="utf-8") as file:
                print(f"saving to {MODEL_TRAINED_FILE} ...")
                start_time = time.time()
                json.dump(training_author_dict, file)
                print(f"Saved! Took {round(time.time()-start_time)} seconds.")
            print(f"testing_author_dict: {testing_author_dict}")
            with open(MODEL_TESTING_FILE, "w",encoding="utf-8") as file:
                print(f"saving to {MODEL_TESTING_FILE} ...")
                start_time = time.time()
                # json.dump(testing_author_dict, file)
                json.dump(training_author_dict, file)
                print(f"Saved! Took {round(time.time()-start_time)} seconds.")
        else:
            print("Model not saved.")

        # train
        # get doc and author
        # tokenize doc
        # make markov chain for doc, not normalized
        # add to authors markov chain
        # repeat with next doc and author
        # when done with all, calc prob for each one?
    elif choice == "L":
        # with open(MODEL_FILE, "r",encoding="utf-8") as file:
        #     print(f"loading model from {MODEL_FILE} ...")
        #     start_time = time.time()
        #     training_author_dict = json.load(file)
        #     print(f"Loaded! Took {round(time.time()-start_time)} seconds.")
        with open(MODEL_TRAINED_FILE, "r",encoding="utf-8") as file:
            print(f"loading model from {MODEL_TRAINED_FILE} ...")
            start_time = time.time()
            training_author_dict = json.load(file)
            print(f"Loaded! Took {round(time.time()-start_time)} seconds.")
        with open(MODEL_TESTING_FILE, "r",encoding="utf-8") as file:
            print(f"loading model from {MODEL_TESTING_FILE} ...")
            start_time = time.time()
            testing_author_dict = json.load(file)
            print(f"Loaded! Took {round(time.time()-start_time)} seconds.")
    else:
        print("exiting ...")
        return

    # for author_id in author_dict:
        # print("in for loop")
        # print(author_dict[author_id]["markov_chain"]["solomon"])
        # break
    # # classify
    # get document_author_pairs for test set
    # test_document_author_pairs = TEST_create_document_author_pairs(TEST_DATA_FILE)
    # print("before min score")
    print("Testing model. Takes about 3 minutes. ...")
    correct = 0
    tested = 0
    min_score = -1
    predicted_author_id = ""
    docs_per_author = 4
    for real_author_id in testing_author_dict: # pylint: disable=consider-using-dict-items
        documents = testing_author_dict[author_id]["documents"]
        docs_checked = 0
        for doc in documents:
            docs_checked += 1
            tokens = doc.split(' ')
            transition_counts = create_transition_counts(tokens)
            make_into_markov_chain_in_place(transition_counts)
            documents_markov_chain = transition_counts
            for candidate_author_id in training_author_dict:
                authors_markov_chain = training_author_dict[candidate_author_id]["markov_chain"]
                current_score = get_similarity(authors_markov_chain, documents_markov_chain)
                if current_score < min_score or min_score == -1:
                    min_score = current_score
                    predicted_author_id = candidate_author_id
            min_score = -1
            print(f"predicted author: {predicted_author_id}, actual author: {real_author_id}")
            tested += 1
            if predicted_author_id == real_author_id:
                correct += 1
            print(f"accuracy so far: {correct} / {tested} = {round(correct/tested*100)}%")
            if docs_checked >= docs_per_author:
                break
        # make transition count
        # make markov
        # get similarities

    # for pair in test_document_author_pairs:
    #     print(pair)
    #     break
    # get markov chain for test document
    # calcualte similarity score for each author
    # give author with highest similarity score
    # compare against actual author
    # update evals
if __name__ == '__main__':
    main()