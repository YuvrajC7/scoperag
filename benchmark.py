import time
import numpy as np
from core import KnowledgeStore,seed
from reporting import save_report

if __name__=='__main__':
    s=KnowledgeStore();seed(s,100)
    totals={};latencies=[]
    for mode in ['lexical','character','hybrid']:
        correct=queries=leaks=0
        for tenant in ['acme','beacon']:
            for i in range(100):
                if i%4==0:continue
                topic=['refund','retention','invoice','export','subscription'][i%5]
                for q in [f'product{i} {topic} window',f'prodct{i} {topic} exceptions']:
                    t=time.perf_counter();r=s.retrieve(tenant,'reader',q,mode=mode);latencies.append((time.perf_counter()-t)*1000)
                    correct+=bool(r['hits'] and r['hits'][0]['id']==f'{tenant}-{i}');queries+=1
                    leaks+=sum(not h['id'].startswith(tenant) or (h['id'].split('-')[-1].isdigit() and int(h['id'].split('-')[-1])%4==0) for h in r['hits'])
        totals[mode]={'queries':queries,'top1_correct':int(correct),'top1_accuracy':correct/queries,'unauthorized_hits':leaks}
    passed=0
    for i in range(100):
        if i%4==0:continue
        q=f'product{i}';s.retrieve('acme','reader',q)
        s.put(f'acme-{i}','acme',q,'revoked',['manager'])
        passed+=all(h['id']!=f'acme-{i}' for h in s.retrieve('acme','reader',q)['hits'])
    s.close()
    save_report({'corpus_documents':202,'retrieval':totals,'revocation_tests':75,'revocation_passed':passed,
      'median_retrieval_ms':round(float(np.median(latencies)),3),'p95_retrieval_ms':round(float(np.percentile(latencies,95)),3),
      'answer_mode':'Offline extractive; external LLM integration not benchmarked.',
      'relevance_labels':'Synthetic exact product IDs; one matching authorized policy per query. Not an external relevance benchmark.'})
