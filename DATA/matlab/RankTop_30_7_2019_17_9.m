[labels,x,y] = readColData('RankTop_30_7_2019_17_9.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'GA---GA30pb05','GA---GA30pb02','GA---GA30pb10'})
xlabel('rank')
