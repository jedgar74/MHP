[labels,x,y] = readColData('RankTop_17_7_2019_9_46.txt', 4, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'g','d','MINn'})
xlabel('rank')
