package com.mzlabs.count.op.impl;

import java.math.BigInteger;


/**
 * prefix tree on integer vectors (trying to cut down number of flyweight objects)
 * @author johnmount
 *
 */
public final class RecNode {
	public final int key;
	public BigInteger value = null;
	private int noccupied = 0;
	private RecNode[] map = null;
	
	public RecNode(final int key) {
		this.key = key;
	}
	
	/**
	 * 
	 * @param nk
	 * @param mp map with some nulls
	 * @return a null or matching key
	 */
	private static int findSlot(final int nk, final RecNode[] mp) {
		final int n = mp.length;
		int probe = nk%n;
		while(true) {
			final RecNode nd = mp[probe];
			if((null==nd)||(nd.key==nk)) {
				return probe;
			}
			probe = probe+1;
			if(probe>=n) {
				probe -= n;
			}
		}		
	}
	
	private RecNode get(final int nk) {
		if(null==map) {
			return null;
		}
		final int i = findSlot(nk,map);
		return map[i];
	}
	
	/**
	 * 
	 * @param x not null
	 */
	private void put(final RecNode x) {
		if(null==map) {
			map = new RecNode[10];
		}
		final int nk = x.key;
		final int i = findSlot(nk,map);
		if(null!=map[i]) {
			map[i] = x;
			return;
		}
		++noccupied;
		if(5*noccupied>=map.length) {
			// need to grow map
			final RecNode[] oldMap = map;
			map = new RecNode[5*oldMap.length];
			for(final RecNode nj: oldMap) {
				if(null!=nj) {
					final int j = findSlot(nj.key,map);
					map[j] = nj;
				}
				final int j = findSlot(nk,map);
				map[j] = x;
			}
		} else {
			map[i] = x;
		}
	}
	
	
	/**
	 * 
	 * @param x x.dim()>0
	 * @param newNode not null with key==x.get(x.dim()-1) (possible mutex locked)
	 * @return terminal node to hold value (newNode if there was allocation)
	 */
	private static RecNode lookupAlloc(RecNode nd, final int[] x, final RecNode newNode) {
		final int n = x.length;
		if(n<=0) {
			throw new IllegalArgumentException("empty x");
		}
		if(newNode.key!=x[n-1]) {
			throw new IllegalArgumentException("bad new key");
		}
		int firstPosn = 0;
		while(true) {
			final int key = x[firstPosn];
			RecNode sub = nd.get(key);
			if(firstPosn>=n-1) {
				// at terminal case
				if(null==sub) {
					sub = newNode;
					nd.put(sub);
				}
				return sub;
			} else {
				// interior case, recurse
				if(null==sub) {
					sub = new RecNode(key);
					nd.put(sub);
				}
				nd = sub;
				++firstPosn;
			}
		}
	}

	/**
	 * 
	 * @param x x.dim()>0
	 * @param newNode
	 * @return
	 */
	public RecNode lookupAlloc(final int[] x, final RecNode newNode) {
		return lookupAlloc(this,x,newNode);
	}
	
	public void clear() {
		map = null;
		noccupied = 0;
	}
	
	public long size() {
		long sz = 0;
		if(null!=value) {
			sz += 1;
		}
		if(null!=map) {
			for(final RecNode vi: map) {
				if(null!=vi) {
					sz += vi.size();
				}
			}
		}
		return sz;
	}
}