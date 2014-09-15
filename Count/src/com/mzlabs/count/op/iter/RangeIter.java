package com.mzlabs.count.op.iter;

import com.mzlabs.count.op.Sequencer;

/**
 * step from a to less than b
 * @author johnmount
 *
 */
public final class RangeIter implements Sequencer {
	public final int a;
	public final int b;
	

	/**
	 * 
	 * @param a
	 * @param b >=a
	 */
	public RangeIter(final int a, final int b) {
		this.a = a;
		this.b = b;
	}

	@Override
	public int[] first() {
		final int[] x = new int[1];
		x[0] = a;
		return x;
	}

	@Override
	public boolean advance(final int[] x) {
		x[0] += 1;
		return x[0]<b;
	}

}
