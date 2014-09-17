package com.mzlabs.count.op;

import java.math.BigInteger;
import java.util.Arrays;

import com.mzlabs.count.op.impl.RecNode;

public final class SolnCache {
	private final int nsub = 100;
	private final RecNode[] stores;
	
	public SolnCache() {
		stores = new RecNode[nsub];
		for(int i=0;i<nsub;++i) {
			stores[i] = new RecNode(-1);
		}
	}
	
	/**
	 * Look for a cached value of f(x), if none such create a record, block on the record and compute f(x) (so only one attempt to compute f(x))
	 * @param f
	 * @param x not null, x.length>0
	 * @return
	 */
	public BigInteger evalCached(final CachableCalculation f, final int[] x) {
		int subi = Arrays.hashCode(x)%nsub;
		if(subi<0) {
			subi += nsub;
		}
		final RecNode store = stores[subi];
		final RecNode newHolder = new RecNode(x[x.length-1]);
		final RecNode cached;
		synchronized (newHolder) {
			synchronized(store) {
				cached = store.lookupAlloc(x,newHolder);
			}
			// newHolder now potentially visible to other threads (as it is in the cache and we released the mutex)
			// keep newHolder mutex so we can fill in value before anybody else looks
			// if cached.value==null it is because we allocated and cached==newHolder
			if(null==cached.value) {
				cached.value = f.eval(x);
				return cached.value;
			}
		}
		// cached is not null here
		synchronized (cached) {
			// if we can obtain the lock then cached.value is not null (as it is set before the lock is released)
			return cached.value;
		}
	}
		
	
	/**
	 * good effort clear, not atomic across sub-caches
	 * @return
	 */
	public long size() {
		long sz = 0;
		for(final RecNode store: stores) {
			synchronized (store) {
				sz += store.size();
			}
		}
		return sz;
	}

	/**
	 * good effort clear, not atomic across sub-caches
	 */
	public void clear() {
		for(final RecNode store: stores) {
			synchronized (store) {
				store.clear();
			}
		}
	}
}
