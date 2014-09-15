package com.mzlabs.count.op.iter;

import com.mzlabs.count.op.Sequencer;

/**
 * step through all ordered sets of size m from 0,...,n-1
 * @author johnmount
 *
 */
public final class SetStepper implements Sequencer {
	public final int n; // number of items to choose from
	public final int m; // number of items to choose
	
	/**
	 * 
	 * @param m  number of items to choose (>0)
	 * @param n  number of items to choose from (>=m)
	 */
	public SetStepper(final int m, final int n) {
		this.m = m;
		this.n = n;
		if((m<=0)||(n<m)) {
			throw new IllegalArgumentException();
		}
	}
	
	@Override
	public int[] first() {
		final int[] x = new int[m];
		for(int i=0;i<m;++i) {
			x[i] = i;
		}
		return x;
	}
	
	@Override
	public boolean advance(final int[] x) {
		// find right-most item we can advance
		int i = m-1;
		while(i>=0) {
			if(x[i]<n-(m-i)) {
				final int nv = x[i]+1;
				for(int j=i;j<m;++j) {
					x[j] = nv + (j-i);
				}
				return true;
			}
			--i;
		}
		return false;
	}
}
