import pickle


if __name__ == '__main__':
    file_path = "output/classes_without_comment.pickle"
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
    print('whole data info: %d' % len(data))
    for i in range(40):
        save_path = 'output/split_classes/classes_without_comment_%s.pickle' % i
        save_data = data[i*1000:(i+1)*1000]
        print('start save No.%d' % i)
        with open(save_path, 'wb') as f:
            pickle.dump(save_data, f)
