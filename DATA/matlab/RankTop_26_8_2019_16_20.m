[labels,x,y] = readColData('RankTop_26_8_2019_16_20.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'ILS','HBBOSA','HBBOILS'})
xlabel('rank')
