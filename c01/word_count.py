import re

CHUNK_SIZE = 100 # 这个数表示一次最多读取的字符长度

# 这个函数每次会接收上一次得到的 last_word，然后和这次的 text 合并起来处理。
# 合并后判断最后一个词有没有可能连续，并分离出来，然后返回。
# 这里的代码没有 if 语句，但是仍然是正确的，可以想一想为什么。
def parse_to_word_list(text, last_word):
    text = re.sub(r'[^\w ]', ' ', last_word + text)
    text = text.lower()
    cur_word_list = text.split(' ')
    cur_word_list, last_word = cur_word_list[:-1], cur_word_list[-1]
    return (filter(None, cur_word_list), last_word)

def solve():
    with open('in.txt', 'r') as fin:
        word_cnt = {}
        word_list, last_word = [], ''
        while True:
            text = fin.read(CHUNK_SIZE)
            if not text:
                # 读取完毕，中断循环
                break
            word_list, last_word = parse_to_word_list(text, last_word)

            for word in word_list:
                if word not in word_cnt:
                    word_cnt[word] = 1
                else:
                    word_cnt[word] += 1

        if last_word:
            if last_word not in word_cnt:
                word_cnt[last_word] = 1
            else:
                word_cnt[last_word] += 1

        sorted_word_cnt = sorted(word_cnt.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_word_cnt

words = solve()
with open('out.txt', 'w') as fout:
    for word,count in words:
        fout.write(f'{word} {count}\n')
