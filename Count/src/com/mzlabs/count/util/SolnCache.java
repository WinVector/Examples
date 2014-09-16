package com.mzlabs.count.util;

import java.math.BigInteger;
import java.util.HashMap;

public final class SolnCache {
	private final int nsub = 1000;
	
	
	private static final class CI extends HashMap<IntVec,BHolder> {
		private static final long serialVersionUID = 1L;
	};
	
	private static final class BHolder {
		public BigInteger value = null;
	}
	
	private final CI[] caches = new CI[nsub];  // split caches to cut down on contention and improve hash slightly 
	
	public SolnCache() {
		for(int i=0;i<nsub;++i) {
			caches[i] = new CI();
		}
	}
	
	private int subKey(final IntVec key) {
		final int n = key.dim();
		int r = 0;
		for(int i=0;i<n;++i) {
			r = r*73 + key.get(i);
		}
		r = r%nsub;
		if(r<0) {
			r += nsub;
		}
		return r;
	}
	
	
//	private static final Object syncObj = new Object();
//	public static long totalEvals = 0;
	
	/**
	 * Look for a cached value of f(x), if none such create a record, block on the record and compute f(x) (so only one attempt to compute f(x))
	 * @param f
	 * @param x
	 * @return
	 */
	public BigInteger evalCached(final IntVecFn f, final IntVec x) {
		final BHolder cached;
		{
			final CI cache = caches[subKey(x)];
			final BHolder newHolder = new BHolder();
			synchronized (newHolder) {
				synchronized(cache) {
					cached = cache.get(x);
					if(null==cached) {
						cache.put(x,newHolder);
					}
				}
				if(null==cached) {
//					synchronized (syncObj) {
//						totalEvals += 1;
//					}
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
	
	
//	private BigInteger evalCachedSimple(final IntVecFn f, final IntVec x) {
//		final CI cache = caches[subKey(x)];
//		synchronized (cache) {
//			final BHolder cached = cache.get(x);
//			if(null!=cached) {
//				return cached.value;
//			}
//		}
//		final BHolder newHolder = new BHolder();
//		synchronized (syncObj) {
//			totalEvals += 1;
//		}
//		newHolder.value = f.eval(x);
//		synchronized (cache) {
//			cache.put(x,newHolder);
//		}
//		return newHolder.value;
//	}
	
	
	public int size() {
		int sz = 0;
		for(final CI ci: caches) {
			synchronized(ci) {
				sz += ci.size();
			}
		}
		return sz;
	}

	public void clear() {
		for(final CI ci: caches) {
			synchronized(ci) {
				ci.clear();
			}
		}
	}
}
