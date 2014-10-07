package com.mzlabs.count.op;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Map;
import java.util.TreeMap;

import com.mzlabs.count.util.IntVec;

public final class SolnCache {
	private final int storeMask = 0x07fff; // 2^k-1
	
	private static final class SolnEntry {
		public BigInteger value = null; 
	}
	
	private final ArrayList<Map<int[],SolnEntry>> hotStores = new ArrayList<Map<int[],SolnEntry>>(storeMask+1);  // sub-stores (to shallow trees), also sync on these
	

	public SolnCache() {
		for(int i=0;i<=storeMask;++i) {
			hotStores.add(new TreeMap<int[],SolnEntry>(IntVec.IntComp));
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
		final SolnEntry foundValueHolder;
		final SolnEntry newValueHolder = new SolnEntry();
		synchronized (newValueHolder) {
			// find the sub-store
			final int storeIndex = Arrays.hashCode(xin)&storeMask;
			final Map<int[],SolnEntry> hotStore = hotStores.get(storeIndex);
			// hope for cached
			synchronized (hotStore) {
				foundValueHolder = hotStore.get(xin);
				if(null==foundValueHolder) {
					final int[] xcopy = Arrays.copyOf(xin,xin.length);
					hotStore.put(xcopy,newValueHolder); // newValueHolder now visible to other threads, don't release it's lock before calculating
				}
			}
			if(null==foundValueHolder) {
				// do the work (while not holding outer locks, but while holding newValueHolder lock)
				newValueHolder.value = f.eval(xin);
				return newValueHolder.value;
			}
		}
		// foundValueHolder not null here
		synchronized (foundValueHolder) {
			return foundValueHolder.value;
		}
	}
	

	/**
	 * best effort, not atomic across stores; but still fairly expensive because of lock acquisition costs
	 * @return
	 */
	public long size() {
		long size = 0;
		for(int i=0;i<=storeMask;++i) {
			final Map<int[],SolnEntry> s = hotStores.get(i);
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
		for(int i=0;i<=storeMask;++i) {
			final Map<int[],SolnEntry> s = hotStores.get(i);
			synchronized (s) {
				s.clear();
			}
		}
	}
}
