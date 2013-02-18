from igraph import *
import scp
import random
import heapq
import codecs

def write_communities_scp(graph, filename):
    comus = scp.communities_scp(graph,3,10)
    comu_names = scp.comuid2name(graph, comus)
    f = open(filename, 'w')
    for com in comu_names:
        s = ' '.join(com) + '\r\n'
        f.write(s.encode('gb18030'))
    f.close()

def get_graph(filename='../data/cn-topic.db'):
    from CommunityBuilder import CommunityBuilder
    cb = CommunityBuilder(filename)
    graph = cb.load_title_wordnet()
    return graph
    

def get_vertexcover_scp(graph=None, k=3, min_nodes=20):
    if graph == None:
        graph = get_graph()
    comus = scp.communities_scp(graph,k,min_nodes)
    
    idset = set()
    for ids in comus:
        idset.update(ids)
    sg = graph.subgraph(idset)
    sg.vs['weight'] = sg.pagerank()
    
    comu_names = scp.comuid2name(graph, comus)
    comu_ids = scp.comuname2id(sg,comu_names)
    cover = VertexCover(sg,comu_ids)

    ccp = ClusterColoringPalette(len(cover))
    #cls = ['black','gray','blue','green','white' ,'Maroon']
    for i,cluster in enumerate(cover):
         vlist = [v for v in sg.vs.select(cluster)]
         vlist.sort(key=lambda v:v['weight'], reverse=True)
         for v in vlist:
             try:
                 v['color'] = ccp[i]
             except:
                 v['color'] = ccp[i]
         for v in vlist[0:4]:
             v['label'] = v['name'].encode('utf8')
             #v['lable_cex'] = 1.5
             v['label_color'] = 'black'

    return cover

def draw_vertexcover_scp(graph=None, k=3, min_nodes=10):
    cover = get_vertexcover_scp(graph, k, min_nodes)
    plot(cover,bbox=(500,600), mark_groups=True,vertex_size=5,vertex_label_dist=5, edge_width=0.3, opacity=0.8)

def output_topn_kw(graph=None, outfile=None, n=5):
    import comdect
    graph = get_graph()
   
    lcd = comdect.LabelCommunityDetection(min_nodes=20)
    coms = lcd.detect(graph)
    f = codecs.open(outfile,'w','utf-8')
    for c in coms:
        sg = graph.subgraph(iter(c))
        sg.vs['weight'] = sg.pagerank(directed=True, weights='weight')
        topn = heapq.nlargest(n, sg.vs, key=lambda v:v['weight'])
        words = ' '.join((v['name'] for v in topn))
        f.write(words)
        f.write(u'\n')
    f.close()

def draw_vertexcluster(graph=None):
    import comdect
    graph = get_graph()
   
    lcd = comdect.LabelCommunityDetection(min_nodes=20)
    coms = lcd.detect(graph)
 
    idset = set()
    for ids in coms:
        idset.update(ids)
    sg = graph.subgraph(iter(idset))
    sg.vs['weight'] = sg.pagerank()    
    comu_names = scp.comuid2name(graph, coms)
    comu_ids = scp.comuname2id(sg,comu_names)
    membership = [0 for i in range(0,sg.vcount())]
    for idx,idset in enumerate(comu_ids):
        for vid in idset:
            membership[vid] = idx
    
    cluster = VertexClustering(sg, membership)
    ncluster = len(cluster)
    
    ccp = ClusterColoringPalette(ncluster)
    #cls = ['black','gray','blue','green','white' ,'Maroon']
    for i,c in enumerate(comu_ids):
        vlist = [v for v in sg.vs.select(c)]
        for v in vlist:
            try:
                v['color'] = ccp[i]
            except:
                v['color'] = ccp[i]
        topn = heapq.nlargest(5, vlist, key=lambda v:v['weight'])
        for v in topn:
            v['label'] = v['name'].encode('utf8')
            v['label_size'] = 18
            v['label_color'] = ccp[ncluster-i-1]
    fig = Plot()
    fig.add(cluster,bbox=(600,600), mark_groups=True,vertex_size=5, vertex_label_dist=2, edge_width=0.3, opacity=0.8)
    return fig