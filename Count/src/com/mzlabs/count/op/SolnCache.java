package com.mzlabs.count.op;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.Map;
import java.util.TreeMap;

import com.mzlabs.count.util.IntVec;

public final class SolnCache {
	
	private static final class StoreEntry {
		public final int[] key;
		public final BigInteger value;
		public long lastAccess;
		
		public StoreEntry(final int[] key, final BigInteger value, final long lastAccess) {
			this.key = key;
			this.value = value;
			this.lastAccess = lastAccess;
		}
	}
	
	private final int nStores = 1377;
	private final long bigSize = 5000000;
	private final int initialSizeTargetI = (int)(bigSize/nStores) + 5;
	private final long baseTimeMS;
	private final ArrayList<Map<int[],StoreEntry>> hotStores = new ArrayList<Map<int[],StoreEntry>>(nStores);  // sub-stores (to shallow trees), also sync on these
	private final int[] storeBound = new int[nStores]; // heuristic triggers for expensive attempted cache shrink
	
	
	public SolnCache() {
		baseTimeMS = System.currentTimeMillis();
		for(int i=0;i<nStores;++i) {
			hotStores.add(new TreeMap<int[],StoreEntry>(IntVec.IntComp));
		}
		clear(); // get into initial state
	}
	
	/**
	 * Look for a cached value of f(x), if none such create a record, block on the record and compute f(x) (so only one attempt to compute f(x))
	 * @param f
	 * @param x not null, x.length>0
	 * @return
	 */
	public BigInteger evalCached(final CachableCalculation f, final int[] xin) {
		// find the sub-store
		final long time = System.currentTimeMillis();
		final int storeIndex;
		final Map<int[],StoreEntry> hotStore;
		{
			int subi = Arrays.hashCode(xin)%nStores;
			if(subi<0) {
				subi += nStores;
			}
			storeIndex = subi;
			hotStore = hotStores.get(storeIndex);
		}
		// hope for cached
		synchronized (hotStore) {
			final StoreEntry found = hotStore.get(xin);
			if(null!=found) {
				found.lastAccess = time;
				return found.value;
			}
		}
		// do the work (while not holding locks)
		final int[] xcopy = Arrays.copyOf(xin,xin.length);
		final BigInteger value = f.eval(xcopy);
		final StoreEntry entry = new StoreEntry(xcopy,value,time);
		// write back result
		boolean considerReorg = false;
		synchronized (hotStore) {
			hotStore.put(xcopy,entry);
			considerReorg = hotStore.size()>=storeBound[storeIndex];
		}
		if(considerReorg) {
			possiblyReorg();
		}
		return value;
	}
	
	/**
	 * assumes no locks held when this is called
	 * expensive chech and re-org.  amortize this to cheap by using double per-sub store count guards.
	 * trying to be a amortized cheap approximate LRU
	 */
	private void possiblyReorg() {
		synchronized (this) { // there may be other operations working in parallel to this reorg, but no other reorg
			// estimate sizes and reset individual triggers
			long szEst = 0;
			for(int i=0;i<nStores;++i) {
				final Map<int[],StoreEntry> s = hotStores.get(i);
				synchronized (s) {
					final int szi = s.size();
					szEst += szi;
					storeBound[i] = 2*szi + initialSizeTargetI; // move trigger up to prevent a soon re-trigger
				}
			}
			if(szEst<=bigSize) {
				return;  // total size still in bounds, take no more action
			}
			// total size too large, shrink the stores, reset the triggers
			// use mean access time as a approximation for median access time
			long sumTimes = 0;
			long totEntries = 0;
			for(int i=0;i<nStores;++i) {
				final Map<int[],StoreEntry> s = hotStores.get(i);
				synchronized (s) {
					for(final StoreEntry v: s.values()) {
						sumTimes += v.lastAccess-baseTimeMS;
						totEntries += 1;
					}
				}
			}
			final long meanTime = (long)Math.ceil(sumTimes/(double)totEntries);
			// prune stores and reset triggers
			long newSize = 0;
			for(int i=0;i<nStores;++i) {
				final Map<int[],StoreEntry> s = hotStores.get(i);
				synchronized (s) {
					final StoreEntry[] vals = s.values().toArray(new StoreEntry[s.size()]);
					s.clear();
					for(final StoreEntry v: vals) {
						if(v.lastAccess-baseTimeMS>meanTime) {
							s.put(v.key,v);
						}
					}
					final int szi = s.size();
					newSize += szi;
					storeBound[i] = 2*szi + initialSizeTargetI; // move trigger up to prevent a soon re-trigger
				}
			}
			System.err.println("#\tinfo: reorg stores " + szEst + " -> " + newSize + "\t" + new Date());
		}
	}

	/**
	 * best effort, not atomic across stores; but still fairly expensive because of lock acquisition costs
	 * @return
	 */
	public long size() {
		long size = 0;
		for(int i=0;i<nStores;++i) {
			final Map<int[],StoreEntry> s = hotStores.get(i);
			synchronized (s) {
				size += s.size();
			}
		}
		return size;
	}
	
	/**
	 * best effort, not atomic across stores
	 */
	public void clear() {
		for(int i=0;i<nStores;++i) {
			final Map<int[],StoreEntry> s = hotStores.get(i);
			synchronized (s) {
				s.clear();
				storeBound[i] = initialSizeTargetI;
			}
		}
	}
}
