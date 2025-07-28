import os
paths = ['test','train','val']
l_path = 'dataset/labels/'
i_path = 'dataset/images/'
tamanhoDataset = {}
for path in paths:
    image_path = os.path.join(i_path,path)
    label_path = os.path.join(l_path,path)
    labels = os.listdir(label_path)
    tamanhoDataset[path] = len(labels)
    for label in labels:
        if os.stat(os.path.join(l_path,path,label)).st_size == 0:
            image = label.replace('.txt','.png')
            os.system(f'rm {os.path.join(i_path,path,image)}')
            os.system(f'rm {os.path.join(l_path,path,label)}')

print(tamanhoDataset)
