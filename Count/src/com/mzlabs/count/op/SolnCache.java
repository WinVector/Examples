package com.mzlabs.count.op;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Map;
import java.util.TreeMap;

import com.mzlabs.count.util.IntVec;

/**
 * assuming any recursive calls are on strictly smaller totals (so we can't have circular locks)
 * @author jmount
 *
 */
public final class SolnCache {
	private final int maxSum = 2*10*100;
	private final int storeMask = 0x07f; // 2^k-1
	

	private final ArrayList<ArrayList<Map<int[],BigInteger>>> hotStores = 
			new ArrayList<ArrayList<Map<int[],BigInteger>>>(storeMask+1);
	

	public SolnCache() {
		for(int i=0;i<=storeMask;++i) {
			final ArrayList<Map<int[],BigInteger>> ai = new ArrayList<Map<int[],BigInteger>>(maxSum+1);
			for(int j=0;j<=maxSum;++j) {
				ai.add(new TreeMap<int[],BigInteger>(IntVec.IntComp));
			}
			hotStores.add(ai);
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
		final int storeIndex = Arrays.hashCode(xin)&storeMask;
		int total = 0;
		for(final int xi: xin) {
			total += xi;
		}
		final Map<int[],BigInteger> hotStore = hotStores.get(storeIndex).get(total);
		synchronized (hotStore) {
			{ 		// hope for cached
				final BigInteger foundValue = hotStore.get(xin);
				if(null!=foundValue) {
					return foundValue;
				}
			}
			// do the work (while holding locks)
			final BigInteger newValue = f.eval(xin);
			final int[] xcopy = Arrays.copyOf(xin,xin.length);
			hotStore.put(xcopy,newValue);
			return newValue;
		}
	}
	

	/**
	 * best effort, not atomic across stores; but still fairly expensive because of lock acquisition costs
	 * @return
	 */
	public long size() {
		long size = 0;
		for(final ArrayList<Map<int[], BigInteger>> ai: hotStores) {
			for(final Map<int[], BigInteger> aij: ai) {
				synchronized(aij) {
					size += aij.size();
				}
			}
		}
		return size;
	}
	
	/**
	 * best effort, not atomic across stores
	 */
	public void clear() {
		for(final ArrayList<Map<int[], BigInteger>> ai: hotStores) {
			for(final Map<int[], BigInteger> aij: ai) {
				synchronized(aij) {
					aij.clear();
				}
			}
		}
	}
}
