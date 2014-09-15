package com.mzlabs.count.op.iter;

import com.mzlabs.count.op.Sequencer;

/**
 * advance a non-negative through all non-negative combinations less than bound, (starting at all zeros)
 * @param bvec
 * @return true if we haven't wrapped around to all zeros
 */
public final class SeqLT implements Sequencer {
	private final int dim;
	private final int bound;
	
	public SeqLT(final int dim, final int bound) {
		this.dim = dim;
		this.bound = bound;
	}

	@Override
	public int[] first() {
		return new int[dim];
	}

	@Override
	public boolean advance(final int[] x) {
		final int n = x.length;
		final int boundMinus1 = bound-1;
		// look for right-most advancable item
		for(int i=n-1;i>=0;--i) {
			if(x[i]<boundMinus1) {
				x[i] += 1;
				return true;
			}
			x[i] = 0;
		}
		return false;
	}
}
