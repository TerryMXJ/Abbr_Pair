import pickle

file_path = 'output/abbr_pair_result_12_10.pickle'
save_path = 'output/abbr_pair_result_sorted_12_10.txt'

if __name__ == '__main__':
    with open(file_path, 'rb') as f:
        data: dict = pickle.load(f)
    result: list = list((i, data[i]) for i in data.keys())
    sorted_result: list = sorted(result, key=lambda x: x[1], reverse=True)
    with open(save_path, 'w+') as f:
        for i in sorted_result:
            # 过滤abbr和full都是数字的pair
            if not i[0][0].isnumeric() and not i[0][1].isnumeric():
                f.write('{} - {}\n'.format(i[0], i[1]))
