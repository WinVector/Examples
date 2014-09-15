package com.mzlabs.count.op.iter;

import com.mzlabs.count.op.Sequencer;
import com.mzlabs.count.util.IntVec;

/**
 * advance a non-negative through all non-negative combinations less than equal to bound, (starting at all zeros)
 * @param bvec
 * @return true if we haven't wrapped around to all zeros
 */
public final class SeqLE implements Sequencer {
	private final IntVec bound;
	private final int vecDim;
	private final int iterDim;
	
	public SeqLE(final IntVec x, final int vecDim, final int iterDim) {
		this.bound = x;
		this.vecDim = vecDim;
		this.iterDim = iterDim;
	}
	
	public SeqLE(final IntVec x) {
		this(x,x.dim(),x.dim());
	}

	@Override
	public int[] first() {
		return new int[vecDim];
	}

	@Override
	public boolean advance(final int[] x) {
		// look for right-most incrementable item
		final int n = iterDim;
		for(int i=n-1;i>=0;--i) {
			if(x[i]<bound.get(i)) {
				x[i] += 1;
				return true;
			}
			x[i] = 0;
		}
		return false;
	}
}
