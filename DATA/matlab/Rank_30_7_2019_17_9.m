[labels,x,y] = readColData('Rank_30_7_2019_17_9.txt', 9, 0, 1)
boxplot(y, 'orientation', 'horizontal', 'labels',{'GA---GA30pb02','GA---GA30pb05','GA---GA30pb10','GA---GA30pb01','GA---GA30ap10','GA---GA30ap02','GA---GA30ap01','GA---GA30ap05'})
xlabel('rank')
