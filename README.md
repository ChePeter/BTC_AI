
PM_rand_600_t.bin  - random sequence

data_preparation.cpp - preparation and shuffle of data

dieharder_rand.txt - dieharder test of PM_rand_t.bin. dieharder -f PM_rand_600.bin -g 201 -a > dieharder_rand.txt

x600_btc_32_LH.bin, y600_btc_32_LH.bin - prepared data

train_test.py  - python+keras machine. train & test x600_btc_32_LH.bin, y600_btc_32_LH.bin


