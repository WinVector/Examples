package com.mzlabs.count.op.impl;

import java.math.BigInteger;

import com.mzlabs.count.op.IntFunc;
import com.mzlabs.count.op.Reducer;
import com.mzlabs.count.op.Sequencer;

public final class SimpleSum implements Reducer {

	@Override
	public BigInteger reduce(final IntFunc f, final Sequencer s) {
		final int[] x = s.first();
		BigInteger sum = BigInteger.ZERO;
		if(null!=x) {
			do {
				final BigInteger term = f.f(x);
				if(term.compareTo(BigInteger.ZERO)!=0) {
					sum = sum.add(term);
				}
			} while(s.advance(x));
		}
		return sum;
	}

}
