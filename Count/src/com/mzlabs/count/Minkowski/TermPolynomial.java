package com.mzlabs.count.Minkowski;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;

import com.mzlabs.count.util.BigRat;
import com.mzlabs.count.util.IntVec;

public final class TermPolynomial implements RatFun {
	private final Map<IntVec,BigRat> terms = new HashMap<IntVec,BigRat>();
	
	@Override
	public final BigRat eval(final int[] x) {
		final int n = x.length;
		BigRat sum = BigRat.ZERO;
		for(final Map.Entry<IntVec,BigRat> me: terms.entrySet()) {
			final IntVec term = me.getKey();
			final BigRat coef = me.getValue();
			BigInteger eTerm = BigInteger.ONE;
			for(int i=0;i<n;++i) {
				final BigInteger ti = BigInteger.valueOf(x[i]).pow(term.get(i));
				eTerm = eTerm.multiply(ti);
			}
			sum = sum.add(coef.multiply(BigRat.valueOf(eTerm)));
		}
		return sum;
	}

}
