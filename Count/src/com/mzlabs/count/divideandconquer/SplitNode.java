package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;

import com.mzlabs.count.IntVec;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.ZeroOneCounter;

final class SplitNode implements NonNegativeIntegralCounter {
	private static final boolean debug = true;
	private final NonNegativeIntegralCounter leftSubSystem;
	private final NonNegativeIntegralCounter rightSubSystem;
	private final int[][] A;
	private final Map<IntVec,BigInteger> cache = new HashMap<IntVec,BigInteger>(1000);
	
	public SplitNode(final int[][] A,
			final NonNegativeIntegralCounter leftSubSystem,
			final NonNegativeIntegralCounter rightSubSystem) {
		this.A = A;
		this.leftSubSystem = leftSubSystem;
		this.rightSubSystem = rightSubSystem;
	}

	@Override
	public BigInteger countNonNegativeSolutions(final int[] b) {
		final IntVec bd1 = new IntVec(b);
		BigInteger count = cache.get(bd1);
		if(null==count) {
			final int m = b.length;
			final int[] b1 = new int[m];
			final int[] b2 = new int[m];
			count = BigInteger.ZERO;
			do {
				// add sub1*sub2 terms, but try to avoid calculating sub(i) if sub(1-i) is obviously zero
				final BigInteger sub1 = leftSubSystem.countNonNegativeSolutions(b1);
				if(sub1.compareTo(BigInteger.ZERO)>0) {
					for(int i=0;i<m;++i) {
						b2[i] = b[i] - b1[i];
					}
					final BigInteger sub2 = rightSubSystem.countNonNegativeSolutions(b2);
					if(sub2.compareTo(BigInteger.ZERO)>0) {
						count = count.add(sub1.multiply(sub2));
					}
				}
			} while(bd1.advanceLE(b1));
			cache.put(bd1,count);
		}
		if(debug) {
			final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(A,b);
			if(check.compareTo(count)!=0) {
				throw new IllegalStateException("got wrong answer");
			}
		}
		return count;
	}
	
	@Override
	public String toString() {
		return "split(" + leftSubSystem + "," + rightSubSystem + ")";
	}
}
