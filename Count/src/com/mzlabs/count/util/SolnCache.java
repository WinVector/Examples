package com.mzlabs.count.util;

import java.math.BigInteger;
import java.util.HashMap;

public final class SolnCache {
	private final int nsub = 1000;
	
	
	private static final class CI extends HashMap<IntVec,BigInteger> {
		private static final long serialVersionUID = 1L;
	};
	
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
	
	public BigInteger get(final IntVec key) {
		final CI cache = caches[subKey(key)];
		synchronized (cache) {
			return cache.get(key);
		}
	}

	public void put(final IntVec key, final BigInteger value) {
		final CI cache = caches[subKey(key)];
		synchronized (cache) {
			cache.put(key,value);
		}
	}
	
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
