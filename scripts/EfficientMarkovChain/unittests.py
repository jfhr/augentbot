#! python3.6

from .MemoryEfficientMarkovChain import MarkovChain

with open('text_sample.txt') as file:
    text_sample: str = file.read()


def test_memory_usage():
    mc: MarkovChain = MarkovChain()
    mc.generateDatabase(text_sample)
    res = mc.generateString()
    print(res)


if __name__ == '__main__':
    test_memory_usage()
