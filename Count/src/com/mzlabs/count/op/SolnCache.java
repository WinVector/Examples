package com.mzlabs.count.op;

import java.math.BigInteger;

import com.mzlabs.count.op.impl.RecNode;
import com.mzlabs.count.util.IntVec;

public final class SolnCache {
	private final RecNode store = new RecNode(-1);
	
	/**
	 * Look for a cached value of f(x), if none such create a record, block on the record and compute f(x) (so only one attempt to compute f(x))
	 * @param f
	 * @param x
	 * @return
	 */
	public BigInteger evalCached(final IntVecFn f, final IntVec x) {
		final RecNode cached;
		final RecNode newHolder = new RecNode(x.get(x.dim()-1));
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
		
	
	public long size() {
		synchronized (store) {
			return store.size();
		}
	}

	/**
	 * good effort clear, not atomic accross sub-caches
	 */
	public void clear() {
		synchronized (store) {
			store.clear();
		}
	}
}
