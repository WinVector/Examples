package com.mzlabs.count.op;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Map;
import java.util.TreeMap;

import com.mzlabs.count.util.IntVec;

public final class SolnCache {
	private final int nsubs = 10000;
	
	/**
	 * gives as per-problem lock to hold
	 * @author johnmount
	 *
	 */
	private static final class BHolder {
		public BigInteger value = null;
	}
	
	private final ArrayList<Map<IntVec,BHolder>> hashCodeToMap = new ArrayList<Map<IntVec,BHolder>>(nsubs);

	public SolnCache() {
		for(int i=0;i<nsubs;++i) {
			hashCodeToMap.add(new TreeMap<IntVec,BHolder>());
		}
	}
	
	
	/**
	 * Look for a cached value of f(x), if none such create a record, block on the record and compute f(x) (so only one attempt to compute f(x))
	 * @param f
	 * @param x
	 * @return
	 */
	public BigInteger evalCached(final IntVecFn f, final IntVec x) {
		final BHolder cached;
		{
			int kv = x.hashCode()%nsubs;
			if(kv<0) {
				kv += nsubs;
			}
			final Map<IntVec, BHolder> cache = hashCodeToMap.get(kv);
			final BHolder newHolder = new BHolder();
			synchronized (newHolder) {
				synchronized(cache) {
					cached = cache.get(x);
					if(null==cached) {
						cache.put(x,newHolder);
					}
				}
				if(null==cached) {
					newHolder.value = f.eval(x);
					return newHolder.value;
				}
			}
		}
		// cached is not null here
		synchronized (cached) {
			// if we can obtain the lock then cached.value is not null (as it is set before the lock is released)
			return cached.value;
		}
	}
		
	
	/** 
	 * advisory size, not atomic accross sub-caches
	 * @return
	 */
	public int size() {
		int sz = 0;
		for(final Map<IntVec, BHolder> ci: hashCodeToMap) {
			synchronized(ci) {
				sz += ci.size();
			}
		}
		return sz;
	}

	/**
	 * good effort clear, not atomic accross sub-caches
	 */
	public void clear() {
		for(final Map<IntVec, BHolder> ci: hashCodeToMap) {
			synchronized(ci) {
				ci.clear();
			}
		}
	}
}
