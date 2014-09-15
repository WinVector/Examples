package com.mzlabs.count.op.iter;

import com.mzlabs.count.op.Sequencer;

/**
 * step over all x such that x.length==dim, x>=0 and sum(x)<=degree
 * @author johnmount
 *
 */
public final class SumStepper implements Sequencer {
	public final int dim;
	public final int degree;
	
	public SumStepper(final int dim, final int degree) {
		this.degree = degree;
		this.dim = dim;
	}

	
	@Override
	public int[] first() {
		return new int[dim];
	}

	@Override
	public boolean advance(final int[] x) {
		// find right-most advancible place
		int sum = 0;
		for(final int xi: x) {
			sum += xi;
		}
		final int n = x.length;
		int i = n-1;
		do {
			final int xi = x[i];
			if(sum+1<=degree) {
				x[i] = xi + 1;
				return true;
			}
			sum -= xi;
			x[i] = 0;
			--i;
		} while(i>=0);
		return false;
	}
}
