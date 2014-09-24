package com.mzlabs.count.op;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Map;
import java.util.TreeMap;

import com.mzlabs.count.util.IntVec;

public final class SolnCache {
	
	private final int nStores = 1377;
	private final ArrayList<Map<int[],BigInteger>> hotStores = new ArrayList<Map<int[],BigInteger>>(nStores);
	
	
	public SolnCache() {	
		for(int i=0;i<nStores;++i) {
			hotStores.add(new TreeMap<int[],BigInteger>(IntVec.IntComp));
		}
	}
	
	/**
	 * Look for a cached value of f(x), if none such create a record, block on the record and compute f(x) (so only one attempt to compute f(x))
	 * @param f
	 * @param x not null, x.length>0
	 * @return
	 */
	public BigInteger evalCached(final CachableCalculation f, final int[] xin) {
		// find the sub-store
		final Map<int[],BigInteger> hotStore;
		{
			int subi = Arrays.hashCode(xin)%nStores;
			if(subi<0) {
				subi += nStores;
			}
			hotStore = hotStores.get(subi);
		}
		// hope for cached
		synchronized (hotStore) {
			final BigInteger found = hotStore.get(xin);
			if(null!=found) {
				return found;
			}
		}
		// do the work (while not holding locks)
		final int[] xcopy = Arrays.copyOf(xin,xin.length);
		final BigInteger value = f.eval(xcopy);
		// write back result
		synchronized (hotStore) {
			hotStore.put(xcopy,value);
		}
		return value;
	}
	
	/**
	 * best effort, not atomic across stores
	 * @return
	 */
	public long size() {
		long size = 0;
		for(final Map<int[],BigInteger> s: hotStores) {
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
		for(final Map<int[],BigInteger> s: hotStores) {
			synchronized (s) {
				s.clear();
			}
		}
	}
}
